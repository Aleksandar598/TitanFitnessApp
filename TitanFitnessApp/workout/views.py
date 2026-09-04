from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from workout.forms.ExerciseForm import ExerciseForm
from workout.forms.WorkoutExerciseSetForm import WorkoutExerciseSetForm
from workout.forms.WorkoutSessionExerciseForm import WorkoutSessionExerciseForm
from workout.models import Exercise, WorkoutSession, WorkoutSessionExercise, WorkoutExerciseSet


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
    active_session = WorkoutSession.objects.filter(user=request.user, status=WorkoutSession.STATUS_ACTIVE,).first()

    if active_session:
        return redirect(
            'workout_session_detail', session_id=active_session.id,)

    session = WorkoutSession.objects.create(user=request.user)
    return redirect('workout_session_detail', session_id=session.id,)


@login_required
def workout_session_detail_view(request, session_id):
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    form = WorkoutSessionExerciseForm(user=request.user, workout_session=session)
    set_form = WorkoutExerciseSetForm()
    return render(request, 'workout/workout_session.html', {
        'session': session,
        'form': form,
        'set_form': set_form,
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


@login_required
@require_POST
def add_set_to_session_exercise_view(request, session_id, session_exercise_id):
    session = get_object_or_404(
        WorkoutSession,
        id=session_id,
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    )
    session_exercise = get_object_or_404(
        WorkoutSessionExercise,
        id=session_exercise_id,
        workout_session=session,
    )
    form = WorkoutExerciseSetForm(request.POST)

    if form.is_valid():
        next_set_number = (
            session_exercise.sets.aggregate(Max('set_number'))['set_number__max'] or 0
        ) + 1
        workout_set = form.save(commit=False)
        workout_set.workout_session_exercise = session_exercise
        workout_set.set_number = next_set_number
        workout_set.save()

    return redirect('workout_session_detail', session_id=session.id)


@login_required
@require_POST
def remove_set_from_session_exercise_view(  request, session_id, session_exercise_id, set_id, ):
    session = get_object_or_404(
        WorkoutSession,
        id=session_id,
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    )
    session_exercise = get_object_or_404(
        WorkoutSessionExercise,
        id=session_exercise_id,
        workout_session=session,
    )
    workout_set = get_object_or_404(
        WorkoutExerciseSet,
        id=set_id,
        workout_session_exercise=session_exercise,
    )
    workout_set.delete()
    return redirect('workout_session_detail', session_id=session.id)


@login_required
@require_POST
def remove_exercise_from_session_view(request, session_id, session_exercise_id,):
    session = get_object_or_404(
        WorkoutSession,
        id=session_id,
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    )
    session_exercise = get_object_or_404(
        WorkoutSessionExercise,
        id=session_exercise_id,
        workout_session=session,
    )
    session_exercise.delete()
    return redirect('workout_session_detail', session_id=session.id)


@login_required
@require_POST
def finish_workout_session_view(request, session_id):
    session = get_object_or_404(
        WorkoutSession,
        id=session_id,
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    )
    session.status = WorkoutSession.STATUS_COMPLETED
    session.completed_at = timezone.now()
    session.save(update_fields=('status', 'completed_at'))
    return redirect('workout')
