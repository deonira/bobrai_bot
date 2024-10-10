from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class RequestLog(models.Model):
    user_id = models.CharField(max_length=100)
    command = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    response = models.TextField()

    def __str__(self):
        return f'{self.user_id} - {self.command} - {self.response} - {self.timestamp}'

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.user_id} - {self.preferred_city}'
