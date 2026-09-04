from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Role

class ReportsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='report_admin', password='password123')
        self.admin_user.profile.role = Role.BLOOD_BANK_ADMIN
        self.admin_user.profile.save()
        self.client.login(username='report_admin', password='password123')

    def test_reports_index_view(self):
        resp = self.client.get(reverse('reports:index'))
        self.assertEqual(resp.status_code, 200)

    def test_donor_report_csv_export(self):
        resp = self.client.get(reverse('reports:donors') + '?export=csv')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')

    def test_donor_report_pdf_export(self):
        resp = self.client.get(reverse('reports:donors') + '?export=pdf')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
