from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from workout.models import Exercise, WorkoutExerciseSet, WorkoutSession, WorkoutSessionExercise


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

    def test_session_exercise_can_have_sets(self):
        session = WorkoutSession.objects.create(user=self.user)
        session_exercise = WorkoutSessionExercise.objects.create(
            workout_session=session,
            exercise=self.exercise,
            position=1,
        )
        workout_set = WorkoutExerciseSet.objects.create(
            workout_session_exercise=session_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
        )

        self.assertEqual(session.session_exercises.get(), session_exercise)
        self.assertEqual(session_exercise.sets.get(), workout_set)

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

    def test_user_can_start_a_session_and_add_an_available_exercise(self):
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('start_workout_session'))

        session = WorkoutSession.objects.get(user=self.user)
        self.assertRedirects(response, reverse('workout_session_detail', args=[session.id]))

        response = self.client.post(
            reverse('add_exercise_to_session', args=[session.id]),
            {'exercise': self.exercise.id},
        )

        self.assertRedirects(response, reverse('workout_session_detail', args=[session.id]))
        self.assertTrue(WorkoutSessionExercise.objects.filter(
            workout_session=session,
            exercise=self.exercise,
        ).exists())

    def test_starting_a_workout_resumes_existing_active_session(self):
        existing_session = WorkoutSession.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('start_workout_session'))

        self.assertRedirects(
            response,
            reverse('workout_session_detail', args=[existing_session.id]),
        )
        self.assertEqual(
            WorkoutSession.objects.filter(
                user=self.user,
                status=WorkoutSession.STATUS_ACTIVE,
            ).count(),
            1,
        )

    def test_user_can_add_a_set_to_a_session_exercise(self):
        session = WorkoutSession.objects.create(user=self.user)
        session_exercise = WorkoutSessionExercise.objects.create(
            workout_session=session,
            exercise=self.exercise,
            position=1,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('add_set_to_session_exercise', args=[session.id, session_exercise.id]),
            {'weight': 60, 'repetitions': 8},
        )

        self.assertRedirects(response, reverse('workout_session_detail', args=[session.id]))
        workout_set = WorkoutExerciseSet.objects.get(workout_session_exercise=session_exercise)
        self.assertEqual(workout_set.set_number, 1)
        self.assertEqual(workout_set.weight, 60)
        self.assertEqual(workout_set.repetitions, 8)

    def test_user_can_finish_an_active_workout_session(self):
        session = WorkoutSession.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('finish_workout_session', args=[session.id]))

        self.assertRedirects(response, reverse('workout'))
        session.refresh_from_db()
        self.assertEqual(session.status, WorkoutSession.STATUS_COMPLETED)
        self.assertIsNotNone(session.completed_at)
