from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from workout.forms.ExerciseForm import ExerciseForm
from workout.forms.WorkoutSessionExerciseForm import WorkoutSessionExerciseForm
from workout.models import Exercise, WorkoutSession, WorkoutSessionExercise


@login_required
def workout_view(request):
    active_session = WorkoutSession.objects.filter(
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    ).first()
    return render(request, 'workout/workout.html', {
        'active_session': active_session,
    })


@login_required
def exercise_list_view(request):
    exercises = Exercise.objects.filter(
        Q(created_by__isnull=True) | Q(created_by=request.user),
    )
    return render(request, 'workout/exercises.html', {
        'available_exercises': exercises,
    })


@login_required
def create_personal_exercise_view(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST, user=request.user)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.save()
            return redirect('exercise_list')
    else:
        form = ExerciseForm(user=request.user)

    return render(request, 'workout/create_exercise.html', {'form': form})


@login_required
@require_POST
def start_workout_session_view(request):
    session = WorkoutSession.objects.create(user=request.user)
    return redirect('workout_session_detail', session_id=session.id)


@login_required
def workout_session_detail_view(request, session_id):
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    form = WorkoutSessionExerciseForm(user=request.user, workout_session=session)
    return render(request, 'workout/workout_session.html', {
        'session': session,
        'form': form,
    })


@login_required
@require_POST
def add_exercise_to_session_view(request, session_id):
    session = get_object_or_404(
        WorkoutSession,
        id=session_id,
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    )
    form = WorkoutSessionExerciseForm(request.POST, user=request.user, workout_session=session)
    if form.is_valid():
        next_position = (session.session_exercises.aggregate(Max('position'))['position__max'] or 0) + 1
        session_exercise = form.save(commit=False)
        session_exercise.workout_session = session
        session_exercise.position = next_position
        session_exercise.save()

    return redirect('workout_session_detail', session_id=session.id)
