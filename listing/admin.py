from django.contrib import admin
from listing import models

# Register your models here.
admin.site.register(models.Donation)
admin.site.register(models.DonationTraits)
admin.site.register(models.Request)
admin.site.register(models.RequestTraits)