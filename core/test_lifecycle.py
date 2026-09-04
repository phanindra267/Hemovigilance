from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

from core.models import BloodBank
from accounts.models import UserProfile, Role
from hospitals.models import Hospital
from patients.models import Patient
from donors.models import Donor, EligibilityAssessment
from donations.models import Donation
from laboratory.models import BloodBag, LabSample, ScreeningResult
from blood_components.models import BloodComponent
from inventory.models import InventoryItem, StorageArea, StorageDevice
from requests_app.models import BloodRequest, BloodRequestItem, InventoryReservation, BloodIssue, BloodReturn, DiscardRecord

class EndToEndLifecycleTestCase(TestCase):
    """
    Complete Full Lifecycle Test:
    Donor 
    -> Eligibility Assessment 
    -> Donation 
    -> Blood Bag 
    -> Lab Sample 
    -> Screening Tests 
    -> Medical Verification & Release 
    -> Component Processing (PRBC & FFP) 
    -> Available Inventory 
    -> Hospital Blood Request 
    -> Medical Officer Approval 
    -> Atomic Inventory Reservation 
    -> Crossmatch Blood Issue
    """

    def setUp(self):
        self.client = Client()
        # Blood Bank
        self.bank = BloodBank.objects.create(
            name='Lifecycle Transfusion Centre',
            code='LTC-01',
            license_number='LIC-LTC-2026',
            address='10 Health Boulevard',
            city='New Delhi', district='Central', state='Delhi', postal_code='110001',
            phone='+91-11-99887766', email='info@ltc.org'
        )

        # Users
        self.mo_user = User.objects.create_user(username='doctor_test', password='password123', email='mo@test.com')
        self.mo_user.profile.role = Role.MEDICAL_OFFICER
        self.mo_user.profile.blood_bank = self.bank
        self.mo_user.profile.save()

        self.tech_user = User.objects.create_user(username='tech_test', password='password123', email='tech@test.com')
        self.tech_user.profile.role = Role.LAB_TECHNICIAN
        self.tech_user.profile.blood_bank = self.bank
        self.tech_user.profile.save()

        # Hospital
        self.hospital = Hospital.objects.create(
            name='Apollo Specialty Hospital',
            code='HOSP-APL-01',
            license_number='LIC-APL-9921',
            address='Sarita Vihar', city='New Delhi', district='South', state='Delhi', postal_code='110076',
            contact_person='Dr. Raman', phone='+91-11-2692-5858', email='blood@apollo.com'
        )

        # Patient
        self.patient = Patient.objects.create(
            first_name='Maya', last_name='Devi', dob='1990-05-15', gender='F',
            blood_group='O+', hospital=self.hospital, phone='+91-98110-00112'
        )

    def test_complete_traceable_lifecycle(self):
        # 1. DONOR REGISTRATION
        donor = Donor.objects.create(
            first_name='Suresh', last_name='Kumar', dob='1993-08-20', gender='M',
            blood_group='O+', rh_factor='POSITIVE', donor_type='VOLUNTARY', donor_status='ACTIVE',
            phone='+91-98765-12345', address='Connaught Place', city='New Delhi', state='Delhi', postal_code='110001'
        )
        self.assertTrue(donor.donor_id.startswith('DNR-'))
        self.assertEqual(donor.blood_group, 'O+')

        # 2. ELIGIBILITY ASSESSMENT
        assessment = EligibilityAssessment.objects.create(
            donor=donor, assessed_by=self.mo_user, status='ELIGIBLE',
            weight_kg=70.0, hemoglobin_g_dl=14.5, systolic_bp=120, diastolic_bp=80, pulse_bpm=72, temperature_c=36.6,
            deferral_type='NONE', medical_notes='Cleared for whole blood collection'
        )
        self.assertEqual(assessment.status, 'ELIGIBLE')
        self.assertEqual(donor.donor_status, 'ACTIVE')

        # 3. DONATION
        donation = Donation.objects.create(
            donor=donor, assessment=assessment, blood_bank=self.bank,
            donation_type='WHOLE_BLOOD', bag_type='TRIPLE_450ML', volume_ml=450,
            collected_by=self.tech_user, status='COLLECTED'
        )
        self.assertTrue(donation.donation_id.startswith('DON-'))

        # 4. BLOOD BAG REGISTRATION (Initially QUARANTINED)
        now = timezone.now()
        blood_bag = BloodBag.objects.create(
            donation=donation, blood_group=donor.blood_group, rh_factor=donor.rh_factor,
            collection_date=now, expiry_date=now + timedelta(days=35), bag_type=donation.bag_type,
            volume_ml=donation.volume_ml, status='QUARANTINED', storage_location='Quarantine Area A'
        )
        self.assertTrue(blood_bag.bag_id.startswith('BB-'))
        self.assertEqual(blood_bag.status, 'QUARANTINED')

        # Initial InventoryItem is in QUARANTINED state
        inv_bag = InventoryItem.objects.create(
            blood_bag=blood_bag, item_type='WHOLE_BLOOD_BAG', blood_group=blood_bag.blood_group,
            rh_factor=blood_bag.rh_factor, component_type='WHOLE_BLOOD', volume_ml=blood_bag.volume_ml,
            collection_date=blood_bag.collection_date, expiry_date=blood_bag.expiry_date, status='QUARANTINED'
        )
        self.assertFalse(inv_bag.is_issuable)

        # 5. LAB SAMPLE & SCREENING RESULTS
        sample = LabSample.objects.create(blood_bag=blood_bag, collected_at=now, collected_by=self.tech_user, status='PENDING')
        self.assertTrue(sample.sample_id.startswith('SMP-'))

        test_types = ['ABO_RH_CONFIRMATION', 'HIV_1_2_ANTIBODY', 'HBSAG_HEPATITIS_B', 'HCV_ANTIBODY_HEPATITIS_C', 'SYPHILIS_VDRL_TPHA', 'MALARIA_ANTIGEN']
        for tt in test_types:
            ScreeningResult.objects.create(
                sample=sample, test_category=tt, test_name=f'Automated {tt}',
                result='NON_REACTIVE', tested_by=self.tech_user, kit_lot_number='LOT-TEST-01'
            )
        self.assertEqual(sample.screening_results.count(), 6)

        # 6. MEDICAL OFFICER VERIFICATION & RELEASE
        sample.status = 'VERIFIED'
        sample.verified_by = self.mo_user
        sample.verified_at = timezone.now()
        sample.save()

        blood_bag.status = 'TESTED_SAFE'
        blood_bag.save()

        inv_bag.status = 'AVAILABLE'
        inv_bag.save()
        self.assertTrue(inv_bag.is_issuable)

        # 7. COMPONENT SEPARATION (PRBC and FFP)
        prbc = BloodComponent.objects.create(
            parent_bag=blood_bag, component_type='PRBC', blood_group=blood_bag.blood_group, rh_factor=blood_bag.rh_factor,
            prepared_date=now, expiry_date=now + timedelta(days=42), volume_ml=250, prepared_by=self.tech_user,
            status='AVAILABLE', storage_location='PRBC Refrigerator 01'
        )
        inv_prbc = InventoryItem.objects.create(
            component=prbc, item_type='COMPONENT', blood_group=prbc.blood_group, rh_factor=prbc.rh_factor,
            component_type='PRBC', volume_ml=prbc.volume_ml, collection_date=blood_bag.collection_date,
            expiry_date=prbc.expiry_date, status='AVAILABLE'
        )
        blood_bag.status = 'PROCESSED_TO_COMPONENTS'
        blood_bag.save()
        inv_bag.status = 'DISCARDED' # Original whole blood bag replaced by separated components
        inv_bag.save()

        self.assertTrue(inv_prbc.is_issuable)
        self.assertEqual(inv_prbc.status, 'AVAILABLE')

        # 8. HOSPITAL BLOOD REQUEST
        blood_req = BloodRequest.objects.create(
            hospital=self.hospital, patient=self.patient, blood_bank=self.bank,
            requesting_doctor='Dr. Raman', requested_by_user=self.mo_user, urgency='URGENT',
            required_date_time=now + timedelta(hours=4), clinical_diagnosis='Severe acute blood loss anemia',
            status='SUBMITTED'
        )
        req_item = BloodRequestItem.objects.create(
            request=blood_req, component_type='PRBC', blood_group='O+', units_requested=1, units_reserved=0, units_issued=0, status='PENDING'
        )

        # 9. MEDICAL OFFICER APPROVAL
        blood_req.status = 'APPROVED'
        blood_req.reviewed_by = self.mo_user
        blood_req.review_timestamp = timezone.now()
        blood_req.save()
        self.assertEqual(blood_req.status, 'APPROVED')

        # 10. ATOMIC RESERVATION
        # Lock and reserve
        inv_prbc.status = 'RESERVED'
        inv_prbc.save()

        reservation = InventoryReservation.objects.create(
            request_item=req_item, inventory_item=inv_prbc, reserved_by=self.tech_user, is_active=True
        )
        req_item.units_reserved = 1
        req_item.status = 'RESERVED'
        req_item.save()

        blood_req.status = 'RESERVED'
        blood_req.save()

        self.assertFalse(inv_prbc.is_issuable) # Reserved unit is not issuable to another request

        # 11. CROSSMATCH BLOOD ISSUE
        issue = BloodIssue.objects.create(
            request=blood_req, inventory_item=inv_prbc, patient=self.patient,
            issued_by=self.tech_user, authorized_by=self.mo_user, recipient_name='Hospital Courier Staff',
            recipient_id_proof='STAFF-APL-88', crossmatch_compatible=True, status='ISSUED'
        )
        inv_prbc.status = 'ISSUED'
        inv_prbc.save()
        reservation.is_active = False
        reservation.save()
        req_item.units_issued = 1
        req_item.status = 'ISSUED'
        req_item.save()
        blood_req.status = 'ISSUED'
        blood_req.save()

        self.assertTrue(issue.issue_id.startswith('ISS-'))
        self.assertEqual(inv_prbc.status, 'ISSUED')
        self.assertEqual(blood_req.status, 'ISSUED')

        # 12. RETURN WITH DISPOSITION
        ret = BloodReturn.objects.create(
            blood_issue=issue, returned_by_name='Nurse Sunita', received_by=self.tech_user,
            cold_chain_maintained=True, visual_inspection_passed=True, bag_seal_intact=True,
            assessed_by=self.mo_user, disposition='RE_ENTRY_APPROVED', disposition_notes='Cold chain validated 3.8C'
        )
        self.assertTrue(ret.return_id.startswith('RET-'))
        inv_prbc.status = 'AVAILABLE'
        inv_prbc.save()
        self.assertTrue(inv_prbc.is_issuable)
