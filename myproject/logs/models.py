from django.db import models

class RequestLog(models.Model):
    user_id = models.CharField(max_length=100)
    command = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    response = models.TextField()

    def __str__(self):
        return f'{self.user_id} - {self.command} - {self.timestamp}'

class UserSetting(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    preferred_city = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.user_id} - {self.preferred_city}'
