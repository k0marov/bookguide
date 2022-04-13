from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    friends = models.ManyToManyField("self")

class Invite(models.Model):
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="invites_to_me")
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="invites_from_me")

class Book(models.Model):
    title = models.CharField(max_length=100)
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

class BookDate(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title + ' @' + self.user.username
