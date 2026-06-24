from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ['email','full_name','role','is_verified','is_active','date_joined']
    list_filter    = ['role','is_verified','is_active','country']
    search_fields  = ['email','first_name','last_name','phone']
    ordering       = ['-date_joined']
    fieldsets = (
        (None,            {'fields': ('email','password')}),
        ('personal info', {'fields': ('first_name','last_name','phone','avatar','country','language')}),
        ('role & status', {'fields': ('role','is_verified','is_active','is_staff','is_superuser')}),
        ('permissions',   {'fields': ('groups','user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email','first_name','last_name','role','password1','password2'),
        }),
    )
