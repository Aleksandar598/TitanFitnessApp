from datetime import date

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='undfined',
                                               email='misho@misho.net',
                                               password='misho',
                                               birth_date=date(1970, 1, 1),
                                               height=100,
                                               gender='male',
                                               current_weight=100,
                                               target_weight=100,
                                               fitness_goal=0,
                                               activity_level=1.2,
                                               )
        self.logout = reverse('logout')
    def test_logout_successful(self):
        self.client.login(username='undfined', password='misho')
        response = self.client.post(self.logout)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse('home'))

    def test_get_logout_not_logging_out(self):
        self.client.login(username='undfined', password='misho')
        response = self.client.get(self.logout)
        self.assertTrue(response.wsgi_request.user.is_authenticated)