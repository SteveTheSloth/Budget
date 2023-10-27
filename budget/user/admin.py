from django.contrib import admin

from .models import UserGroup, MyUser

admin.site.register(UserGroup)
admin.site.register(MyUser)
