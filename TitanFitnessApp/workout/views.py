from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST

from workout.forms.ExerciseForm import ExerciseForm
from workout.forms.WorkoutExerciseForm import WorkoutExerciseForm
from workout.forms.WorkoutForm import WorkoutForm
from workout.forms.WorkoutPlanExerciseSetForm import WorkoutPlanExerciseSetForm
from workout.forms.WorkoutExerciseSetForm import WorkoutExerciseSetForm
from workout.forms.WorkoutSessionExerciseForm import WorkoutSessionExerciseForm
from workout.models import (
    Exercise,
    Workout,
    WorkoutExercise,
    WorkoutPlanExerciseSet,
    WorkoutSession,
    WorkoutSessionExercise,
    WorkoutExerciseSet,
)


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
def workout_history_view(request):
    completed_sessions = WorkoutSession.objects.filter(
        user=request.user,
        status=WorkoutSession.STATUS_COMPLETED,
    ).order_by('-completed_at')

    return render(request, 'workout/workout_history.html', {
        'completed_sessions': completed_sessions,
    })


@login_required
def workout_plan_list_view(request):
    workout_plans = Workout.objects.filter(user=request.user)

    return render(request, 'workout/workout_plan_list.html', {
        'workout_plans': workout_plans,
    })


@login_required
def create_workout_plan_view(request):
    if request.method == 'POST':
        form = WorkoutForm(request.POST, user=request.user)

        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()

            return redirect('workout_plan_list')
    else:
        form = WorkoutForm(user=request.user)

    return render(request, 'workout/create_workout_plan.html', {
        'form': form,
    })


@login_required
@require_POST
def delete_workout_plan_view(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    workout.delete()

    return redirect('workout_plan_list')


@login_required
def workout_plan_detail_view(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )
    form = WorkoutExerciseForm(
        user=request.user,
        workout=workout,
    )
    set_form = WorkoutPlanExerciseSetForm()

    return render(request, 'workout/workout_plan_detail.html', {
        'workout': workout,
        'form': form,
        'set_form': set_form,
    })


@login_required
@require_POST
def add_exercise_to_workout_plan_view(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )
    form = WorkoutExerciseForm(
        request.POST,
        user=request.user,
        workout=workout,
    )

    if form.is_valid():
        next_position = (
            workout.workout_exercises.aggregate(Max('position'))[
                'position__max'
            ] or 0
        ) + 1

        workout_exercise = form.save(commit=False)
        workout_exercise.workout = workout
        workout_exercise.position = next_position
        workout_exercise.save()

    return redirect('workout_plan_detail', workout_id=workout.id)


@login_required
@require_POST
def add_planned_set_to_workout_exercise_view(
    request,
    workout_id,
    workout_exercise_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )
    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )
    form = WorkoutPlanExerciseSetForm(request.POST)

    if form.is_valid():
        next_set_number = (
            workout_exercise.planned_sets.aggregate(
                Max('set_number')
            )['set_number__max'] or 0
        ) + 1

        planned_set = form.save(commit=False)
        planned_set.workout_exercise = workout_exercise
        planned_set.set_number = next_set_number
        planned_set.save()

    return redirect('workout_plan_detail', workout_id=workout.id)


@login_required
@require_POST
def remove_exercise_from_workout_plan_view(
    request,
    workout_id,
    workout_exercise_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )
    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )

    workout_exercise.delete()

    return redirect('workout_plan_detail', workout_id=workout.id)


@login_required
@require_POST
def remove_planned_set_view(
    request,
    workout_id,
    workout_exercise_id,
    planned_set_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )
    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )
    planned_set = get_object_or_404(
        WorkoutPlanExerciseSet,
        id=planned_set_id,
        workout_exercise=workout_exercise,
    )

    planned_set.delete()

    return redirect('workout_plan_detail', workout_id=workout.id)


@login_required
@require_POST
def start_workout_plan_view(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    active_session = WorkoutSession.objects.filter(
        user=request.user,
        status=WorkoutSession.STATUS_ACTIVE,
    ).first()

    if active_session:
        messages.error(
            request,
            'There is a workout in progress',
        )

        next_url = request.POST.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

        return redirect(
            'workout_plan_detail',
            workout_id=workout.id,
        )

    workout_exercises = list(
        workout.workout_exercises.select_related(
            'exercise'
        ).prefetch_related(
            'planned_sets'
        )
    )

    if not workout_exercises:
        messages.error(
            request,
            'Add at least one exercise before starting this workout plan.',
        )
        return redirect('workout_plan_detail', workout_id=workout.id)

    if any(
        not workout_exercise.exercise.is_active
        for workout_exercise in workout_exercises
    ):
        messages.error(
            request,
            'This workout plan contains an archived exercise. Edit the plan first.',
        )
        return redirect('workout_plan_detail', workout_id=workout.id)

    with transaction.atomic():
        session = WorkoutSession.objects.create(
            user=request.user,
            workout=workout,
        )

        for workout_exercise in workout_exercises:
            session_exercise = WorkoutSessionExercise.objects.create(
                workout_session=session,
                exercise=workout_exercise.exercise,
                position=workout_exercise.position,
            )

            WorkoutExerciseSet.objects.bulk_create([
                WorkoutExerciseSet(
                    workout_session_exercise=session_exercise,
                    set_number=planned_set.set_number,
                    weight=planned_set.weight,
                    repetitions=planned_set.repetitions,
                    is_completed=False,
                )
                for planned_set in workout_exercise.planned_sets.all()
            ])

    return redirect(
        'workout_session_detail',
        session_id=session.id,
    )


@login_required
def exercise_list_view(request):
    exercises = Exercise.objects.filter(
        Q(created_by__isnull=True) | Q(created_by=request.user),
        is_active=True,
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
def archive_personal_exercise_view(request, exercise_id):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        created_by=request.user,
        is_active=True,
    )

    exercise.is_active = False
    exercise.save(update_fields=('is_active',))

    return redirect('exercise_list')


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
def complete_workout_set_view(
    request,
    session_id,
    session_exercise_id,
    set_id,
):
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
        is_completed=False,
    )

    workout_set.is_completed = True
    workout_set.save(update_fields=('is_completed',))

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

    incomplete_sets_exist = WorkoutExerciseSet.objects.filter(
        workout_session_exercise__workout_session=session,
        is_completed=False,
    ).exists()

    if incomplete_sets_exist:
        messages.error(
            request,
            'Complete or remove all sets before finishing the workout.',
        )
        return redirect(
            'workout_session_detail',
            session_id=session.id,
        )

    session.status = WorkoutSession.STATUS_COMPLETED
    session.completed_at = timezone.now()
    session.set_calories()
    session.save(update_fields=('status', 'completed_at', 'calories_burned'))
    return redirect('workout')
