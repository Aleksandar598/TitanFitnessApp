from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from nutrition.models import Food, FoodLog
from users.models import CustomUser


class FoodLogListViewsTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='log-list-user', email='log-list@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.other_user = CustomUser.objects.create_user(
            username='other-log-user', email='other-log@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.food = Food.objects.create(
            user=self.user, name='Eggs', quantity=100, quantity_type='g',
            protein=13, carbohydrates=1, fat=11, calories=155,
        )

    def test_today_view_shows_only_current_users_logs_and_totals(self):
        FoodLog.objects.create(user=self.user, food=self.food, quantity=100, date=timezone.localdate())
        FoodLog.objects.create(user=self.other_user, food=self.food, quantity=100, date=timezone.localdate())
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('today_food_log'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['logs']), [FoodLog.objects.filter(user=self.user).get()])
        self.assertEqual(response.context['totals']['calories'], 155)

    def test_history_view_shows_the_selected_day(self):
        selected_date = date(2026, 8, 1)
        FoodLog.objects.create(user=self.user, food=self.food, quantity=100, date=selected_date)
        self.client.login(username=self.user.username, password='password123')

        response = self.client.get(reverse('food_log_history'), {'date': selected_date.isoformat()})

        self.assertEqual(response.context['selected_date'], selected_date)
        self.assertContains(response, 'Eggs')

    def test_user_can_remove_own_food_log_from_today(self):
        log = FoodLog.objects.create(user=self.user, food=self.food, quantity=100, date=timezone.localdate())
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('remove_today_food_log', args=[log.id]))

        self.assertRedirects(response, reverse('today_food_log'))
        self.assertFalse(FoodLog.objects.filter(id=log.id).exists())

    def test_user_cannot_remove_another_users_food_log(self):
        log = FoodLog.objects.create(user=self.other_user, food=self.food, quantity=100, date=timezone.localdate())
        self.client.login(username=self.user.username, password='password123')

        response = self.client.post(reverse('remove_today_food_log', args=[log.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(FoodLog.objects.filter(id=log.id).exists())
