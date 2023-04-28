from django.contrib import admin

# Register your models here.
from .models import Balance, Profile

admin.site.register(Balance)
admin.site.register(Profile)