"""
URL configuration for TitanFitnessApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from dashboard.views import dashboard_view
from nutrition import views as nutrition_views
from nutrition.views import (
    create_food_log_view,
    create_food_view,
    food_log_history_view,
    nutrition_view,
    remove_today_food_log_view,
    today_food_log_view,
)
from users.views import register_view, unregistered_menu_view, login_view, logout_view, settings_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('workouts/', include('workout.urls')),
    path('community/', include('community.urls')),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('', unregistered_menu_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('settings/', settings_view, name='settings'),
    path('logout/', logout_view, name='logout'),
    path('create_food/', create_food_view, name='create_food'),
    path('food-log/add/', create_food_log_view, name='create_food_log'),
    path('food-log/today/', today_food_log_view, name='today_food_log'),
    path('food-log/today/<int:log_id>/remove/', remove_today_food_log_view, name='remove_today_food_log'),
    path('food-log/history/', food_log_history_view, name='food_log_history'),
    path('nutrition/', nutrition_view, name='nutrition'),
    path("saved-foods/", nutrition_views.saved_view_foods, name="saved_foods"),
    path("saved-foods/<int:food_id>/edit/", nutrition_views.edit_saved_food_view, name="edit_saved_food"),
    path("saved-foods/remove/<int:food_id>/", nutrition_views.remove_saved_food, name="remove_saved_food"),
]
