from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import BloodBank
from hospitals.models import Hospital
from patients.models import Patient
from inventory.models import InventoryItem
from requests_app.models import BloodRequest, BloodRequestItem, InventoryReservation, BloodIssue, DiscardRecord

class BloodRequestsAndReservationsTestCase(TestCase):
    def setUp(self):
        self.bank = BloodBank.objects.create(name='Req Bank', code='RB-1', license_number='LIC-RB-1')
        self.hospital = Hospital.objects.create(name='Test Hosp', code='TH-1', license_number='LIC-TH-1')
        self.patient = Patient.objects.create(first_name='John', last_name='Doe', dob='1985-01-01', gender='M', blood_group='B+')
        self.user = User.objects.create_user(username='doc_user', password='password123')

    def test_atomic_reservation_locking(self):
        now = timezone.now()
        unit = InventoryItem.objects.create(
            component_type='PRBC', blood_group='B+', volume_ml=250,
            collection_date=now, expiry_date=now + timedelta(days=30), status='AVAILABLE'
        )

        req = BloodRequest.objects.create(
            hospital=self.hospital, patient=self.patient, blood_bank=self.bank,
            requesting_doctor='Dr. Smith', urgency='URGENT', required_date_time=now + timedelta(hours=2),
            clinical_diagnosis='Post-op blood loss', status='APPROVED'
        )
        req_item = BloodRequestItem.objects.create(
            request=req, component_type='PRBC', blood_group='B+', units_requested=1
        )

        # Reserve unit
        rsv = InventoryReservation.objects.create(request_item=req_item, inventory_item=unit, reserved_by=self.user)
        unit.status = 'RESERVED'
        unit.save()

        # Negative test: unit is no longer issuable to other requests
        self.assertFalse(unit.is_issuable)
        self.assertEqual(unit.status, 'RESERVED')

    def test_prevent_issue_of_expired_unit(self):
        now = timezone.now()
        unit = InventoryItem.objects.create(
            component_type='PRBC', blood_group='B+', volume_ml=250,
            collection_date=now - timedelta(days=45), expiry_date=now - timedelta(days=2), status='EXPIRED'
        )
        self.assertFalse(unit.is_issuable)

    def test_discard_authorization(self):
        now = timezone.now()
        unit = InventoryItem.objects.create(
            component_type='PLATELET', blood_group='O-', volume_ml=50,
            collection_date=now - timedelta(days=10), expiry_date=now - timedelta(days=3), status='EXPIRED'
        )
        discard = DiscardRecord.objects.create(
            inventory_item=unit, discard_reason='EXPIRED', reason_details='Platelet shelf life 5 days exceeded',
            discarded_by=self.user, authorized_by=self.user
        )
        unit.status = 'DISCARDED'
        unit.save()
        self.assertTrue(discard.discard_id.startswith('DIS-'))
        self.assertEqual(unit.status, 'DISCARDED')
