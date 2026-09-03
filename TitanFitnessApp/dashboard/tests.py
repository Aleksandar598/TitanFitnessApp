from datetime import date

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


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
