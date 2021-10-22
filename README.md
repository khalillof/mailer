app features:
    this app correspond to the requirements for cybersecurity specilization capstone on coursera by maryland university

    - user registration pages and login with password reset functionality using text based security questions 
    - login in using either username or email
    - send receive reply and archive messages 
    - send messages using either username or email
    - send messages to multiple recipients by adding comma separated list of registered usernames or emails or combination of usernames and emails
    - html5 form validations plus some server side form validations
    - read messages shows in light color and unread with dark color
    - important data encrpted on the database
    - dump database should print out the database on the browser

setup:
    This app was tested on ubuntu and require python3, pip, Django 3.2.8 and django_cryptography 1.0

    FIRST TIME USAGE RUN command (sudo make build) or  commands (sudo make all)'
    After the first time build, whenever you want to run the app js run (sudo make run) or (sudo make browser) to run on your default browser'

USAGE :
    - when you run the app login page will be displayed
    - on login page you can either use on of the above users to login or click on regisetr buttun to register
        fill in theregistration details then login
    - Inbox page will be displayed listing all messages with navigations to other pages such as inbox - compose - sent - archive dump database and logout
    - you can press compose buttun to send message 
    - right after seding the message sent messages inbox will show up 
    - the rest of the app is self explanatory 

