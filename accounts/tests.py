from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, Role

class AccountsSecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.donor_user = User.objects.create_user(username='donor1', password='password123')
        self.donor_user.profile.role = Role.DONOR
        self.donor_user.profile.save()

        self.admin_user = User.objects.create_user(username='admin1', password='password123')
        self.admin_user.profile.role = Role.SUPER_ADMIN
        self.admin_user.profile.save()

    def test_login_and_logout(self):
        resp = self.client.post(reverse('accounts:login'), {'username': 'donor1', 'password': 'password123'})
        self.assertEqual(resp.status_code, 302)
        resp_logout = self.client.get(reverse('accounts:logout'))
        self.assertEqual(resp_logout.status_code, 302)

    def test_unauthorized_role_access(self):
        # Donor user trying to access user management list (restricted to Super Admin & Blood Bank Admin)
        self.client.login(username='donor1', password='password123')
        resp = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(resp.status_code, 403)

    def test_authorized_role_access(self):
        self.client.login(username='admin1', password='password123')
        resp = self.client.get(reverse('accounts:user_list'))
        self.assertEqual(resp.status_code, 200)
