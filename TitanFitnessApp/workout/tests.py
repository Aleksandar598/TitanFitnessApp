from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser
from workout.models import (
    Exercise,
    Workout,
    WorkoutExercise,
    WorkoutExerciseSet,
    WorkoutPlanExerciseSet,
    WorkoutSession,
    WorkoutSessionExercise,
)


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

    def test_user_can_create_a_workout_plan(self):
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('create_workout_plan'),
            {'name': 'Push day'},
        )

        self.assertRedirects(response, reverse('workout_plan_list'))

        workout_plan = Workout.objects.get(
            user=self.user,
            name='Push day',
        )
        self.assertEqual(workout_plan.user, self.user)

    def test_user_can_add_an_exercise_to_a_workout_plan(self):
        workout_plan = Workout.objects.create(
            user=self.user,
            name='Push day',
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('add_exercise_to_workout_plan', args=[workout_plan.id]),
            {'exercise': self.exercise.id},
        )

        self.assertRedirects(
            response,
            reverse('workout_plan_detail', args=[workout_plan.id]),
        )

        workout_exercise = WorkoutExercise.objects.get(
            workout=workout_plan,
            exercise=self.exercise,
        )
        self.assertEqual(workout_exercise.position, 1)

    def test_starting_workout_plan_copies_exercises_and_planned_sets(self):
        workout_plan = Workout.objects.create(
            user=self.user,
            name='Push day',
        )
        workout_exercise = WorkoutExercise.objects.create(
            workout=workout_plan,
            exercise=self.exercise,
            position=1,
        )
        WorkoutPlanExerciseSet.objects.create(
            workout_exercise=workout_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('start_workout_plan', args=[workout_plan.id]),
        )

        session = WorkoutSession.objects.get(
            user=self.user,
            workout=workout_plan,
        )
        self.assertRedirects(
            response,
            reverse('workout_session_detail', args=[session.id]),
        )

        session_exercise = session.session_exercises.get()
        workout_set = session_exercise.sets.get()

        self.assertEqual(session_exercise.exercise, self.exercise)
        self.assertEqual(workout_set.weight, 60)
        self.assertEqual(workout_set.repetitions, 8)
        self.assertFalse(workout_set.is_completed)

    def test_user_can_remove_a_planned_set(self):
        workout_plan = Workout.objects.create(
            user=self.user,
            name='Push day',
        )
        workout_exercise = WorkoutExercise.objects.create(
            workout=workout_plan,
            exercise=self.exercise,
            position=1,
        )
        planned_set = WorkoutPlanExerciseSet.objects.create(
            workout_exercise=workout_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse(
                'remove_planned_set',
                args=[
                    workout_plan.id,
                    workout_exercise.id,
                    planned_set.id,
                ],
            ),
        )

        self.assertRedirects(
            response,
            reverse('workout_plan_detail', args=[workout_plan.id]),
        )
        self.assertFalse(
            WorkoutPlanExerciseSet.objects.filter(
                id=planned_set.id,
            ).exists()
        )
        self.assertTrue(
            WorkoutExercise.objects.filter(
                id=workout_exercise.id,
            ).exists()
        )

    def test_user_can_remove_an_exercise_from_a_workout_plan(self):
        workout_plan = Workout.objects.create(
            user=self.user,
            name='Push day',
        )
        workout_exercise = WorkoutExercise.objects.create(
            workout=workout_plan,
            exercise=self.exercise,
            position=1,
        )
        planned_set = WorkoutPlanExerciseSet.objects.create(
            workout_exercise=workout_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse(
                'remove_exercise_from_workout_plan',
                args=[workout_plan.id, workout_exercise.id],
            ),
        )

        self.assertRedirects(
            response,
            reverse('workout_plan_detail', args=[workout_plan.id]),
        )
        self.assertFalse(
            WorkoutExercise.objects.filter(
                id=workout_exercise.id,
            ).exists()
        )
        self.assertFalse(
            WorkoutPlanExerciseSet.objects.filter(
                id=planned_set.id,
            ).exists()
        )
        self.assertTrue(
            Exercise.objects.filter(id=self.exercise.id).exists()
        )

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
        self.assertFalse(workout_set.is_completed)

    def test_user_can_finish_an_active_workout_session(self):
        session = WorkoutSession.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('finish_workout_session', args=[session.id]))

        self.assertRedirects(response, reverse('workout'))
        session.refresh_from_db()
        self.assertEqual(session.status, WorkoutSession.STATUS_COMPLETED)
        self.assertIsNotNone(session.completed_at)

    def test_user_cannot_finish_workout_with_incomplete_sets(self):
        session = WorkoutSession.objects.create(user=self.user)
        session_exercise = WorkoutSessionExercise.objects.create(
            workout_session=session,
            exercise=self.exercise,
            position=1,
        )
        WorkoutExerciseSet.objects.create(
            workout_session_exercise=session_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
            is_completed=False,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('finish_workout_session', args=[session.id]),
        )

        self.assertRedirects(
            response,
            reverse('workout_session_detail', args=[session.id]),
        )
        session.refresh_from_db()
        self.assertEqual(session.status, WorkoutSession.STATUS_ACTIVE)
        self.assertIsNone(session.completed_at)

    def test_finishing_workout_saves_calories_burned(self):
        session = WorkoutSession.objects.create(user=self.user)
        session_exercise = WorkoutSessionExercise.objects.create(
            workout_session=session,
            exercise=self.exercise,
            position=1,
        )
        WorkoutExerciseSet.objects.create(
            workout_session_exercise=session_exercise,
            set_number=1,
            weight=60,
            repetitions=8,
            is_completed=True,
        )
        WorkoutExerciseSet.objects.create(
            workout_session_exercise=session_exercise,
            set_number=2,
            weight=40,
            repetitions=10,
            is_completed=True,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(
            reverse('finish_workout_session', args=[session.id]),
        )

        self.assertRedirects(response, reverse('workout'))
        session.refresh_from_db()

        # Volume: (60 × 8) + (40 × 10) = 880
        # Repetitions: 8 + 10 = 18
        # Weight: 80 kg
        # round((880 + (18 × 80 × 1)) × 0.014) = 32
        self.assertEqual(session.calories_burned, 32)
