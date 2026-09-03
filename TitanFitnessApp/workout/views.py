from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from workout.forms.ExerciseForm import ExerciseForm
from workout.models import Exercise


@login_required
def workout_view(request):
    return render(request, 'workout/workout.html')


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
