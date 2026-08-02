from datetime import date

from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class LoginViewTest(TestCase):

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
        self.login_url = reverse("login")
        self.dashboard_url = reverse("dashboard")
    def tearDown(self):
        self.client.logout()

    def test_get_login_page_form(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
        self.assertIn("form", response.context)

    def test_logged_in_user(self):
        self.client.login(username='undfined', password='misho')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.dashboard_url)

    def test_successful_login(self):
        response = self.client.post(self.login_url, {'username': self.user.username , 'password': 'misho' })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_wrong_login(self):
        response = self.client.post(self.login_url, {'username': self.user.username , 'password': 'Wrong Password' })
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        form = response.context["form"]
        self.assertFalse(form.is_valid())