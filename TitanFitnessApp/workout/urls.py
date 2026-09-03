from django.urls import path

from workout import views


urlpatterns = [
    path('', views.workout_view, name='workout'),
    path('exercises/', views.exercise_list_view, name='exercise_list'),
    path('exercises/create/', views.create_personal_exercise_view, name='create_personal_exercise'),
]
