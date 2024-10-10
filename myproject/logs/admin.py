from django.contrib import admin
from .models import RequestLog, UserSettings
admin.site.register(RequestLog)
admin.site.register(UserSettings)
# Register your models here.
