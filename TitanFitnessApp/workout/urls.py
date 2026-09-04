from django.urls import path

from workout import views


urlpatterns = [
    path('', views.workout_view, name='workout'),
    path('history/', views.workout_history_view, name='workout_history'),
    path('plans/', views.workout_plan_list_view, name='workout_plan_list'),
    path('plans/create/', views.create_workout_plan_view, name='create_workout_plan'),
    path(
        'plans/<int:workout_id>/delete/',
        views.delete_workout_plan_view,
        name='delete_workout_plan',
    ),
    path(
        'plans/<int:workout_id>/',
        views.workout_plan_detail_view,
        name='workout_plan_detail',
    ),
    path(
        'plans/<int:workout_id>/exercises/add/',
        views.add_exercise_to_workout_plan_view,
        name='add_exercise_to_workout_plan',
    ),
    path(
        'plans/<int:workout_id>/exercises/<int:workout_exercise_id>/sets/add/',
        views.add_planned_set_to_workout_exercise_view,
        name='add_planned_set_to_workout_exercise',
    ),
    path(
        'plans/<int:workout_id>/exercises/<int:workout_exercise_id>/remove/',
        views.remove_exercise_from_workout_plan_view,
        name='remove_exercise_from_workout_plan',
    ),
    path(
        'plans/<int:workout_id>/exercises/<int:workout_exercise_id>/sets/<int:planned_set_id>/remove/',
        views.remove_planned_set_view,
        name='remove_planned_set',
    ),
    path(
        'plans/<int:workout_id>/start/',
        views.start_workout_plan_view,
        name='start_workout_plan',
    ),
    path('exercises/', views.exercise_list_view, name='exercise_list'),
    path('exercises/create/', views.create_personal_exercise_view, name='create_personal_exercise'),
    path(
        'exercises/<int:exercise_id>/archive/',
        views.archive_personal_exercise_view,
        name='archive_personal_exercise',
    ),
    path('sessions/start/', views.start_workout_session_view, name='start_workout_session'),
    path('sessions/<int:session_id>/', views.workout_session_detail_view, name='workout_session_detail'),
    path('sessions/<int:session_id>/exercises/add/', views.add_exercise_to_session_view, name='add_exercise_to_session'),
    path(
        'sessions/<int:session_id>/exercises/<int:session_exercise_id>/sets/add/',
        views.add_set_to_session_exercise_view,
        name='add_set_to_session_exercise',
    ),
    path(
        'sessions/<int:session_id>/exercises/<int:session_exercise_id>/sets/<int:set_id>/remove/',
        views.remove_set_from_session_exercise_view,
        name='remove_set_from_session_exercise',
    ),
    path(
        'sessions/<int:session_id>/exercises/<int:session_exercise_id>/sets/<int:set_id>/complete/',
        views.complete_workout_set_view,
        name='complete_workout_set',
    ),
    path(
        'sessions/<int:session_id>/exercises/<int:session_exercise_id>/remove/',
        views.remove_exercise_from_session_view,
        name='remove_exercise_from_session',
    ),
    path(
        'sessions/<int:session_id>/finish/',
        views.finish_workout_session_view,
        name='finish_workout_session',
    ),
]
