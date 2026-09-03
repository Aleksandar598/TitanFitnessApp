from django.contrib import admin
from nutrition.models import Food, FoodLog


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'quantity', 'quantity_type', 'calories')
    search_fields = ('name', 'user__username')
    list_filter = ('quantity_type',)


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'user', 'quantity', 'quantity_type', 'calories', 'date')
    list_filter = ('date',)
