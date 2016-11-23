from django.contrib import admin

from app import models

admin.site.register(models.Team)
admin.site.register(models.Student)
admin.site.register(models.School)
