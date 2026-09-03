from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Fitness profile', {'fields': ('birth_date', 'height', 'gender', 'current_weight', 'target_weight', 'fitness_goal', 'activity_level')}),
    )
    list_display = ('username', 'email', 'current_weight', 'fitness_goal', 'is_staff')
