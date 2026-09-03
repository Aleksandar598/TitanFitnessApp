from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from workout.models import Exercise, Workout, WorkoutExercise, WorkoutExerciseSet


class WorkoutModelsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='workout-user', email='workout@example.com', password='password123',
            birth_date='1990-01-01', height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.exercise = Exercise.objects.create(
            name='Bench Press', muscle_group='Chest', description='Barbell chest press.',
        )

    def test_workout_can_have_an_exercise_with_planned_sets(self):
        workout = Workout.objects.create(user=self.user, name='Push Day')
        workout_exercise = WorkoutExercise.objects.create(
            workout=workout,
            exercise=self.exercise,
            position=1,
        )
        planned_set = WorkoutExerciseSet.objects.create(
            workout_exercise=workout_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
        )

        self.assertEqual(workout.workout_exercises.get(), workout_exercise)
        self.assertEqual(workout_exercise.sets.get(), planned_set)

    def test_user_can_create_a_personal_exercise(self):
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('create_personal_exercise'), {
            'name': 'Band Pull Apart',
            'description': 'Rear shoulder exercise.',
            'muscle_group': 'Shoulders',
        })

        self.assertRedirects(response, reverse('exercise_list'))
        exercise = Exercise.objects.get(name='Band Pull Apart')
        self.assertEqual(exercise.created_by, self.user)

    def test_exercise_list_does_not_show_another_users_personal_exercises(self):
        other_user = CustomUser.objects.create_user(
            username='other-workout-user', email='other-workout@example.com', password='password123',
            birth_date='1990-01-01', height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        Exercise.objects.create(name='Private exercise', created_by=other_user)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('exercise_list'))

        self.assertNotContains(response, 'Private exercise')
        self.assertContains(response, 'Bench Press')

    def test_exercise_list_shows_the_users_personal_exercise(self):
        Exercise.objects.create(name='Band Pull Apart', created_by=self.user)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('exercise_list'))

        self.assertContains(response, 'Bench Press')
        self.assertContains(response, 'Band Pull Apart')

    def test_workout_menu_requires_login(self):
        response = self.client.get(reverse('workout'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('workout')}")

    def test_logged_in_user_can_open_workout_menu(self):
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('workout'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'workout/workout.html')
