import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, FileResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Email
from .dumper import db_dump
import re

def index(request):

    # Authenticated users view their inbox
    if request.user.is_authenticated:
        return render(request, "mail/index.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))

@login_required
def compose(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    emails = [email.strip() for email in data.get("recipients").split(",")]
    if emails == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    # Convert email addresses to users
    recipients = []
    for email in emails:
        user = getUserNameOrEmail(email)
          
        if user is not None:
            recipients.append(user)
        else:
            return JsonResponse({
                "error": f"User with username or email (( {email} )) does not exist."
            }, status=400)

    # Get contents of email
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        email = Email(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    return JsonResponse({"message": "Email sent successfully."}, status=201)


@login_required
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == "archive":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return emails in reverse chronologial order
    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serialize() for email in emails], safe=False)


@login_required
def email(request, email_id):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
        if data.get("archived") is not None:
            email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def login_view(request):
    if request.method == "POST":
        try:
            attempts = request.session.get('logging_attempts')
            if attempts:
                request.session['logging_attempts'] += attempts
            else:
                request.session['logging_attempts'] = 1
        except KeyError as e:
            print(e)
            pass

        # Attempt to sign user in
        username_email = request.POST["username_email"]
        password = request.POST["password"]

        _user = getUserNameOrEmail(username_email) 

        # Check if authentication successful
        if _user is not None:
            user = authenticate(request=request, username=_user.username, password=password)
            login(request, user)
            if attempts:
                del request.session['logging_attempts']
            return HttpResponseRedirect(reverse("index"))
        else:
            if attempts and attempts <= 2:
                return render(request, "mail/login.html", {
                "message": "one more Invalid attempt and your account will be locked try to reset password"
                })
            elif attempts and attempts >= 3:
                return render(request, "mail/login.html", {
                "message": "your account is locked try to reset password"
                })
            ##
            return render(request, "mail/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "mail/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        email = request.POST["email"].lower()

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        security_question = request.POST["security_question"].lower()
        question_answer = request.POST["question_answer"].lower()

        vals = [
        __validate('username',username),
        __validate('email',email),
        __validate('password',password),
        __validate('security_question',security_question),
        __validate('question_answer',question_answer)
        ]
        vals = [v for v in vals if v]

        if vals and isinstance(vals[0], str):
            return render(request, "mail/register.html", {
                "message": str(vals)
            })
        elif password != confirmation:
            return render(request, "mail/register.html", {
                "message": "Passwords must match.",
                "username":username,
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.security_question = security_question
            user.question_answer = question_answer
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "mail/register.html", {
                "message": "Emailaddress or username  already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mail/register.html")


def password_reset(request):
    if request.method == "GET":
        return render(request, "mail/password_reset.html")
    elif request.method == "POST":
        username_email = request.POST["username_email"].lower()
        user = getUserNameOrEmail(username_email)
        if user is None:
            return render(request, "mail/password_reset.html", {
                "message": "Invalid email or username"
            })
        else:
            return render(request, "mail/security_question.html", {
                "username":user.username,
                "security_question": user.security_question
            })
    else:
        return render(request, "mail/password_reset.html", {
                "message": "HTTP GET or POST REQUIRD"
            }, status=400)

def security_guestions(request):
    if request.method == "POST":
        username = request.POST["username"]
        security_question = request.POST["security_question"].lower()
        question_answer = request.POST["question_answer"].lower()

        user = get_user(username=username)
        if user is None:
            return render(request, "mail/password_reset.html", {
                "message": "Invalid email and/or username"
            })
        else:
            if security_question == user.security_question and question_answer == user.question_answer:
                return render(request, "mail/password_reset_confirm.html", {
                "username":user.username,
            })
            else:
                return render(request, "mail/security_question.html", {
                "message": "answer to the security question doesn't match",
                "username":user.username,
                "security_question": user.security_question
            })

    else:
        render(request, "mail/password_reset.html", {
                "message": "REQUIR HTTP POST"
            }, status=400)

def password_reset_confirm(request):
    if request.method == "POST":
        username = request.POST["username"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        val = __validate('password',password)           

        if isinstance(val, str):
                return render(request, "mail/password_reset_confirm.html", {
                "message": val,
                "username":username,
                })
        if password != confirmation:
            return render(request, "mail/password_reset_confirm.html", {
                "message": "Passwords must match.",
                "username":username,
            })
        user = get_user(username=username)
        if user is None:
            return render(request, "mail/password_reset.html", {
                "message": "Invalid email and/or username"
            })
        else:
            user.set_password(password)
            user.save()
            return render(request, "mail/password_reset_done.html")
    else:
        return render(request, "mail/password_reset.html", {
                "message": "HTTP GET or POST REQUIRD"
            }, status=400)


@login_required
def dumpdb(request):
    if request.method == "GET":
        dbFile= db_dump()
        response =FileResponse(dbFile)
        return response
    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


def get_user(user_id:int=None,username:str=None, email:str=None):
        try:
            if user_id:
                return User.objects.get(pk=user_id)
            elif username:
                return User.objects.get(username=username)
            elif email:
                return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

def getUserNameOrEmail(content):
    if '@' in content:
        return get_user(email=content)
    else:
        return get_user(username=content)

 ##################################################
    
def __validate(name:str, feild:str):
    if name == 'email':
        if not __email_check(feild):
            return 'email feild is not valid'
            

    if name == 'username':
        if len(feild) < 3 or len(feild) > 15:
            return 'username should be at least 3 or less than 30 chars'
            
    if name == 'password':
        test = __password_check(feild)
        if isinstance(test,str):            
            return  test
            
    if name == 'security_question' or name == 'question_answer':
        if len(feild) < 3 or len(feild) > 30:
            return 'security questions and answers should be at least 3 or less than 30 chars'
            

def __email_check(email:str):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    matches = re.search(regex, email)
    return True if matches else False

def __password_check(passwd):

    SpecialSym =['$', '@', '#', '%']
    val = True
    msg = None

    if len(passwd) < 6:
        msg ='length should be at least 6'
        val = False
    
    if len(passwd) > 20:
        msg='length should be not be greater than 8'
        val = False

    if not any(char.isdigit() for char in passwd):
        msg ='Password should have at least one numeral'
        val = False
    if not any(char.isupper() for char in passwd):
        msg = 'Password should have at least one uppercase letter'
        val = False
    if not any(char.islower() for char in passwd):
        msg='Password should have at least one lowercase letter'
        val = False
    if not any(char in SpecialSym for char in passwd):
        msg='Password should have at least one of the symbols $@#'
        val = False
    if val:
        return val
    else:
        return msg