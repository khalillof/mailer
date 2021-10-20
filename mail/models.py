from django.contrib.auth.models import AbstractUser
from django.db import models
from django_cryptography.fields import encrypt
from django.utils.translation import gettext_lazy as _
class User(AbstractUser):
    #first_name = encrypt(models.CharField(_('first name'), max_length=150, blank=True))
    #last_name = encrypt(models.CharField(_('last name'), max_length=150, blank=True))
    #email = encrypt(models.EmailField(_('email address'), blank=True))
    security_question = encrypt(models.CharField(max_length=50))
    question_answer = encrypt(models.CharField(max_length=50))


class Email(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField("User", related_name="emails_received")
    subject = encrypt(models.CharField(max_length=255))
    body = encrypt(models.TextField(blank=True))
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False) 

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "recipients": [user.username for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%A %d %B %Y %I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }
