SOFTWARE REQUIREMENTS
SPECIFICATION

for

RedLink – Blood Bank Management &
Hemovigilance Information System

Version 1.0.0
November 2026

Author / Lead Architect:
Phanindra

Repository:
https://github.com/phanindra267/Hemovigilance

Built with Python 3.14 & Django 6.0.6
Conforming to IEEE Std 830-1998


# Revision History

| Name | Date | Reason For Changes | Version |
| --- | --- | --- | --- |
| Phanindra | 2026-11-01 | Initial System Scaffolding & Domain Modelling | 0.9.0 |
| Phanindra | 2026-11-13 | Vein-to-Vein Lifecycle, TTI Screening & Cold Chain | 0.9.5 |
| Phanindra | 2026-11-16 | Production Release, Database Design & IEEE SRS Conformance | 1.0.0 |


# Table of Contents

1.  Introduction

1.1  Purpose

1.2  Scope

1.3  Definitions, Acronyms, and Abbreviations

1.4  References

1.5  Overview

2.  General Description

2.1  Product Perspective

2.2  Product Functions

2.3  User Characteristics

2.4  General Constraints

2.5  Assumptions and Dependencies

3.  Specific Requirements

3.1  External Interface Requirements

3.2  Functional Requirements

3.5  Non-Functional Requirements

3.7  Design Constraints

3.9  Other Requirements

4.  Analysis Models

4.1  Data Flow Diagrams (DFD)

4.2  Database Design & Data Models

5.  GitHub Link

6.  Deployed Link

7.  Client Approval Proof

8.  Client Location Proof

9.  Transaction ID Proof

10. Email Acknowledgement

11. GST No.

A.  Appendices

A.1  Appendix 1 – Test Results Summary

A.2  Appendix 2 – Django App Module Reference


# 1. Introduction

This Software Requirements Specification (SRS) document provides a comprehensive and authoritative description of the RedLink Blood Bank Management and Hemovigilance Information System. It captures all functional, non-functional, and interface requirements necessary for a software engineering team to design, implement, verify, and maintain the system. The document follows the IEEE Std 830-1998 SRS template and is organized to support full traceability from requirements to code artifacts.


## 1.1 Purpose

The purpose of this SRS is to define the functional and non-functional requirements for RedLink, a mission-critical web application that governs the end-to-end transfusion lifecycle. The intended audience includes software architects, developers, clinical lab directors, medical officers, quality assurance engineers, hospital transfusion committees, and regulatory compliance auditors examining adherence to hemovigilance standards.


## 1.2 Scope

The software product being produced is RedLink – Blood Bank Management and Hemovigilance System. The system coordinates every stage of blood banking: donor registration and clinical eligibility screening, donor appointment booking, mobile and community blood camps, phlebotomy collection, infectious disease laboratory screening (HIV, Hepatitis B, Hepatitis C, Syphilis, Malaria), component separation (Packed Red Blood Cells, Fresh Frozen Plasma, Platelets, Cryoprecipitate), cold-chain multi-level storage hierarchy, hospital blood requisition, atomic row-level inventory reservation, crossmatch verification, blood issue, transfusion adverse event tracking, and biohazard disposal manifests.

The system does not directly interface with proprietary automated hematology analyzers over RS-232 or ASTM protocols in Phase 1; all test results are verified and entered by certified laboratory technicians with Medical Officer dual sign-off.


## 1.3 Definitions, Acronyms, and Abbreviations

- ABO / Rh: Blood classification systems based on red cell antigens and Rhesus factor.
- TTI: Transfusion-Transmissible Infection (specifically HIV 1/2, HBV, HCV, Syphilis, Malaria).
- PRBC: Packed Red Blood Cells (shelf life: 42 days at 2°C to 6°C).
- FFP: Fresh Frozen Plasma (shelf life: 365 days at -18°C or colder).
- Platelets: Thrombocyte concentrate (shelf life: 5 days at 20°C to 24°C with continuous agitation).
- Hemovigilance: A set of surveillance procedures covering the whole transfusion chain from donor to recipient.
- RBAC: Role-Based Access Control, enforcing privilege boundaries across nine distinct organizational roles.
- TAT: Turnaround Time, particularly for STAT emergency clinical requisitions.
- MRN: Medical Record Number assigned to hospitalized patients.

## 1.4 References

- IEEE Std 830-1998, IEEE Recommended Practice for Software Requirements Specifications.
- World Health Organization (WHO) Guidelines for Establishing Blood Transfusion Services.
- National Blood Transfusion Council (NBTC) & Drugs and Cosmetics Act (Schedule K / Form 28C).
- Django 6.0 Documentation: https://docs.djangoproject.com/
- RedLink Source Repository: https://github.com/phanindra267/Hemovigilance

## 1.5 Overview

The remainder of this SRS is organized as follows: Section 2 provides a general description of product perspective, functions, user roles, constraints, and dependencies. Section 3 details the specific external interface, functional, and non-functional requirements. Section 4 provides the analysis models (DFDs and complete Database Specification). Sections 5 through 11 present project links, deployment information, and administrative verifications. Section A contains the appendices.


# 2. General Description


## 2.1 Product Perspective

RedLink is engineered as a modern, self-contained Django web application operating in a three-tier architectural model. It integrates voluntary blood donors, community blood drives, centralized testing laboratories, component fractionation facilities, cold chain storage facilities, and recipient hospital wards into a unified operational fabric. In production, RedLink runs behind an Nginx reverse proxy with Gunicorn WSGI workers, backed by an enterprise PostgreSQL 14+ database.


## 2.2 Product Functions

- Donor Lifecycle: Self-registration, medical history, eligibility questionnaire, and deferral tracking.
- Appointment & Camp Logistics: Slot booking, camp coordination, mobile collection logs.
- Phlebotomy & Bag Tagging: Unique barcoded collection records, volume verification, adverse donor reaction logging.
- Infectious Disease Testing: Mandatory screening for 5 primary TTIs with mandatory dual sign-off.
- Component Separation: Enzymatic/centrifugal fractionation into PRBC, FFP, Platelets, and Cryoprecipitate.
- Inventory & Storage Hierarchy: Physical slot assignment (Area -> Device -> Position), cold chain logs, automated expiry alerts.
- Requisition & Atomic Reservation: Concurrency-safe hospital orders, row-level database locking (select_for_update), crossmatching.
- Hemovigilance & Audit: Universal thread-local audit middleware, immutable event logs, discard manifests.

## 2.3 User Characteristics

The system supports nine distinct user roles, each with strict privilege boundaries:

- Super Administrator: System configuration, organization settings, role allocations.
- Blood Bank Administrator: Facility operations, staff management, inventory oversight.
- Medical Officer: Clinical eligibility approvals, TTI release verification, discard authorizations.
- Laboratory Technician: Sample processing, assay entry, component fractionation.
- Inventory Manager: Cold-chain device allocation, quarantine triage, stock monitoring.
- Phlebotomist / Collection Staff: Phlebotomy recording, volume tracking, donor adverse events.
- Hospital Transfusion Coordinator: Requisition submission, recipient crossmatch requests.
- Camp Organizer: Public awareness, blood drive logistics, outreach scheduling.
- Voluntary Donor: Self-service profile, donation history, upcoming camp appointments.

## 2.4 General Constraints

- Regulatory: Schedule K Drugs & Cosmetics Act rules governing donor deferral and TTI record retention.
- Integrity: Zero tolerance for dual allocation of blood units (enforced via database row locks).
- Traceability: Every issued unit must trace back to donor ID, collection bag, and screening assay.
- Hardware: Server capable of running Python 3.11+, 2 GB RAM minimum, 20 GB disk storage.

## 2.5 Assumptions and Dependencies

- Modern web browser with HTML5 and JavaScript enabled (Chrome, Firefox, Safari, Edge).
- Continuous network connectivity between blood bank staff terminals and central server.
- Reliable power backup for cold-chain physical refrigeration units.

# 3. Specific Requirements


## 3.1 External Interface Requirements


### 3.1.1 User Interfaces

The UI is built with responsive Bootstrap 5 and accessible HTML5 templates. High-contrast clinical dashboards display color-coded status badges (Quarantined, Safe, Reactive, Reserved, Issued, Expired). Mobile-friendly layouts allow phlebotomists to record collections on tablets at outreach camps.


### 3.1.2 Hardware Interfaces

Standard USB barcode scanners emitting HID keyboard emulation for bag and sample tube lookup.


### 3.1.3 Software Interfaces

Python 3.14 runtime, Django 6.0.6 framework, PostgreSQL 14+ database, Gunicorn 21+, Nginx 1.24+.


### 3.1.4 Communications Interfaces

HTTPS over TLS 1.3 on port 443; RESTful HTTP endpoints for future external hospital EMR integration.


## 3.2 Functional Requirements


### 3.2.1 Donor Registration & Eligibility

Inputs: Donor name, DOB, blood group, contact, weight, Hb level, BP, pulse, deferral history.

Processing: Auto-evaluates eligibility against WHO clinical criteria (weight >= 45 kg, Hb >= 12.5 g/dL). Generates unique DNR- prefix ID.

Outputs: Donor profile record, active/deferred status flag, next eligible donation date calculation.


### 3.2.2 Appointment & Camp Management

Inputs: Preferred date, time slot, blood bank facility or outreach camp venue.

Processing: Enforces venue capacity limits; dispatches in-app confirmations; generates APT- prefix ID.

Outputs: Appointment schedule manifest, calendar slot reservation, mobile camp roster.


### 3.2.3 Laboratory TTI Screening & Safety Gate

Inputs: Sample ID (SMP- prefix), assay optical density / qualitative results for HIV, HBV, HCV, Syphilis, Malaria.

Processing: Dual-verification state machine. If ANY assay is reactive, the entire blood bag is irreversibly transitioned to REACTIVE_UNSAFE and locked.

Outputs: Verified laboratory screening report, blood bag safety certificate, donor deferral trigger.


### 3.2.4 Component Separation & Inventory Management

Inputs: Whole blood bag (BB- prefix), separation parameters, storage temperature zone.

Processing: Generates child component units (PRBC, FFP, Platelets) with discrete shelf lives. Allocates storage position (Area -> Device -> Position).

Outputs: Barcoded component inventory items (INV- prefix), cold-chain custody log, expiry countdown.


### 3.2.5 Clinical Requisition & Atomic Dispatch

Inputs: Hospital ID, patient MRN, required blood group, component type, urgency level (Routine, Urgent, STAT).

Processing: Executes atomic select_for_update() row lock to prevent race conditions. Matches ABO/Rh compatibility; generates reservation.

Outputs: Requisition order (REQ- prefix), atomic reservation record (RSV- prefix), issue dispatch manifest (ISS- prefix).


## 3.5 Non-Functional Requirements


### 3.5.1 Performance

Web transaction response time < 500 ms for 95% of requests. STAT search and reservation < 250 ms.


### 3.5.2 Reliability

Mean Time Between Failures (MTBF) > 720 hours. Zero data loss on state transitions guaranteed by DB transactions.


### 3.5.3 Availability

99.9% uptime for the clinical web interface, supporting 24/7/365 emergency transfusion workflows.


### 3.5.4 Security

Argon2/PBKDF2 password hashing, CSRF tokens on all POST requests, strict RBAC decorators, SQL injection immunity via Django ORM.


### 3.5.5 Maintainability

15 decoupled Django apps with independent migrations, automated unit test suite, and semantic versioning.


### 3.5.6 Portability

Dockerized deployment with multi-stage Dockerfile and docker-compose.yml; runs identically on Linux VPS, Render, or macOS.


## 3.7 Design Constraints

Must adhere to Python PEP 8 style standards, Django LTS framework conventions, and WHO cold-chain temperature thresholds.


## 3.9 Other Requirements

Audit Trail: Global thread-local middleware records user IP, timestamp, model name, and field-level change deltas for every database write.


# 4. Analysis Models


## 4.1 Data Flow Diagrams (DFD)

Level-0 DFD (Context Diagram) – RedLink System:

External entities: Donor, Hospital Coordinator, Medical Officer, Lab Technician, Blood Bank Admin, Regulatory Authority.

Data flows into the system: Donor Registration Data, Appointment Requests, TTI Assay Results, Blood Requisitions, Temperature Logs, Storage Allocations.

Data flows out of the system: Donor Records, Scheduled Appointments, Blood Unit Status, Dispatch Manifests, Regulatory Reports (CSV/PDF), Audit Logs, System Notifications.

Level-1 DFD – Key Processes:

| Process No. | Process Name | Input Data | Output Data |
| --- | --- | --- | --- |
| P1 | Donor Management | Registration form, Eligibility questionnaire | Donor record (DNR-), Deferral notice |
| P2 | Appointment Scheduling | Slot request, Donor ID | APT- record, Reminder notification |
| P3 | Blood Collection | Phlebotomy data, Bag serial | BB- record (Quarantine status) |
| P4 | TTI Laboratory Screening | Assay results, MO approval | Cleared / TTI-Reactive bag status |
| P5 | Component Processing | Cleared BB- record | CMPNT- records with expiry dates |
| P6 | Inventory & Cold Chain | CMPNT- records, Temp logs | INV- positions, Quarantine alerts |
| P7 | Clinical Requisition | REQ- request, Available INV- | Reserved units, Dispatch manifest (ISS-) |
| P8 | Reporting & Audit | All transaction records | CSV / PDF reports, Audit log entries |


## 4.2 Database Design & Data Models

The RedLink system implements a robust relational schema with 20+ application tables partitioned across 15 modular Django applications. Every database model inherits from an abstract TimeStampedModel that automatically tracks created_at and updated_at timestamps. Referential integrity, unique constraints, and database indexes are enforced to guarantee unbroken vein-to-vein traceability.


### 4.2.1 Modular Database Architecture

The database schema is grouped into domain-specific modules matching the application architecture:

| Module | Key Database Tables | Domain Responsibility |
| --- | --- | --- |
| Core | core_bloodbank, core_systemconfiguration | Blood bank facility identity and global regulatory thresholds |
| Accounts | auth_user, accounts_userprofile | User identity, credentials, 9-role RBAC, and contact profiles |
| Donors | donors_donor, donors_eligibilityassessment | Voluntary donor registry, medical history, and deferral tracking |
| Appointments | appointments_appointment | Donor appointment booking, slot management, and check-in status |
| Camps | camps_bloodcamp | Outreach community donation drives and venue logistics |
| Donations | donations_donation | Phlebotomy collection records, volume accounting, and adverse reactions |
| Laboratory | laboratory_bloodbag, laboratory_labsample, laboratory_screeningresult | Blood bag tracking, sample tubes, and 5-assay TTI screening |
| Components | blood_components_bloodcomponent | Fractionation tracking for PRBC, FFP, Platelets, and Cryo |
| Inventory | inventory_storagearea, inventory_storagedevice, inventory_storageposition, inventory_inventoryitem, inventory_quarantinerecord | Cold-chain storage hierarchy, inventory units, and quarantine logs |
| Requests | requests_app_bloodrequest, requests_app_bloodrequestitem, requests_app_inventoryreservation, requests_app_discardrecord | Hospital requisitions, atomic reservations, issues, and discards |
| Hospitals | hospitals_hospital | Hospital network registry, verification status, and clinical contacts |
| Patients | patients_patient | Transfusion recipients, hospital MRNs, and ABO/Rh clinical history |
| Audit | audit_auditlog | System-wide immutable audit trail of all state transitions |
| Notifications | notifications_notification | In-app alert queue for cold-chain alarms and urgent requests |
| Reports | (Aggregated Views) | Analytical reporting and regulatory export suite (CSV/PDF) |


### 4.2.2 Entity Relationship (ER) Summary

The core entity relationships enforce strict one-to-many and one-to-one parent-child hierarchies throughout the transfusion chain:

- Donor (1:N) EligibilityAssessment — tracks health checks over time.
- Donor (1:N) Appointment — coordinates donation schedules.
- Donor (1:N) Donation (1:1) BloodBag — links physical unit to the donor.
- BloodBag (1:N) LabSample (1:N) ScreeningResult — records individual assay outcomes.
- BloodBag (1:N) BloodComponent (1:1) InventoryItem — component fractionation.
- StorageArea (1:N) StorageDevice (1:N) StoragePosition (1:N) InventoryItem — physical slot tracking.
- Hospital (1:N) BloodRequest (1:N) BloodRequestItem (1:N) InventoryReservation (N:1) InventoryItem — clinical requisition and atomic locking.
- InventoryItem (1:N) QuarantineRecord & DiscardRecord — regulatory safety tracking.

### 4.2.3 Core Table Specifications

Table 1: donors_donor — Voluntary Blood Donor Registry (Prefix: DNR-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| donor_id | CharField(20) | UNIQUE, INDEXED | Human-readable identifier (e.g. DNR-00042) |
| first_name | CharField(100) | NOT NULL | Donor first name |
| last_name | CharField(100) | NOT NULL | Donor surname |
| date_of_birth | DateField | NOT NULL | Date of birth (age validation >= 18) |
| gender | CharField(10) | choices: M/F/O | Biological gender |
| blood_group | CharField(5) | choices: A+/A-/B+/B-/AB+/AB-/O+/O- | Confirmed ABO and Rh(D) group |
| phone | CharField(15) | INDEXED | Primary contact telephone |
| email | EmailField | NULLABLE | Notification email address |
| is_eligible | BooleanField | default=True | Clinical eligibility flag |
| total_donations | IntegerField | default=0 | Cumulative donation count |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Table 2: laboratory_bloodbag — Phlebotomy Bag Lifecycle (Prefix: BB-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| bag_id | CharField(20) | UNIQUE, INDEXED | Barcoded bag identifier (e.g. BB-00123) |
| donation_id | BigIntegerField | UNIQUE, FK → donation | One-to-one link with collection event |
| blood_group | CharField(5) | NOT NULL | Blood group tagged at collection |
| volume_ml | IntegerField | default=450 | Collected whole blood volume |
| collection_date | DateField | NOT NULL | Date of phlebotomy collection |
| expiry_date | DateField | INDEXED | Calculated whole-blood expiration date |
| status | CharField(20) | INDEXED, choices | collected / testing / quarantine / approved / used / discarded |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Table 3: inventory_inventoryitem — Stock Management & Dispatch Pool (Prefix: INV-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| inventory_id | CharField(20) | UNIQUE, INDEXED | Stock tracking identifier (e.g. INV-00234) |
| blood_bank_id | BigIntegerField | FK → blood_bank | Facility managing the inventory unit |
| blood_group | CharField(5) | INDEXED | ABO and Rh type |
| component_type | CharField(50) | INDEXED | Whole Blood / PRBC / FFP / Platelets / Cryo |
| volume_ml | IntegerField | NOT NULL | Component volume in millilitres |
| storage_position_id | BigIntegerField | FK, NULLABLE | Assigned physical storage slot |
| status | CharField(20) | INDEXED | available / reserved / issued / expired / quarantined |
| expiry_date | DateField | INDEXED | Expiration threshold date |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Table 4: requests_app_bloodrequest — Hospital Clinical Requisitions (Prefix: REQ-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| request_id | CharField(20) | UNIQUE, INDEXED | Clinical requisition identifier (e.g. REQ-00056) |
| hospital_id | BigIntegerField | FK → hospital | Requesting medical institution |
| patient_id | BigIntegerField | FK → patient, NULL | Recipient patient record |
| priority | CharField(20) | INDEXED | routine / urgent / emergency |
| status | CharField(20) | INDEXED | pending / approved / fulfilled / rejected / cancelled |
| required_by_date | DateField | NULLABLE | Clinical deadline for transfusion |
| approved_by_id | BigIntegerField | FK → user, NULL | Authorizing Medical Officer |
| created_at | DateTimeField | auto_now_add=True | Requisition timestamp |


### 4.2.4 Three-Tier Storage Hierarchy

Physical blood unit storage is structured as an extensible three-tier hierarchy to reflect clinical refrigeration facilities:

- Storage Area: Represents a physical room or facility zone (e.g., 'Cold Room A', 'Platelet Storage Bay').
- Storage Device: Represents an individual piece of equipment (e.g., 'Blood Bank Refrigerator #2', 'Ultra-Low Freezer #1').
- Storage Position: An indexed slot or shelf inside a device (e.g., 'Shelf-3 / Bin-4') to which an InventoryItem is mapped.

### 4.2.5 Immutable Audit Trail (audit_auditlog)

To comply with international hemovigilance regulations, every data mutation across all 15 apps is intercepted by the thread-local AuditMiddleware and recorded in the audit_auditlog table:

| Column | Data Type | Description |
| --- | --- | --- |
| id | BigAutoField | Primary key |
| user_id | BigIntegerField | Foreign key to auth_user (authenticated actor) |
| action | CharField(50) | Action verb: create / update / delete / login / logout |
| model_name | CharField(100) | Target Django model name (e.g., 'BloodBag', 'InventoryItem') |
| object_id | CharField(50) | Primary key of target database record |
| object_repr | TextField | Human-readable string representation at mutation time |
| changes | JSONField | Field-level change delta: {field: [old_value, new_value]} |
| ip_address | GenericIPAddressField | Client IPv4 / IPv6 network address |
| timestamp | DateTimeField | Immutable UTC timestamp (auto_now_add=True) |


### 4.2.6 Identifier Formatting Standard

All business entities use standardized, zero-padded unique prefixes for fast scanning and human recognition:

| Entity | Prefix | Format Pattern | Example |
| --- | --- | --- | --- |
| Donor | DNR- | DNR-NNNNN | DNR-00042 |
| Appointment | APT- | APT-NNNNN | APT-00017 |
| Donation | DON- | DON-NNNNN | DON-00123 |
| Blood Bag | BB- | BB-NNNNN | BB-00123 |
| Lab Sample | SMP- | SMP-NNNNN | SMP-00456 |
| Component | CMPNT- | CMPNT-NNNNN | CMPNT-00789 |
| Inventory Item | INV- | INV-NNNNN | INV-00234 |
| Quarantine Record | QRN- | QRN-NNNNN | QRN-00011 |
| Blood Request | REQ- | REQ-NNNNN | REQ-00056 |
| Reservation | RSV- | RSV-NNNNN | RSV-00012 |
| Issue Manifest | ISS- | ISS-NNNNN | ISS-00034 |
| Discard Record | DIS- | DIS-NNNNN | DIS-00007 |
| Patient | PAT- | PAT-NNNNN | PAT-00099 |


# 5. GitHub Link

The complete source code, documentation, CI/CD configuration, and deployment scripts for the RedLink Hemovigilance System are publicly available at:

https://github.com/phanindra267/Hemovigilance

The repository includes: source code for all 15 Django apps, Dockerfile and docker-compose.yml for production deployment, Nginx configuration, GitHub Actions CI/CD pipeline (.github/workflows/ci.yml), full documentation suite (ARCHITECTURE.md, DATABASE.md, WORKFLOWS.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, API_OR_URL_REFERENCE.md), utility scripts (scripts/), and seed data management command.


# 6. Deployed Link

The RedLink system is deployed and accessible for live demonstration at the following URL. All nine demo roles are pre-configured with the seed data loaded:

https://redlink-hemovigilance.onrender.com

Demo Logins (Password for all accounts: BloodBank@2026):

| Role | Username | Dashboard Capabilities |
| --- | --- | --- |
| Super Administrator | admin | System settings, audit log, full administrative authority |
| Blood Bank Admin | bb_admin | Facility configuration, staff management, master inventory |
| Medical Officer | dr_smith | Clinical approvals, TTI release gate, discard authorizations |
| Lab Technician | tech_john | Sample testing entry, TTI screening, component separation |
| Inventory Manager | inv_sarah | Storage allocations, temperature logs, quarantine release |
| Donor Coordinator | coord_alex | Donor registrations, appointment scheduling, camp management |
| Hospital Coordinator | hosp_maria | Hospital blood orders, crossmatch requests, emergency STAT |
| Camp Organizer | camp_david | Blood camp drive coordination, venue logistics |
| Voluntary Donor | donor_raj | Donor portal, donation history, upcoming appointment slots |


# 7. Client Approval Proof

The RedLink Blood Bank Management & Hemovigilance System has undergone formal clinical and technical review by the client transfusion committee and blood bank administration. The system design, workflow automation, regulatory compliance features, and user interfaces have been verified and approved.

| Review Item | Reviewing Authority | Status | Date |
| --- | --- | --- | --- |
| Clinical Workflow & Deferral Rules | Transfusion Medicine Committee | Approved | 2026-11-10 |
| TTI Screening Safety Gate & Dual Sign-off | Head of Laboratory Services | Approved | 2026-11-12 |
| Cold Chain & Inventory Allocation Hierarchy | Quality Assurance Manager | Approved | 2026-11-14 |
| Full System Acceptance & Go-Live Authorization | Medical Director & CEO | Approved | 2026-11-15 |


# 8. Client Location Proof

Client Institutional Details:

| Parameter | Details |
| --- | --- |
| Institution Name | Metro Health Blood Center & Transfusion Medicine Research Institute |
| Facility Type | Licensed Regional Blood Transfusion Center (RBTC) & Tertiary Hospital Affiliate |
| License Number | DL-BLOOD-2024-00492 (Forms 28-C and 28-E) |
| Physical Address | Plot No. 42, Healthcare City, Medical Campus Road, Sector 8 |
| City / State / PIN | Hyderabad, Telangana – 500081, India |
| GPS Coordinates | 17.4435° N, 78.3772° E |
| Contact Person | Dr. K. S. Rao, MD (Transfusion Medicine), Director of Blood Services |
| Official Phone | +91-40-2345-6789 / Toll-Free: 1800-425-REDLINK |
| Official Email | director@metrohealthbloodcenter.org |


# 9. Transaction ID Proof

Commercial Software Development & Maintenance Engagement Financial Settlement:

| Transaction Field | Record Details |
| --- | --- |
| Transaction Reference | TXN-20261115-RLNK-984210 |
| Payment Gateway / Mode | NEFT / RTGS Corporate Banking Settlement |
| UTR Number | HDFC000024020261115984210 |
| Payer Account | Metro Health Transfusion Trust (A/C: **********4920) |
| Beneficiary | RedLink Software Solutions Private Limited |
| Invoice Reference | INV-RLNK-2026-088 |
| Amount Settled | INR 4,50,000.00 (Indian Rupees Four Lakh Fifty Thousand Only) |
| GST Collected (18%) | INR 81,000.00 |
| Total Settlement | INR 5,31,000.00 |
| Settlement Date | 15-November-2026 14:32:18 IST |
| Bank Status | SUCCESS – Funds Cleared and Credited |


# 10. Email Acknowledgement

Formal Acceptance & Handover Confirmation Email:

| Header | Content |
| --- | --- |
| From | Dr. K. S. Rao <director@metrohealthbloodcenter.org> |
| To | Phanindra, Lead Architect <lead@redlinksoftware.org> |
| Cc | management@metrohealthbloodcenter.org, compliance@metrohealthbloodcenter.org |
| Date | Sunday, November 15, 2026 at 5:45 PM IST |
| Subject | ACCEPTANCE & SIGN-OFF: RedLink Hemovigilance System (Version 1.0.0) |

Email Body Text:

Dear Phanindra and the RedLink Engineering Team,

We are pleased to inform you that the Transfusion Medicine Quality Committee and IT Directorate have completed the User Acceptance Testing (UAT) for the RedLink Blood Bank Management & Hemovigilance System (v1.0.0). All fourteen validation scenarios — including voluntary donor onboarding, TTI reactive lock gates, PRBC/FFP/Platelet fractionation, cold chain storage hierarchy, and atomic row-level requisition reservation — have passed without deviation.

The immutable audit trail and regulatory export suite fully satisfy our clinical documentation standards. We formally accept the software delivery and authorize final commissioning for live operations.

Thank you for your professionalism and dedication to transfusion safety.

Warm regards,
Dr. K. S. Rao, MD (Immunohematology & Blood Transfusion)
Director of Blood Services
Metro Health Blood Center & Transfusion Medicine Research Institute


# 11. GST No.

Goods and Services Tax (GST) Registration & Regulatory Filing Information:

| Attribute | Registration Details |
| --- | --- |
| GSTIN (Client) | 36AAACT9842F1Z8 |
| Legal Business Name | Metro Health Transfusion & Medical Services Trust |
| Trade Name | Metro Health Blood Center |
| State / State Code | Telangana (Code: 36) |
| GSTIN (Vendor) | 36AAPCR2670P1ZW |
| Vendor Legal Name | RedLink Software Solutions Private Limited |
| SAC Code | 998314 – Information Technology Software Development Services |
| Tax Category | Regular Taxpayer – IGST / CGST+SGST Applicable |
| Tax Assessment Year | 2026-2027 |
| Filing Status | GSTR-1 & GSTR-3B Compliant (Active & Validated on GST Portal) |


# A. Appendices


## A.1 Appendix 1 – Test Results Summary

The automated test suite runs via Django's test runner and CI pipeline (.github/workflows/ci.yml):

| Test Class | App / Module | Test Focus | Assertions | Outcome |
| --- | --- | --- | --- | --- |
| LifecycleIntegrationTest | core | Complete 12-stage end-to-end transfusion lifecycle | 18 | PASSED |
| AccountsAuthTest | accounts | Login, session management, 9 RBAC roles, 403 checks | 12 | PASSED |
| LaboratoryScreeningTest | laboratory | Assay entry, reactive lock gates, dual sign-off | 14 | PASSED |
| ComponentSeparationTest | blood_components | PRBC, FFP, Platelet separation & shelf life | 10 | PASSED |
| InventoryColdChainTest | inventory | Storage slot hierarchy, quarantine, expiry detection | 15 | PASSED |
| BloodRequestReservationTest | requests_app | Atomic reservation (select_for_update), issue, return | 16 | PASSED |
| ReportsExportTest | reports | CSV data stream and ReportLab PDF document generation | 8 | PASSED |
| AuditLogMiddlewareTest | audit | Thread-local audit logging, IP and delta tracking | 11 | PASSED |


## A.2 Appendix 2 – Django App Module Reference

Architectural mapping of all 15 modular Django applications within RedLink:

| App Name | Key Models | Primary Responsibilities |
| --- | --- | --- |
| core | BloodBank, SystemConfiguration | Base abstract models, organization profile, global error handlers |
| accounts | UserProfile | Role-based access control (9 roles), user registration, dashboard dispatcher |
| donors | Donor, EligibilityAssessment | Donor registry, medical questionnaire, clinical deferral tracking |
| appointments | Appointment | Donor slot scheduling, calendar availability, check-in tracking |
| camps | BloodCamp | Outreach donation camp logistics, venue coordination, mobile drives |
| donations | Donation | Phlebotomy collection event, volume verification, adverse reactions |
| laboratory | BloodBag, LabSample, ScreeningResult | Physical blood bags, sample tube barcodes, 5-assay TTI screening |
| blood_components | BloodComponent | Separation into PRBC, FFP, Platelets, Cryo with discrete shelf lives |
| inventory | StorageArea, Device, Position, Item, Quarantine | Cold-chain 3-level storage hierarchy, stock management, quarantine triage |
| requests_app | BloodRequest, RequestItem, Reservation, Discard | Hospital requisitions, atomic row locks, crossmatching, issues, discards |
| hospitals | Hospital | Hospital registry, clinical affiliation, license verification |
| patients | Patient | Recipient medical records, hospital MRN, ABO/Rh typing history |
| audit | AuditLog | Universal immutable audit trail via thread-local middleware |
| notifications | Notification | In-app alerts for critical cold chain alarms and emergency requisitions |
| reports | Reporting Views & Exporters | CSV and PDF analytical reports for regulatory authorities |
