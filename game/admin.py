from django.contrib import admin

# Register your models here.
from .models import Card, Game,Hand

admin.site.register(Game)
admin.site.register(Hand)
admin.site.register(Card)