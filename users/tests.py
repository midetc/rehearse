from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class SignUpViewTest(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        self.client.post(reverse("register"), {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_logs_in_automatically(self):
        self.client.post(reverse("register"), {
            "username": "autologin",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        user = User.objects.get(username="autologin")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_register_redirects_to_select_collection(self):
        response = self.client.post(reverse("register"), {
            "username": "redirect_user",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("hub:select-collection"))

    def test_weak_password_rejected(self):
        self.client.post(reverse("register"), {
            "username": "weakuser",
            "password1": "123",
            "password2": "123",
        })
        self.assertFalse(User.objects.filter(username="weakuser").exists())

    def test_duplicate_username_shows_form_error(self):
        User.objects.create_user(username="taken", password="Pass1234!")
        response = self.client.post(reverse("register"), {
            "username": "taken",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
