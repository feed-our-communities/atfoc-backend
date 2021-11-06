from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.UserProfile)
admin.site.register(models.Organization)
admin.site.register(models.JoinRequest)
admin.site.register(models.OrgApplication)
