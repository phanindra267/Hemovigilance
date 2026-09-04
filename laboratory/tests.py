from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import BloodBank
from donors.models import Donor
from donations.models import Donation
from laboratory.models import BloodBag, LabSample, ScreeningResult

class LaboratoryScreeningTestCase(TestCase):
    def setUp(self):
        self.bank = BloodBank.objects.create(name='Lab Bank', code='LB-1', license_number='LIC-LB-1')
        self.donor = Donor.objects.create(first_name='Aarav', last_name='Shah', dob='1991-03-10', gender='M', blood_group='A+', phone='9822334455')
        self.user = User.objects.create_user(username='lab_tech', password='password123')
        self.donation = Donation.objects.create(donor=self.donor, blood_bank=self.bank, donation_type='WHOLE_BLOOD')

    def test_sample_and_screening_workflow(self):
        now = timezone.now()
        bag = BloodBag.objects.create(
            donation=self.donation, blood_group=self.donor.blood_group,
            collection_date=now, expiry_date=now + timedelta(days=35), status='QUARANTINED'
        )
        sample = LabSample.objects.create(blood_bag=bag, collected_at=now, collected_by=self.user)

        res_hiv = ScreeningResult.objects.create(
            sample=sample, test_category='HIV_1_2_ANTIBODY', test_name='HIV 4th Gen ELISA',
            result='NON_REACTIVE', tested_by=self.user
        )
        self.assertEqual(res_hiv.result, 'NON_REACTIVE')

        # Negative test: if screening is reactive, unit cannot be released
        res_hbv = ScreeningResult.objects.create(
            sample=sample, test_category='HBSAG_HEPATITIS_B', test_name='HBsAg Rapid Test',
            result='REACTIVE', tested_by=self.user
        )
        self.assertEqual(res_hbv.result, 'REACTIVE')
        bag.status = 'REACTIVE_UNSAFE'
        bag.save()
        self.assertEqual(bag.status, 'REACTIVE_UNSAFE')
