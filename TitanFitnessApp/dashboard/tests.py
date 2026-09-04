from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from nutrition.models import FoodLog
from users.models import CustomUser
from workout.models import WorkoutSession


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='dashboard-user', email='dashboard@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_is_rendered_by_dashboard_app(self):
        self.client.login(username=self.user.username, password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard_shows_daily_intake_and_workout_compensation(self):
        FoodLog.objects.create(
            user=self.user,
            quantity=100,
            date=timezone.localdate(),
            food_name='Oatmeal',
            quantity_type='g',
            calories=1000,
            protein=50,
            carbohydrates=100,
            fat=30,
        )
        WorkoutSession.objects.create(
            user=self.user,
            status=WorkoutSession.STATUS_COMPLETED,
            completed_at=timezone.now(),
            calories_burned=400,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['daily_intake'], {
            'calories': 1000,
            'protein': 50,
            'carbohydrates': 100,
            'fat': 30,
        })
        self.assertEqual(response.context['workout_calories_burned'], 400)
        self.assertEqual(
            response.context['daily_goals'],
            self.user.daily_macronutrient_goals_with_workout(400),
        )

    def test_dashboard_excludes_other_users_food_and_workout_data(self):
        other_user = CustomUser.objects.create_user(
            username='other-dashboard-user',
            email='other-dashboard@example.com',
            password='password123',
            birth_date=date(1990, 1, 1),
            height=180,
            gender='male',
            current_weight=80,
            target_weight=80,
            fitness_goal=0,
            activity_level=1.2,
        )
        FoodLog.objects.create(
            user=other_user,
            quantity=100,
            date=timezone.localdate(),
            food_name='Other food',
            quantity_type='g',
            calories=1000,
            protein=50,
            carbohydrates=100,
            fat=30,
        )
        WorkoutSession.objects.create(
            user=other_user,
            status=WorkoutSession.STATUS_COMPLETED,
            completed_at=timezone.now(),
            calories_burned=400,
        )
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['daily_intake'], {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
        })
        self.assertEqual(response.context['workout_calories_burned'], 0)
