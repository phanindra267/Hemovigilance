import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from core.models import BloodBank, SystemConfiguration
from accounts.models import UserProfile, Role
from hospitals.models import Hospital
from patients.models import Patient
from donors.models import Donor, EligibilityAssessment
from camps.models import BloodCamp, CampRegistration
from appointments.models import Appointment
from donations.models import Donation
from laboratory.models import BloodBag, LabSample, ScreeningResult
from blood_components.models import BloodComponent
from inventory.models import StorageArea, StorageDevice, StoragePosition, TemperatureLog, InventoryItem, QuarantineRecord
from requests_app.models import BloodRequest, BloodRequestItem, InventoryReservation, BloodIssue, BloodReturn, DiscardRecord
from notifications.models import Notification
from audit.models import AuditLog

class Command(BaseCommand):
    help = 'Seeds complete realistic synthetic demo data across all 15 RedLink apps'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting RedLink complete demo data seeding...'))

        with transaction.atomic():
            # 1. Primary Blood Bank
            bank, _ = BloodBank.objects.get_or_create(
                code='REDLINK-HQ',
                defaults={
                    'name': 'RedLink National Blood & Hemovigilance Centre',
                    'license_number': 'LIC-NBTC-2026-0982',
                    'registration_number': 'REG-HEALTH-IN-4921',
                    'address': 'Plot 42, Health City Avenue, Medical Enclave',
                    'city': 'New Delhi',
                    'district': 'Central Delhi',
                    'state': 'Delhi',
                    'postal_code': '110001',
                    'phone': '+91-11-2394-8000',
                    'email': 'centre@redlink.org',
                    'emergency_helpline': '1800-RED-LINK (1800-733-5465)',
                    'operating_hours': '24x7 Round-the-Clock Emergency Operations',
                }
            )

            # System Configurations
            configs = [
                ('DONOR_MIN_AGE', '18', 'CLINICAL', 'Minimum donor eligibility age'),
                ('DONOR_MAX_AGE', '65', 'CLINICAL', 'Maximum donor eligibility age'),
                ('DONOR_MIN_WEIGHT_KG', '45.0', 'CLINICAL', 'Minimum donor weight in kg'),
                ('DONOR_MIN_HB_FEMALE', '12.5', 'CLINICAL', 'Minimum hemoglobin for female donor (g/dL)'),
                ('DONOR_MIN_HB_MALE', '13.0', 'CLINICAL', 'Minimum hemoglobin for male donor (g/dL)'),
                ('DONATION_INTERVAL_DAYS', '90', 'CLINICAL', 'Minimum days between whole blood donations'),
                ('TEMP_PRBC_MIN', '2.0', 'STORAGE', 'Minimum storage temperature for PRBC (C)'),
                ('TEMP_PRBC_MAX', '6.0', 'STORAGE', 'Maximum storage temperature for PRBC (C)'),
                ('TEMP_PLATELET_MIN', '20.0', 'STORAGE', 'Minimum storage temperature for Platelets (C)'),
                ('TEMP_PLATELET_MAX', '24.0', 'STORAGE', 'Maximum storage temperature for Platelets (C)'),
                ('TEMP_FFP_MAX', '-18.0', 'STORAGE', 'Maximum storage temperature for FFP/Cryo (C)'),
            ]
            for k, val, cat, desc in configs:
                SystemConfiguration.objects.get_or_create(key=k, defaults={'value': val, 'category': cat, 'description': desc})

            # 2. Storage Hierarchy
            vault_area, _ = StorageArea.objects.get_or_create(code='AREA-VAULT-01', defaults={'name': 'Central Cold Chain Vault', 'blood_bank': bank})
            proc_area, _ = StorageArea.objects.get_or_create(code='AREA-PROC-01', defaults={'name': 'Component Processing Room', 'blood_bank': bank})

            dev_prbc, _ = StorageDevice.objects.get_or_create(
                code='DEV-REF-01',
                defaults={'name': 'PRBC Refrigerator Alpha (+2C to +6C)', 'area': vault_area, 'device_type': 'REFRIGERATOR_2_6C', 'target_temp_c': 4.0, 'min_temp_c': 2.0, 'max_temp_c': 6.0}
            )
            dev_ffp, _ = StorageDevice.objects.get_or_create(
                code='DEV-FRZ-01',
                defaults={'name': 'Deep Plasma Freezer Beta (-40C)', 'area': vault_area, 'device_type': 'FREEZER_MINUS_80C', 'target_temp_c': -40.0, 'min_temp_c': -50.0, 'max_temp_c': -20.0}
            )
            dev_plt, _ = StorageDevice.objects.get_or_create(
                code='DEV-AGT-01',
                defaults={'name': 'Platelet Agitator & Incubator Gamma (+22C)', 'area': proc_area, 'device_type': 'PLATELET_AGITATOR_20_24C', 'target_temp_c': 22.0, 'min_temp_c': 20.0, 'max_temp_c': 24.0}
            )

            # Positions
            for i in range(1, 4):
                StoragePosition.objects.get_or_create(device=dev_prbc, rack_identifier='Rack A', shelf_identifier=f'Shelf {i}', position_identifier=f'Slot {i}')
                StoragePosition.objects.get_or_create(device=dev_ffp, rack_identifier='Rack B', shelf_identifier=f'Shelf {i}', position_identifier=f'Slot {i}')
                StoragePosition.objects.get_or_create(device=dev_plt, rack_identifier=f'Tray {i}', shelf_identifier='Level 1', position_identifier=f'Bay {i}')

            # 3. Hospitals
            hosp_metro, _ = Hospital.objects.get_or_create(
                code='HOSP-METRO-01',
                defaults={
                    'name': 'Metro Multispeciality Hospital & Research Institute',
                    'license_number': 'HOSP-LIC-8821',
                    'category': 'PRIVATE',
                    'address': '12 Ring Road, South Extension',
                    'city': 'New Delhi', 'district': 'South Delhi', 'state': 'Delhi', 'postal_code': '110049',
                    'contact_person': 'Dr. Alok Verma (Medical Superintendent)',
                    'phone': '+91-11-4567-8900', 'email': 'bloodbank@metrohospital.org', 'emergency_contact': '+91-98110-22334'
                }
            )
            hosp_city, _ = Hospital.objects.get_or_create(
                code='HOSP-CITY-02',
                defaults={
                    'name': 'Government Civil Hospital & Trauma Centre',
                    'license_number': 'HOSP-GOV-1029',
                    'category': 'GOVERNMENT',
                    'address': 'Main Highway Junction, Sector 14',
                    'city': 'New Delhi', 'district': 'North Delhi', 'state': 'Delhi', 'postal_code': '110007',
                    'contact_person': 'Dr. Sunita Rao (Chief Medical Officer)',
                    'phone': '+91-11-2789-1122', 'email': 'trauma@citycivil.gov.in', 'emergency_contact': '+91-98765-43210'
                }
            )

            # 4. User Accounts across 9 Roles
            users_meta = [
                ('admin', 'admin@redlink.org', 'Super', 'Administrator', Role.SUPER_ADMIN, True, True),
                ('bb_admin', 'bbadmin@redlink.org', 'Vikram', 'Malhotra', Role.BLOOD_BANK_ADMIN, True, False),
                ('doctor_rajesh', 'rajesh.mo@redlink.org', 'Dr. Rajesh', 'Khurana', Role.MEDICAL_OFFICER, True, False),
                ('tech_priya', 'priya.lab@redlink.org', 'Priya', 'Sharma', Role.LAB_TECHNICIAN, True, False),
                ('tech_arun', 'arun.tech@redlink.org', 'Arun', 'Patel', Role.BLOOD_BANK_TECH, True, False),
                ('recep_meena', 'meena.reception@redlink.org', 'Meena', 'Iyer', Role.RECEPTIONIST, True, False),
                ('hospital_user', 'transfusion@metrohospital.org', 'Dr. Sanjay', 'Mehta', Role.HOSPITAL_USER, False, False),
                ('donor_user', 'rahul.donor@gmail.com', 'Rahul', 'Deshmukh', Role.DONOR, False, False),
                ('patient_user', 'ananya.recipient@gmail.com', 'Ananya', 'Sen', Role.PATIENT, False, False),
            ]

            created_users = {}
            for username, email, fname, lname, role, is_staff, is_super in users_meta:
                user = User.objects.filter(username=username).first()
                if not user:
                    user = User.objects.create_user(username=username, email=email, password='password123', first_name=fname, last_name=lname)
                user.is_staff = is_staff
                user.is_superuser = is_super
                user.save()

                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = role
                profile.phone = '+91-98230-12345'
                profile.blood_bank = bank
                if role == Role.HOSPITAL_USER:
                    profile.hospital = hosp_metro
                profile.save()
                created_users[username] = user

            # 5. Patients
            pat_ananya, _ = Patient.objects.get_or_create(
                patient_id='PAT-2026-000001',
                defaults={
                    'first_name': 'Ananya', 'last_name': 'Sen', 'dob': '1995-04-12', 'gender': 'F',
                    'blood_group': 'O+', 'hospital': hosp_metro, 'hospital_mrn': 'MRN-METRO-44912',
                    'attending_physician': 'Dr. Sanjay Mehta (Hematology)', 'ward_or_room': 'ICU Bed 04',
                    'phone': '+91-98101-55443', 'email': 'ananya.recipient@gmail.com',
                    'medical_history': 'Severe chronic anemia undergoing chemotherapy; regular packed cell transfusions required.'
                }
            )
            created_users['patient_user'].profile.patient_profile = pat_ananya
            created_users['patient_user'].profile.save()

            pat_rohit, _ = Patient.objects.get_or_create(
                patient_id='PAT-2026-000002',
                defaults={
                    'first_name': 'Rohit', 'last_name': 'Verma', 'dob': '1982-11-23', 'gender': 'M',
                    'blood_group': 'AB-', 'hospital': hosp_city, 'hospital_mrn': 'TRAUMA-991',
                    'attending_physician': 'Dr. Sunita Rao', 'ward_or_room': 'Emergency Trauma OT 2',
                    'phone': '+91-98711-22334', 'email': 'rohit.verma@example.com',
                    'medical_history': 'Polytrauma acute blood loss following road traffic accident.'
                }
            )

            # 6. Donors
            donor_rahul, _ = Donor.objects.get_or_create(
                donor_id='DNR-2026-000001',
                defaults={
                    'user': created_users['donor_user'],
                    'first_name': 'Rahul', 'last_name': 'Deshmukh', 'dob': '1992-06-15', 'gender': 'M',
                    'blood_group': 'O+', 'rh_factor': 'POSITIVE', 'donor_type': 'VOLUNTARY', 'donor_status': 'ACTIVE',
                    'phone': '+91-98220-11223', 'email': 'rahul.donor@gmail.com', 'national_id': 'UID-9912-3344-5566',
                    'address': 'Flat 302, Green Valley Apartments', 'city': 'New Delhi', 'district': 'South West', 'state': 'Delhi', 'postal_code': '110070',
                    'emergency_contact_name': 'Sneha Deshmukh', 'emergency_contact_phone': '+91-98220-99887', 'emergency_contact_relation': 'Spouse',
                    'registration_date': timezone.now().date() - timedelta(days=120),
                    'last_donation_date': timezone.now().date() - timedelta(days=95),
                    'next_eligible_date': timezone.now().date(),
                    'total_donations_count': 3
                }
            )
            created_users['donor_user'].profile.donor_profile = donor_rahul
            created_users['donor_user'].profile.save()

            donor_amit, _ = Donor.objects.get_or_create(
                donor_id='DNR-2026-000002',
                defaults={
                    'first_name': 'Amit', 'last_name': 'Kapur', 'dob': '1988-03-21', 'gender': 'M',
                    'blood_group': 'AB-', 'rh_factor': 'NEGATIVE', 'donor_type': 'VOLUNTARY', 'donor_status': 'ACTIVE',
                    'phone': '+91-98100-33445', 'email': 'amit.kapur@gmail.com', 'national_id': 'UID-4411-8899-2233',
                    'address': 'B-14 Hauz Khas', 'city': 'New Delhi', 'district': 'South Delhi', 'state': 'Delhi', 'postal_code': '110016',
                    'registration_date': timezone.now().date() - timedelta(days=200),
                    'total_donations_count': 5
                }
            )

            donor_kavita, _ = Donor.objects.get_or_create(
                donor_id='DNR-2026-000003',
                defaults={
                    'first_name': 'Kavita', 'last_name': 'Nair', 'dob': '1998-09-08', 'gender': 'F',
                    'blood_group': 'A+', 'rh_factor': 'POSITIVE', 'donor_type': 'VOLUNTARY', 'donor_status': 'ACTIVE',
                    'phone': '+91-98990-66778', 'email': 'kavita.nair@gmail.com', 'national_id': 'UID-1122-3344-9988',
                    'address': 'Sector 21 Dwarka', 'city': 'New Delhi', 'district': 'South West', 'state': 'Delhi', 'postal_code': '110077',
                    'registration_date': timezone.now().date() - timedelta(days=45),
                    'total_donations_count': 1
                }
            )

            donor_deferred, _ = Donor.objects.get_or_create(
                donor_id='DNR-2026-000004',
                defaults={
                    'first_name': 'Rakesh', 'last_name': 'Gupta', 'dob': '1994-01-18', 'gender': 'M',
                    'blood_group': 'B+', 'rh_factor': 'POSITIVE', 'donor_type': 'REPLACEMENT', 'donor_status': 'TEMPORARILY_DEFERRED',
                    'phone': '+91-98112-77889', 'email': 'rakesh.gupta@example.com',
                    'address': 'Model Town 2', 'city': 'New Delhi', 'district': 'North Delhi', 'state': 'Delhi', 'postal_code': '110009',
                    'registration_date': timezone.now().date() - timedelta(days=10),
                    'next_eligible_date': timezone.now().date() + timedelta(days=80),
                }
            )

            # 7. Eligibility Assessments
            ea_rahul, _ = EligibilityAssessment.objects.get_or_create(
                donor=donor_rahul,
                status='ELIGIBLE',
                defaults={
                    'assessed_by': created_users['doctor_rajesh'],
                    'assessment_date': timezone.now() - timedelta(days=2),
                    'weight_kg': 72.5, 'hemoglobin_g_dl': 14.2, 'systolic_bp': 122, 'diastolic_bp': 80, 'pulse_bpm': 74, 'temperature_c': 36.6,
                    'deferral_type': 'NONE', 'medical_notes': 'Donor in excellent physical condition. Cleared for whole blood donation.'
                }
            )

            ea_deferred, _ = EligibilityAssessment.objects.get_or_create(
                donor=donor_deferred,
                status='TEMPORARILY_DEFERRED',
                defaults={
                    'assessed_by': created_users['doctor_rajesh'],
                    'assessment_date': timezone.now() - timedelta(days=10),
                    'weight_kg': 68.0, 'hemoglobin_g_dl': 11.2, 'systolic_bp': 118, 'diastolic_bp': 76, 'pulse_bpm': 78, 'temperature_c': 36.5,
                    'deferral_type': 'LOW_HEMOGLOBIN', 'deferral_reason': 'Hemoglobin 11.2 g/dL is below required 12.5 g/dL threshold.',
                    'deferral_start_date': timezone.now().date() - timedelta(days=10),
                    'deferral_end_date': timezone.now().date() + timedelta(days=80),
                    'medical_notes': 'Prescribed oral iron supplements. Advised nutritional follow-up after 90 days.'
                }
            )

            # 8. Blood Donation Camps
            camp_metro, _ = BloodCamp.objects.get_or_create(
                camp_id='CMP-2026-000001',
                defaults={
                    'name': 'Corporate LifeLine Blood Drive - CyberCity Tech Park',
                    'organizer_name': 'Tech Mahindra CSR Foundation',
                    'organizer_phone': '+91-98711-55667',
                    'organizer_email': 'csr@cybercity.org',
                    'venue': 'Tech Park Main Atrium, Sector 24',
                    'address': 'CyberCity Phase 2, DLF Hub',
                    'city': 'Gurugram', 'district': 'Gurugram', 'state': 'Haryana',
                    'start_date': timezone.now().date() + timedelta(days=5),
                    'end_date': timezone.now().date() + timedelta(days=5),
                    'start_time': '09:30:00', 'end_time': '17:00:00',
                    'coordinator': created_users['recep_meena'],
                    'blood_bank': bank,
                    'expected_donors': 120,
                    'actual_donors': 0,
                    'status': 'PLANNED',
                    'notes': 'Complete mobile refrigeration and 4 donor phlebotomy couches requested.'
                }
            )
            CampRegistration.objects.get_or_create(camp=camp_metro, donor=donor_rahul)

            # 9. Appointments
            appt_rahul, _ = Appointment.objects.get_or_create(
                appointment_id='APT-2026-000001',
                defaults={
                    'donor': donor_rahul, 'blood_bank': bank, 'appointment_type': 'BLOOD_BANK',
                    'scheduled_date': timezone.now().date() - timedelta(days=2),
                    'time_slot': '10:00 - 11:00 AM',
                    'status': 'COMPLETED',
                    'checked_in_at': timezone.now() - timedelta(days=2, hours=2),
                    'completed_at': timezone.now() - timedelta(days=2, hours=1),
                }
            )

            appt_upcoming, _ = Appointment.objects.get_or_create(
                appointment_id='APT-2026-000002',
                defaults={
                    'donor': donor_kavita, 'blood_bank': bank, 'appointment_type': 'BLOOD_BANK',
                    'scheduled_date': timezone.now().date() + timedelta(days=1),
                    'time_slot': '11:00 - 12:00 PM',
                    'status': 'SCHEDULED',
                }
            )

            # 10. Donations
            don_rahul, _ = Donation.objects.get_or_create(
                donation_id='DON-2026-000001',
                defaults={
                    'donor': donor_rahul, 'appointment': appt_rahul, 'blood_bank': bank, 'assessment': ea_rahul,
                    'collection_date': timezone.now() - timedelta(days=2, hours=1),
                    'donation_type': 'WHOLE_BLOOD', 'bag_type': 'TRIPLE_450ML', 'volume_ml': 450,
                    'collected_by': created_users['tech_arun'], 'vein_used': 'LEFT_ARM',
                    'status': 'COMPLETED',
                    'notes': 'Smooth collection without adverse reactions.'
                }
            )

            don_amit, _ = Donation.objects.get_or_create(
                donation_id='DON-2026-000002',
                defaults={
                    'donor': donor_amit, 'blood_bank': bank,
                    'collection_date': timezone.now() - timedelta(days=5),
                    'donation_type': 'WHOLE_BLOOD', 'bag_type': 'TRIPLE_450ML', 'volume_ml': 450,
                    'collected_by': created_users['tech_arun'], 'vein_used': 'RIGHT_ARM',
                    'status': 'COMPLETED',
                }
            )

            # 11. Blood Bags
            bag_rahul, _ = BloodBag.objects.get_or_create(
                bag_id='BB-2026-000001',
                defaults={
                    'donation': don_rahul, 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'collection_date': don_rahul.collection_date,
                    'expiry_date': don_rahul.collection_date + timedelta(days=35),
                    'bag_type': 'TRIPLE_450ML', 'volume_ml': 450,
                    'status': 'TESTED_SAFE', 'storage_location': 'Cold Vault #1 (2-6C)'
                }
            )

            bag_amit, _ = BloodBag.objects.get_or_create(
                bag_id='BB-2026-000002',
                defaults={
                    'donation': don_amit, 'blood_group': 'AB-', 'rh_factor': 'NEGATIVE',
                    'collection_date': don_amit.collection_date,
                    'expiry_date': don_amit.collection_date + timedelta(days=35),
                    'bag_type': 'TRIPLE_450ML', 'volume_ml': 450,
                    'status': 'TESTED_SAFE', 'storage_location': 'Cold Vault #1 (2-6C)'
                }
            )

            # 12. Lab Samples & Screening Results
            sample_rahul, _ = LabSample.objects.get_or_create(
                sample_id='SMP-2026-000001',
                defaults={
                    'blood_bag': bag_rahul, 'collected_at': bag_rahul.collection_date,
                    'collected_by': created_users['tech_arun'],
                    'status': 'VERIFIED', 'verified_by': created_users['doctor_rajesh'],
                    'verified_at': timezone.now() - timedelta(days=1),
                    'notes': 'All serological and NAT screenings non-reactive. Verified safe.'
                }
            )

            sample_tests = [
                ('ABO_RH_CONFIRMATION', 'Tube Hemagglutination ABO/Rh Test', 'NON_REACTIVE', 'Confirmed O Rh Positive'),
                ('HIV_1_2_ANTIBODY', 'HIV-1/2 4th Gen Ag/Ab CMIA', 'NON_REACTIVE', 'S/CO 0.08 (Cutoff >= 1.00)'),
                ('HBSAG_HEPATITIS_B', 'HBsAg Chemiluminescence Immunoassay', 'NON_REACTIVE', 'S/CO 0.12 (Cutoff >= 1.00)'),
                ('HCV_ANTIBODY_HEPATITIS_C', 'Anti-HCV Enzyme Immunoassay', 'NON_REACTIVE', 'S/CO 0.14 (Cutoff >= 1.00)'),
                ('SYPHILIS_VDRL_TPHA', 'TPHA Treponemal Rapid Assay', 'NON_REACTIVE', 'Non-Reactive'),
                ('MALARIA_ANTIGEN', 'Rapid Diagnostic Test Pf/Pv Antigen', 'NON_REACTIVE', 'Negative for Plasmodium antigen'),
            ]

            for cat, tname, res, val in sample_tests:
                ScreeningResult.objects.get_or_create(
                    sample=sample_rahul, test_category=cat,
                    defaults={
                        'test_name': tname, 'result': res, 'tested_by': created_users['tech_priya'],
                        'test_date': timezone.now() - timedelta(days=1, hours=4),
                        'kit_lot_number': 'LOT-2026-CMIA-981',
                        'quantitative_value': val
                    }
                )

            # 13. Blood Components
            comp_prbc_rahul, _ = BloodComponent.objects.get_or_create(
                component_id='CMPNT-2026-000001',
                defaults={
                    'parent_bag': bag_rahul, 'component_type': 'PRBC', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'prepared_date': timezone.now() - timedelta(days=1),
                    'expiry_date': timezone.now() + timedelta(days=40),
                    'volume_ml': 260, 'prepared_by': created_users['tech_arun'], 'status': 'AVAILABLE',
                    'storage_location': 'PRBC Refrigerator Alpha - Rack A / Shelf 1'
                }
            )

            comp_ffp_rahul, _ = BloodComponent.objects.get_or_create(
                component_id='CMPNT-2026-000002',
                defaults={
                    'parent_bag': bag_rahul, 'component_type': 'FFP', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'prepared_date': timezone.now() - timedelta(days=1),
                    'expiry_date': timezone.now() + timedelta(days=364),
                    'volume_ml': 180, 'prepared_by': created_users['tech_arun'], 'status': 'AVAILABLE',
                    'storage_location': 'Deep Plasma Freezer Beta - Rack B / Shelf 1'
                }
            )

            comp_plt_rahul, _ = BloodComponent.objects.get_or_create(
                component_id='CMPNT-2026-000003',
                defaults={
                    'parent_bag': bag_rahul, 'component_type': 'PLATELET', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'prepared_date': timezone.now() - timedelta(days=1),
                    'expiry_date': timezone.now() + timedelta(days=4),
                    'volume_ml': 55, 'prepared_by': created_users['tech_arun'], 'status': 'AVAILABLE',
                    'storage_location': 'Platelet Agitator Gamma - Tray 1'
                }
            )

            comp_prbc_amit, _ = BloodComponent.objects.get_or_create(
                component_id='CMPNT-2026-000004',
                defaults={
                    'parent_bag': bag_amit, 'component_type': 'PRBC', 'blood_group': 'AB-', 'rh_factor': 'NEGATIVE',
                    'prepared_date': timezone.now() - timedelta(days=4),
                    'expiry_date': timezone.now() + timedelta(days=38),
                    'volume_ml': 255, 'prepared_by': created_users['tech_arun'], 'status': 'AVAILABLE',
                    'storage_location': 'PRBC Refrigerator Alpha - Rack A / Shelf 2'
                }
            )

            # 14. Inventory Items
            inv_prbc_rahul, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000001',
                defaults={
                    'component': comp_prbc_rahul, 'item_type': 'COMPONENT', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'component_type': 'PRBC', 'volume_ml': 260, 'collection_date': bag_rahul.collection_date,
                    'expiry_date': comp_prbc_rahul.expiry_date, 'status': 'AVAILABLE'
                }
            )

            inv_ffp_rahul, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000002',
                defaults={
                    'component': comp_ffp_rahul, 'item_type': 'COMPONENT', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'component_type': 'FFP', 'volume_ml': 180, 'collection_date': bag_rahul.collection_date,
                    'expiry_date': comp_ffp_rahul.expiry_date, 'status': 'AVAILABLE'
                }
            )

            inv_plt_rahul, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000003',
                defaults={
                    'component': comp_plt_rahul, 'item_type': 'COMPONENT', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'component_type': 'PLATELET', 'volume_ml': 55, 'collection_date': bag_rahul.collection_date,
                    'expiry_date': comp_plt_rahul.expiry_date, 'status': 'AVAILABLE'
                }
            )

            inv_prbc_amit, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000004',
                defaults={
                    'component': comp_prbc_amit, 'item_type': 'COMPONENT', 'blood_group': 'AB-', 'rh_factor': 'NEGATIVE',
                    'component_type': 'PRBC', 'volume_ml': 255, 'collection_date': bag_amit.collection_date,
                    'expiry_date': comp_prbc_amit.expiry_date, 'status': 'AVAILABLE'
                }
            )

            inv_quarantined, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000005',
                defaults={
                    'item_type': 'COMPONENT', 'blood_group': 'B+', 'rh_factor': 'POSITIVE',
                    'component_type': 'PRBC', 'volume_ml': 250, 'collection_date': timezone.now() - timedelta(days=2),
                    'expiry_date': timezone.now() + timedelta(days=40), 'status': 'QUARANTINED'
                }
            )
            QuarantineRecord.objects.get_or_create(
                quarantine_id='QRN-2026-000001',
                inventory_item=inv_quarantined,
                defaults={
                    'reason': 'TEMPERATURE_EXCURSION',
                    'quarantined_by': created_users['tech_arun'],
                    'notes': 'Refrigerator door left ajar for 35 mins; temp reached 8.2C. Investigation pending.'
                }
            )

            inv_expired, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000006',
                defaults={
                    'item_type': 'COMPONENT', 'blood_group': 'A-', 'rh_factor': 'NEGATIVE',
                    'component_type': 'PLATELET', 'volume_ml': 50, 'collection_date': timezone.now() - timedelta(days=10),
                    'expiry_date': timezone.now() - timedelta(days=2), 'status': 'EXPIRED'
                }
            )

            inv_discarded, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000007',
                defaults={
                    'item_type': 'COMPONENT', 'blood_group': 'B-', 'rh_factor': 'NEGATIVE',
                    'component_type': 'PRBC', 'volume_ml': 240, 'collection_date': timezone.now() - timedelta(days=60),
                    'expiry_date': timezone.now() - timedelta(days=15), 'status': 'DISCARDED'
                }
            )
            DiscardRecord.objects.get_or_create(
                discard_id='DIS-2026-000001',
                inventory_item=inv_discarded,
                defaults={
                    'discard_reason': 'EXPIRED',
                    'reason_details': 'Unit exceeded 42 days maximum shelf life in cold storage.',
                    'discarded_by': created_users['tech_arun'],
                    'authorized_by': created_users['doctor_rajesh'],
                    'biohazard_disposal_method': 'AUTOCLAVING_INCINERATION',
                    'disposal_manifest_number': 'BIO-DISP-2026-401'
                }
            )

            # Extra units
            groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
            for idx, grp in enumerate(groups, start=8):
                rh = 'POSITIVE' if '+' in grp else 'NEGATIVE'
                InventoryItem.objects.get_or_create(
                    inventory_id=f'INV-2026-0000{idx:02d}',
                    defaults={
                        'item_type': 'COMPONENT', 'blood_group': grp, 'rh_factor': rh,
                        'component_type': 'PRBC', 'volume_ml': 250, 'collection_date': timezone.now() - timedelta(days=3),
                        'expiry_date': timezone.now() + timedelta(days=39), 'status': 'AVAILABLE'
                    }
                )

            # 15. Blood Requests, Reservations & Issues
            req_ananya, _ = BloodRequest.objects.get_or_create(
                request_id='REQ-2026-000001',
                defaults={
                    'hospital': hosp_metro, 'patient': pat_ananya, 'blood_bank': bank,
                    'requesting_doctor': 'Dr. Sanjay Mehta', 'requested_by_user': created_users['hospital_user'],
                    'urgency': 'URGENT', 'required_date_time': timezone.now() + timedelta(hours=3),
                    'clinical_diagnosis': 'Post-chemotherapy severe bone marrow suppression Hb 6.4 g/dL',
                    'transfusion_indication': 'Packed red blood cell support to maintain hematocrit above 25%',
                    'special_requirements': 'Leukoreduced, Crossmatched Compatible',
                    'status': 'APPROVED', 'reviewed_by': created_users['doctor_rajesh'],
                    'review_timestamp': timezone.now() - timedelta(hours=1)
                }
            )
            req_item_ananya, _ = BloodRequestItem.objects.get_or_create(
                request=req_ananya, component_type='PRBC', blood_group='O+',
                defaults={'units_requested': 1, 'units_reserved': 0, 'units_issued': 0, 'status': 'PENDING'}
            )

            req_emergency, _ = BloodRequest.objects.get_or_create(
                request_id='REQ-2026-000002',
                defaults={
                    'hospital': hosp_city, 'patient': pat_rohit, 'blood_bank': bank,
                    'requesting_doctor': 'Dr. Sunita Rao', 'requested_by_user': created_users['hospital_user'],
                    'urgency': 'EMERGENCY', 'required_date_time': timezone.now() + timedelta(hours=1),
                    'clinical_diagnosis': 'Blunt abdominal trauma, splenic rupture, hemorrhagic shock Grade IV',
                    'transfusion_indication': 'Massive transfusion protocol initiated',
                    'special_requirements': 'STAT uncrossmatched or emergency crossmatched PRBC',
                    'status': 'SUBMITTED'
                }
            )
            BloodRequestItem.objects.get_or_create(
                request=req_emergency, component_type='PRBC', blood_group='AB-',
                defaults={'units_requested': 2, 'units_reserved': 0, 'status': 'PENDING'}
            )

            req_past, _ = BloodRequest.objects.get_or_create(
                request_id='REQ-2026-000003',
                defaults={
                    'hospital': hosp_metro, 'patient': pat_ananya, 'blood_bank': bank,
                    'requesting_doctor': 'Dr. Sanjay Mehta', 'requested_by_user': created_users['hospital_user'],
                    'urgency': 'NORMAL', 'required_date_time': timezone.now() - timedelta(days=10),
                    'clinical_diagnosis': 'Chronic anemia', 'status': 'ISSUED'
                }
            )
            req_item_past, _ = BloodRequestItem.objects.get_or_create(
                request=req_past, component_type='FFP', blood_group='O+',
                defaults={'units_requested': 1, 'units_reserved': 1, 'units_issued': 1, 'status': 'ISSUED'}
            )

            inv_issued_unit, _ = InventoryItem.objects.get_or_create(
                inventory_id='INV-2026-000099',
                defaults={
                    'item_type': 'COMPONENT', 'blood_group': 'O+', 'rh_factor': 'POSITIVE',
                    'component_type': 'FFP', 'volume_ml': 180, 'collection_date': timezone.now() - timedelta(days=15),
                    'expiry_date': timezone.now() + timedelta(days=350), 'status': 'ISSUED'
                }
            )

            issue_past, _ = BloodIssue.objects.get_or_create(
                issue_id='ISS-2026-000001',
                defaults={
                    'request': req_past, 'inventory_item': inv_issued_unit, 'patient': pat_ananya,
                    'issued_by': created_users['tech_arun'], 'authorized_by': created_users['doctor_rajesh'],
                    'recipient_name': 'Ramesh Kumar (Metro Hospital Courier)', 'recipient_id_proof': 'BADGE-MTR-904',
                    'issued_at': timezone.now() - timedelta(days=9),
                    'crossmatch_compatible': True, 'status': 'RETURNED'
                }
            )

            BloodReturn.objects.get_or_create(
                return_id='RET-2026-000001',
                blood_issue=issue_past,
                defaults={
                    'returned_by_name': 'Sister Mary (ICU Nurse)',
                    'returned_at': timezone.now() - timedelta(days=8),
                    'received_by': created_users['tech_arun'],
                    'cold_chain_maintained': True, 'visual_inspection_passed': True, 'bag_seal_intact': True,
                    'condition_notes': 'Patient condition stabilized; unit not transfused. Returned in validated cold box at 3.5C.',
                    'assessed_by': created_users['doctor_rajesh'],
                    'disposition': 'RE_ENTRY_APPROVED',
                    'disposition_notes': 'Temperature log inside carrier verified. Seal intact. Unit cleared for re-entry.'
                }
            )

            # 16. Temperature Logs
            TemperatureLog.objects.get_or_create(
                storage_device=dev_prbc,
                timestamp=timezone.now() - timedelta(hours=8),
                defaults={'temperature_celsius': 4.1, 'recorded_by': created_users['tech_arun'], 'threshold_status': 'NORMAL'}
            )
            TemperatureLog.objects.get_or_create(
                storage_device=dev_prbc,
                timestamp=timezone.now() - timedelta(hours=2),
                defaults={'temperature_celsius': 3.9, 'recorded_by': created_users['tech_arun'], 'threshold_status': 'NORMAL'}
            )
            TemperatureLog.objects.get_or_create(
                storage_device=dev_ffp,
                timestamp=timezone.now() - timedelta(hours=4),
                defaults={'temperature_celsius': -41.5, 'recorded_by': created_users['tech_arun'], 'threshold_status': 'NORMAL'}
            )
            TemperatureLog.objects.get_or_create(
                storage_device=dev_plt,
                timestamp=timezone.now() - timedelta(hours=3),
                defaults={'temperature_celsius': 22.2, 'recorded_by': created_users['tech_arun'], 'threshold_status': 'NORMAL'}
            )

            # 17. In-App Notifications
            Notification.objects.get_or_create(
                recipient=created_users['doctor_rajesh'],
                notification_type='EMERGENCY_REQUEST',
                title='STAT Emergency Blood Request: REQ-2026-000002',
                defaults={
                    'message': 'Emergency Trauma OT 2 requested 2x PRBC [AB-] for Patient Rohit Verma. Splenic rupture.',
                    'link_url': f'/requests/{req_emergency.pk}/',
                    'is_read': False
                }
            )
            Notification.objects.get_or_create(
                recipient=created_users['donor_user'],
                notification_type='APPOINTMENT_REMINDER',
                title='Thank you for donating blood with RedLink!',
                defaults={
                    'message': 'Dear Rahul, your donation 2 days ago was successfully tested and separated into life-saving components. You are a hero!',
                    'link_url': '/appointments/',
                    'is_read': True,
                    'read_at': timezone.now()
                }
            )

            # 18. Audit Logs
            AuditLog.objects.get_or_create(
                action='CREATE', model_name='Donation', object_id=str(don_rahul.pk),
                defaults={'object_repr': str(don_rahul), 'user': created_users['tech_arun'], 'reason': 'Completed whole blood collection'}
            )
            AuditLog.objects.get_or_create(
                action='VERIFY', model_name='LabSample', object_id=str(sample_rahul.pk),
                defaults={'object_repr': str(sample_rahul), 'user': created_users['doctor_rajesh'], 'reason': 'Verified serology and released blood bag BB-2026-000001'}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded synthetic demo data across all RedLink models!'))
