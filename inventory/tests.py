from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import BloodBank
from inventory.models import StorageArea, StorageDevice, InventoryItem, QuarantineRecord

class InventoryColdChainTestCase(TestCase):
    def setUp(self):
        self.bank = BloodBank.objects.create(name='Inv Test Bank', code='ITB-1', license_number='LIC-ITB')
        self.area = StorageArea.objects.create(name='Vault', code='VLT-1', blood_bank=self.bank)
        self.dev = StorageDevice.objects.create(
            name='PRBC Fridge', code='PRF-1', area=self.area, device_type='REFRIGERATOR_2_6C',
            min_temp_c=2.0, max_temp_c=6.0, target_temp_c=4.0
        )
        self.user = User.objects.create_user(username='test_tech', password='password123')

    def test_quarantined_unit_cannot_be_issued(self):
        now = timezone.now()
        item = InventoryItem.objects.create(
            component_type='PRBC', blood_group='O+', volume_ml=250,
            collection_date=now, expiry_date=now + timedelta(days=35), status='QUARANTINED'
        )
        self.assertFalse(item.is_issuable)

    def test_expired_unit_cannot_be_issued(self):
        now = timezone.now()
        item = InventoryItem.objects.create(
            component_type='PRBC', blood_group='O+', volume_ml=250,
            collection_date=now - timedelta(days=50), expiry_date=now - timedelta(days=5), status='AVAILABLE'
        )
        self.assertFalse(item.is_issuable)
        self.assertEqual(item.status, 'EXPIRED')

    def test_quarantine_record_and_release(self):
        now = timezone.now()
        item = InventoryItem.objects.create(
            component_type='FFP', blood_group='A+', volume_ml=180,
            collection_date=now, expiry_date=now + timedelta(days=300), status='AVAILABLE'
        )
        self.assertTrue(item.is_issuable)

        # Place in quarantine
        qr = QuarantineRecord.objects.create(
            inventory_item=item, reason='TEMPERATURE_EXCURSION', quarantined_by=self.user, notes='Temp excursion log'
        )
        item.status = 'QUARANTINED'
        item.save()
        self.assertFalse(item.is_issuable)

        # Release from quarantine
        qr.is_released = True
        qr.released_by = self.user
        qr.release_date = timezone.now()
        qr.release_reason = 'Cold chain re-validated safe'
        qr.save()
        item.status = 'AVAILABLE'
        item.save()
        self.assertTrue(item.is_issuable)
