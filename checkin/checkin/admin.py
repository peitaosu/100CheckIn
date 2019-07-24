from django.contrib import admin
from .models import User, Event, User_Event

admin.site.register(User)
admin.site.register(Event)
admin.site.register(User_Event)