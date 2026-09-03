from django.contrib import admin

from workout.models import Exercise, Workout, WorkoutExercise, WorkoutExerciseSet


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'muscle_group', 'created_by')
    search_fields = ('name', 'muscle_group')
    list_filter = ('muscle_group', 'created_by')


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 0
    ordering = ('position',)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'updated_at')
    search_fields = ('name', 'user__username')
    inlines = (WorkoutExerciseInline,)


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'exercise', 'position')
    list_filter = ('workout',)


@admin.register(WorkoutExerciseSet)
class WorkoutExerciseSetAdmin(admin.ModelAdmin):
    list_display = ('workout_exercise', 'set_number', 'weight', 'repetitions')
    list_filter = ('workout_exercise__workout',)
