from django.urls import path

from workout import views


urlpatterns = [
    path('', views.workout_view, name='workout'),
    path('exercises/', views.exercise_list_view, name='exercise_list'),
    path('exercises/create/', views.create_personal_exercise_view, name='create_personal_exercise'),
    path('sessions/start/', views.start_workout_session_view, name='start_workout_session'),
    path('sessions/<int:session_id>/', views.workout_session_detail_view, name='workout_session_detail'),
    path('sessions/<int:session_id>/exercises/add/', views.add_exercise_to_session_view, name='add_exercise_to_session'),
    path(
        'sessions/<int:session_id>/exercises/<int:session_exercise_id>/sets/add/',
        views.add_set_to_session_exercise_view,
        name='add_set_to_session_exercise',
    ),
    path(
        'sessions/<int:session_id>/finish/',
        views.finish_workout_session_view,
        name='finish_workout_session',
    ),
]
