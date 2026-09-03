from datetime import date

from django.test import TestCase
from django.urls import reverse

from nutrition.models import Food
from users.models import CustomUser


class EditSavedFoodViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='food-editor', email='food-editor@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.other_user = CustomUser.objects.create_user(
            username='other-editor', email='other-editor@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.food = Food.objects.create(
            user=self.user, name='Oats', quantity=100, quantity_type='g',
            protein=13, carbohydrates=68, fat=7, calories=371,
        )

    def test_user_can_edit_own_food_and_calories_are_recalculated(self):
        self.client.login(username=self.user.username, password='password123')
        response = self.client.post(reverse('edit_saved_food', args=[self.food.id]), {
            'name': 'Oats', 'description': 'Updated oats', 'quantity': 100,
            'quantity_type': 'g', 'protein': 14, 'carbohydrates': 60, 'fat': 8,
        })

        self.assertRedirects(response, reverse('saved_foods'))
        self.food.refresh_from_db()
        self.assertEqual(self.food.calories, 368)
        self.assertEqual(self.food.description, 'Updated oats')

    def test_user_cannot_edit_another_users_food(self):
        self.client.login(username=self.other_user.username, password='password123')

        response = self.client.get(reverse('edit_saved_food', args=[self.food.id]))

        self.assertEqual(response.status_code, 404)
