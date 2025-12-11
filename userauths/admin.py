from django.contrib import admin

# Register your models here.
from django.contrib import admin
from userauths import models as userauths_models

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'full_name', 'balance', 'mobile', 'verified']

# class ComplainMessageAdmin(admin.ModelAdmin):
#     list_display = ['full_name', 'email', 'subject', 'date']

admin.site.register(userauths_models.User, UserAdmin)
# admin.site.register(userauths_models.Profile, ProfileAdmin)
# admin.site.register(userauths_models.Complain, ComplainMessageAdmin)
    