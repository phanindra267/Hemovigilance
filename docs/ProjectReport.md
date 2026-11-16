RedLink – Blood Bank Management & Hemovigilance System

Software Requirements Specification

CS / IT / Software Engineering – Capstone Project

Course Code: CSE-499 / CS6080

Course Name: Software Engineering & Capstone Project

Student Names:

Phanindra Reddy G.

Prepared for

Continuous Assessment 3

Spring 2025


# Revision History

| Date | Description | Author | Comments |
| --- | --- | --- | --- |
| 2025-01-15 | Initial Draft – system scope & architecture | Phanindra Reddy G. | v0.1 |
| 2025-02-01 | Requirements baseline – functional & non-functional | Phanindra Reddy G. | v0.5 |
| 2025-03-10 | Final review – test results, DFD, GitHub link added | Phanindra Reddy G. | v1.0 |

Table of Contents

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

5.  GitHub Link

6.  Deployed Link

7.  Client Approval Proof

8.  Client Location Proof

9.  Transaction ID Proof

10. Email Acknowledgement

11. GST No.

A.  Appendices


# 1. Introduction

This Software Requirements Specification (SRS) document provides a comprehensive and authoritative description of the RedLink Blood Bank Management and Hemovigilance Information System. It captures all functional, non-functional, and interface requirements necessary for a software engineering team to design, implement, verify, and maintain the system. The document follows the IEEE Std 830-1998 SRS template and is organized to serve project stakeholders including developers, testers, clinical users, and academic evaluators.


## 1.1 Purpose

The purpose of this SRS is to define the complete set of requirements for RedLink – an enterprise-grade Blood Bank Management and Hemovigilance Information System. The intended audience includes software developers responsible for implementation, quality assurance engineers conducting verification, clinical domain experts validating medical workflow correctness, and academic evaluators assessing the capstone project deliverable.


## 1.2 Scope

RedLink is a web-based clinical information system designed for regional transfusion centres, hospital blood banks, and healthcare regulatory authorities. The system:

- Manages the full vein-to-vein lifecycle of a blood unit across 12 traceable stages, from donor registration through component separation, cold-chain storage, clinical requisition, crossmatch dispatch, and transfusion surveillance or biohazard discard.
- Enforces a mandatory Medical Officer safety release gate that quarantines every blood bag until all five TTI serological assays (HIV, HBV, HCV, Syphilis, Malaria) are verified non-reactive by an authorised Medical Officer.
- Provides atomic, concurrency-safe inventory reservation using database-level select_for_update() row locking, preventing double-booking during simultaneous emergency requisitions.
- Governs continuous cold-chain monitoring across PRBC refrigerators (+2°C to +6°C), plasma freezers (−40°C), and platelet incubators (+20°C to +24°C), with excursion alarms and automatic quarantine triggers.
- Generates regulatory-grade reports in real-time (CSV and ReportLab PDF) covering inventory ledgers, discard root-cause analytics, donation metrics, and rare-donor registers.
The system does not include direct patient Electronic Health Record (EHR) integration, insurance billing modules, or surgical scheduling; those domains remain with the hospital's primary HIS. RedLink is designed to operate standalone or alongside an HIS via API.


## 1.3 Definitions, Acronyms, and Abbreviations

| Term / Acronym | Definition |
| --- | --- |
| SRS | Software Requirements Specification |
| TTI | Transfusion-Transmitted Infection – mandatory 5-panel serological assays |
| PRBC | Packed Red Blood Cells – primary red cell component product |
| FFP | Fresh Frozen Plasma – coagulation-factor-rich blood component |
| MO | Medical Officer – clinician authorised to approve blood unit release |
| RBAC | Role-Based Access Control – permission model enforcing least-privilege |
| DFD | Data Flow Diagram – graphical model of system data movement |
| CSV | Comma-Separated Values – machine-readable tabular export format |
| PDF | Portable Document Format – report output via ReportLab library |
| BB- | Blood Bag unique identifier prefix (e.g., BB-2025-000001) |
| REQ- | Requisition unique identifier prefix |
| DNR- | Donor unique identifier prefix |
| HIS | Hospital Information System |
| CI/CD | Continuous Integration / Continuous Deployment |
| WSGI | Web Server Gateway Interface – Python web server standard |
| ORM | Object-Relational Mapper – Django's database abstraction layer |


## 1.4 References

The following documents and standards are referenced within this SRS:

- IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications
- Django 6.0 Documentation – https://docs.djangoproject.com/en/6.0/
- WHO Guidelines for Blood Transfusion Services – WHO/EHT/08.07
- CDSCO Blood Bank Regulations, India – Drugs and Cosmetics Act, Schedule F Part XII B
- RedLink GitHub Repository – https://github.com/phanindra267/Hemovigilance
- RedLink ARCHITECTURE.md – Architectural patterns and cold chain schema
- RedLink DATABASE.md – Entity-relationship models and primary key design
- RedLink TESTING.md – Test plan, coverage matrix, and execution logs

## 1.5 Overview

The remainder of this SRS is organized as follows. Section 2 provides a general description of the RedLink product, covering product perspective, core functions, user roles, and constraints. Section 3 details specific functional and non-functional requirements. Section 4 presents analysis models including the Level-0 and Level-1 Data Flow Diagrams. Sections 5 through 11 provide supplementary project artefacts including the GitHub link, deployed system URL, client approval proof, and financial/compliance documentation. Appendix A includes additional supporting materials.


# 2. General Description

This section describes general factors that affect RedLink and its requirements. It does not specify individual requirements; it provides context to make those requirements easier to understand and to verify that they are complete and consistent.


## 2.1 Product Perspective

RedLink is a new, self-contained clinical information system. It does not replace but rather complements existing hospital HIS platforms. It interfaces with the HIS via configurable API endpoints to exchange patient demographics and transfusion records where HIS integration is available. When no HIS is present, RedLink operates entirely standalone.

The system is built on a layered web architecture: (1) a Django 6.0 application server providing the business logic and REST-style views, (2) a PostgreSQL relational database for persistent data storage, (3) a WhiteNoise-served Bootstrap 5 frontend, and (4) a Gunicorn WSGI server behind an Nginx reverse proxy in production. GitHub Actions provides CI/CD pipeline automation with automated test execution on every push.


## 2.2 Product Functions

RedLink provides the following high-level functional capabilities:

| # | Function | Description |
| --- | --- | --- |
| F-01 | Donor Lifecycle Management | Registration, eligibility assessment, deferral tracking, rare blood group flagging, and donation history. |
| F-02 | Appointment & Camp Scheduling | Slot-limited appointment booking, walk-in reception, blood donation camp coordination, and self-registration. |
| F-03 | Phlebotomy & Blood Bag Custody | Bag issuance with traceable BB- identifier, volume documentation, adverse reaction recording. |
| F-04 | Laboratory TTI Screening | 5-panel viral assays with individual result entry, batch processing, Medical Officer review gate, and quarantine management. |
| F-05 | Component Separation | PRBC, FFP, Platelets, and Cryoprecipitate yield documentation with component-specific shelf-life enforcement. |
| F-06 | Cold Chain Inventory | Storage hierarchy management (Area → Device → Shelf → Slot), continuous temperature logging, excursion alarms, automatic quarantine. |
| F-07 | Clinical Requisition & Issue | Hospital blood orders with urgency triage (Routine / Urgent / STAT), atomic reservation locking, crossmatch verification, and dispatch manifests. |
| F-08 | Return & Discard Management | Unit return processing with chain-of-custody documentation; root-cause discard cataloguing (expired, contaminated, damaged, TTI-reactive). |
| F-09 | Regulatory Reporting | Live stock ledgers, donation reports, discard analytics, rare-donor registers, and monthly blood bank summaries in CSV and PDF. |
| F-10 | Notifications & Alerts | Real-time system notification drawer: expiry alerts, low-stock alarms, pending requisition notifications, urgent screening reminders. |
| F-11 | Audit Logging | Immutable per-request log capturing authenticated user, IP address, affected entity, action type, and timestamp. |
| F-12 | Role-Based Access Control | 9 granular role profiles with dedicated dashboards; all views protected by @role_required decorator and Django session authentication. |


## 2.3 User Characteristics

RedLink serves nine distinct user roles with different technical expertise and access scopes:

| Role | Technical Level | Primary Activities |
| --- | --- | --- |
| Super Administrator | High – IT staff | Global system administration, user management, role assignment, system settings, audit log review. |
| Blood Bank Director / Admin | Medium – clinical manager | Operational oversight, facility metrics, staff management, report export, inventory approval. |
| Medical Officer | Medium – clinician | Lab result verification, TTI safety release gate, clinical requisition review, donor eligibility assessments. |
| Laboratory Technician | Medium – lab staff | Blood bag processing, TTI assay result entry, component separation, sample management. |
| Inventory Manager / Tech | Medium – technical | Cold storage allocation, temperature monitoring, quarantine resolution, discard documentation. |
| Phlebotomist / Receptionist | Low – front-desk | Donor registration, appointment check-in, donation recording, adverse reaction logging. |
| Hospital Coordinator | Low – clinical administrator | Blood requisition submission, unit tracking, receipt confirmation. |
| Donor (Self-service) | Low – general public | Appointment booking, personal donation history, camp registration. |
| Patient | Low – general public | Transfusion records viewing, hospital assignment. |


## 2.4 General Constraints

The following general constraints govern the design and operation of RedLink:

- Medical Compliance: The system must enforce WHO and CDSCO blood bank regulatory requirements, including mandatory 5-assay TTI screening before unit release.
- Data Integrity: Blood unit identifiers (BB-, DNR-, REQ-, etc.) must be globally unique, immutable once issued, and permanently retained for regulatory audit trails.
- Concurrency Safety: Inventory reservation must be atomic; the system must use database-level locking (select_for_update) to prevent race conditions.
- Security: All routes must be authenticated. Role-based access must be enforced at the view layer. CSRF protection is mandatory for all state-modifying endpoints.
- Deployment: The system must be deployable on a standard Linux server via Docker Compose with Nginx and Gunicorn, and must pass the CI/CD pipeline on GitHub Actions.
- Compatibility: Supported on modern browsers (Chrome, Firefox, Edge, Safari) without requiring browser plugins.

## 2.5 Assumptions and Dependencies

The following assumptions and dependencies apply:

- Python 3.11 or higher is available in the deployment environment.
- PostgreSQL 14+ is used for production; SQLite is acceptable for development and automated testing.
- A valid SMTP server is available for email notifications.
- The deploying institution's network allows HTTPS traffic on port 443.
- Demo seed data via seed_demo_data management command is used for initial staff onboarding and testing.
- Client institutions are responsible for providing valid physical storage device readings for cold chain integration.

# 3. Specific Requirements


## 3.1 External Interface Requirements


### 3.1.1 User Interfaces

The system provides a responsive, clinical-grade web UI built with Bootstrap 5 and Django template rendering. Each user role receives a customized dashboard upon login. Key UI elements include:

- Role-adaptive navigation sidebar and top header with live notification drawer.
- Stat cards displaying real-time counts (available units, pending requisitions, expiring units).
- Data tables with server-side filtering, sorting, and pagination for all entity lists.
- Form-based workflows with inline validation for blood bag registration, lab result entry, and requisition submission.
- One-click demo credentials picker on the login page for evaluator access.

### 3.1.2 Hardware Interfaces

RedLink does not directly interface with hardware devices. Physical temperature sensors and refrigeration units are read by biomedical technicians who manually log readings into the system's temperature monitoring module. Future integration with IoT cold-chain sensors via MQTT or REST API is architecturally planned but not in scope for this release.


### 3.1.3 Software Interfaces

RedLink integrates with or depends on the following software systems:

| Interface | Type | Protocol / Library | Purpose |
| --- | --- | --- | --- |
| PostgreSQL 14+ | Database | psycopg3 (psycopg>=3.1.0) | Primary persistent data store |
| Gunicorn | WSGI Server | HTTP/WSGI | Python application server for production |
| Nginx | Reverse Proxy | HTTP/HTTPS | TLS termination, static file serving |
| SMTP Server | Email | Django EmailBackend / SMTP | System notifications and alerts |
| ReportLab | PDF Library | Python API | Regulatory PDF report generation |
| GitHub Actions | CI/CD | YAML workflows | Automated testing on push/PR |
| Docker Compose | Container Orchestration | Docker CLI | Production deployment automation |


### 3.1.4 Communications Interfaces

All communication between browser clients and the server uses HTTPS (TLS 1.2+) in production. Internal Docker Compose services communicate over a private bridge network. The system does not currently expose a formal REST API for third-party consumption; all data exchange occurs through authenticated Django views returning HTML or downloadable CSV/PDF responses.


## 3.2 Functional Requirements


### 3.2.1 Donor Registration & Eligibility

The system shall:

- Allow authorized staff (Receptionist, Blood Bank Admin) to register new donors with a unique DNR- identifier, capturing full name, date of birth, blood group, Rh factor, contact details, address, and rare blood group flags.
- Record structured eligibility questionnaire responses (haemoglobin level, blood pressure, weight, recent travel, medication history, prior donation dates) and automatically calculate next-eligible donation date.
- Permanently record any deferral with its reason and deferral-end date, preventing scheduling of deferred donors.
- Display a donor's complete donation history, TTI history, and deferral record to authorized clinical staff.

### 3.2.2 Appointment & Camp Management

The system shall:

- Allow donors or reception staff to book appointments in designated time slots, enforcing slot capacity limits to prevent overbooking.
- Support blood donation camp creation with venue, date, coordinator, and target unit goals, with public self-registration for donors.
- Allow reception to check in walk-in donors and generate same-day appointment records.
- Trigger reminder notifications 24 hours before scheduled appointments.

### 3.2.3 Laboratory TTI Screening & Safety Gate

The system shall:

- Assign a unique BB- identifier to each collected blood bag and place it in Quarantine status immediately upon collection.
- Allow Laboratory Technicians to record individual TTI assay results (HIV Ag/Ab, HBsAg, Anti-HCV, Syphilis VDRL/TPHA, Malaria Ag) for each blood bag.
- Prevent any blood bag from leaving Quarantine status unless all five assays have been individually marked Non-Reactive and the record has been digitally approved by an authorized Medical Officer.
- Automatically and permanently mark any bag with one or more Reactive results as TTI-Reactive Discard, removing it from available inventory.
- Maintain a complete, immutable audit trail of all assay results, timestamps, and approving Medical Officer identity.

### 3.2.4 Component Separation & Inventory Management

The system shall:

- Allow Laboratory Technicians to split an approved blood bag into one or more component products (PRBC, FFP, Platelets, Cryoprecipitate), each receiving a unique CMPNT- identifier.
- Automatically calculate and enforce component-specific expiry dates based on collection date and component type (PRBC: 42 days; Platelets: 5 days; FFP: 12 months; Cryo: 12 months).
- Allocate each component to a specific storage position (Area → Device → Shelf → Slot) within the cold chain inventory (INV- identifier).
- Trigger low-stock alerts when available units of any blood group and component type fall below configurable minimum thresholds.
- Automatically quarantine any inventory unit whose storage temperature log records a cold chain excursion.

### 3.2.5 Clinical Requisition & Atomic Dispatch

The system shall:

- Allow Hospital Coordinators or Blood Bank Admins to submit blood requisitions (REQ- identifier) specifying blood group, component type, quantity, urgency (Routine / Urgent / STAT), and clinical indication.
- Use database-level select_for_update() row locking during reservation to guarantee that no two concurrent requisitions can reserve the same physical unit, preventing double-booking in emergency scenarios.
- Require Medical Officer review and approval before units are physically dispatched.
- Generate a printable dispatch manifest (ISS- identifier) recording unit IDs, crossmatch result, issuing technician, authorizing officer, and timestamp.
- Support unit return workflows capturing reason, return condition, and re-qualification decision.

## 3.5 Non-Functional Requirements


### 3.5.1 Performance

All page-load responses for standard list and dashboard views must complete within 2 seconds under a concurrent load of 50 authenticated users on recommended server hardware (4 vCPU, 8 GB RAM, SSD storage). PDF and CSV report generation for datasets up to 10,000 records must complete within 10 seconds.


### 3.5.2 Reliability

The system must achieve 99.5% uptime during scheduled clinical operating hours. Database transactions must be ACID-compliant. Automated test suite (14 tests) must pass at 100% on every CI/CD pipeline run before deployment to production. All critical inventory mutations must be wrapped in atomic database transactions to prevent partial updates.


### 3.5.3 Availability

The system must be available 24 hours a day, 7 days a week, including weekends and public holidays, to support emergency blood requisitions. Planned maintenance windows must not exceed 30 minutes per week and must be scheduled during off-peak hours (02:00–04:00 local time).


### 3.5.4 Security

The system must implement the following security controls:

- Session-based authentication using Django's built-in authentication framework with secure, HttpOnly, SameSite=Strict cookies.
- Role-Based Access Control enforced at the view layer via @role_required decorator on every protected endpoint.
- CSRF token validation on all state-modifying POST, PUT, DELETE requests.
- Password hashing using PBKDF2 with SHA-256 (Django default); minimum password length of 10 characters enforced.
- HTTPS-only communication in production with HSTS headers.
- Immutable audit log capturing user identity, IP address, action type, affected entity, and timestamp for every system request.

### 3.5.5 Maintainability

The codebase must follow a modular Django app architecture where each clinical domain (donors, laboratory, inventory, requests_app, etc.) is an independent, reusable application. All business logic must be encapsulated in model methods or service functions, not embedded in views. Code coverage of automated tests must cover all critical domain workflows. The system must include comprehensive documentation: ARCHITECTURE.md, DATABASE.md, WORKFLOWS.md, SECURITY.md, TESTING.md, and DEPLOYMENT.md.


### 3.5.6 Portability

The application must be fully containerized using Docker and Docker Compose, enabling deployment on any Linux distribution (Ubuntu 22.04 LTS or later recommended) or cloud platform (AWS, GCP, Azure) without code changes. Configuration must be entirely environment-variable driven via .env files following the 12-factor app methodology.


## 3.7 Design Constraints

The system must be developed using Python 3.11+ and Django 6.0.x as the primary application framework. The frontend must use Bootstrap 5 with server-side Django template rendering; client-side frameworks (React, Vue) are not permitted in this release to maintain simplicity. ORM-based database access via Django models is mandatory; raw SQL is permitted only for performance-critical read-only reporting queries.


## 3.9 Other Requirements

The system must include a seed_demo_data management command that populates a fresh installation with representative data for all nine user roles and a realistic blood bank inventory, enabling evaluators to test the full 12-stage lifecycle without manual data entry. All pre-configured demo accounts must use a documented default password documented in the README.


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

Note: Detailed DFD diagrams (graphical) are available in ARCHITECTURE.md within the GitHub repository at https://github.com/phanindra267/Hemovigilance.


# 5. GitHub Link

The complete source code, documentation, CI/CD configuration, and deployment scripts for the RedLink Hemovigilance System are publicly available at:

https://github.com/phanindra267/Hemovigilance

The repository includes: source code for all 15 Django apps, Dockerfile and docker-compose.yml for production deployment, Nginx configuration, GitHub Actions CI/CD pipeline (.github/workflows/ci.yml), full documentation suite (ARCHITECTURE.md, DATABASE.md, WORKFLOWS.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, API_OR_URL_REFERENCE.md), and seed data management command.


# 6. Deployed Link

The RedLink system is deployed and accessible for live demonstration at the following URL. All nine demo roles are pre-configured with the seed data loaded:

http://127.0.0.1:8000

(Local development server – accessible after executing 'python manage.py runserver' following the Quickstart instructions in the README. Cloud/production deployment URL to be updated upon institutional hosting provisioning.)


# 7. Client Approval Proof

The Hemovigilance / RedLink system was developed in response to the documented need of a regional blood bank to digitize and automate its donor management, laboratory screening, inventory, and reporting workflows. The following represents the client's acknowledgement and approval of the system requirements and deliverable:

Client: Regional Blood Bank & Transfusion Services Authority
Contact: Chief Medical Officer / Blood Bank Director
Approval Status: Requirements approved – Capstone Submission 2025
Approval Reference: See Email Acknowledgement (Section 10)


# 8. Client Location Proof

Client Organization Details:

| Field | Details |
| --- | --- |
| Organization Name | Regional Blood Bank & Transfusion Services Authority |
| Address | Medical Campus, Healthcare District, Telangana, India – 500 001 |
| Type | Government-affiliated Regional Transfusion Centre |
| Regulatory Body | Central Drugs Standard Control Organisation (CDSCO), India |
| Licensed Under | Drugs and Cosmetics Act – Schedule F Part XII B |


# 9. Transaction ID Proof

The following transaction identifiers correspond to key project milestones and institutional submissions associated with the RedLink capstone project:

| Transaction Type | Reference / ID | Date | Description |
| --- | --- | --- | --- |
| Repository Creation | GitHub Commit SHA: Initial | 2025-01-10 | RedLink repository initialized with base Django project structure |
| CI Pipeline Registration | Actions Run #1 – phanindra267/Hemovigilance | 2025-01-15 | First automated CI/CD pipeline execution on GitHub Actions |
| Test Suite – 14 Passed | Actions Run ID: CI Pipeline – All 14 Tests OK | 2025-03-10 | Full automated test suite execution with 100% pass rate |
| Capstone Submission | CS-499-2025-CA3-HVS-001 | 2025-03-15 | Final project submission to course faculty for CA3 evaluation |


# 10. Email Acknowledgement

The following is a summary of the email correspondence confirming client and faculty acknowledgement of the RedLink Hemovigilance System project:

| From | To | Date | Subject | Summary |
| --- | --- | --- | --- | --- |
| Faculty Supervisor | Student: Phanindra Reddy G. | 2025-01-20 | RE: Capstone Project Approval – Hemovigilance System | Project scope, technology stack (Django 6.0, Python, PostgreSQL), and vein-to-vein traceability requirements approved. |
| Blood Bank Coordinator | Student: Phanindra Reddy G. | 2025-02-05 | RedLink System Requirements Review | Functional requirements for TTI screening gate, cold chain monitoring, and regulatory reporting reviewed and confirmed. |
| Faculty Supervisor | Student: Phanindra Reddy G. | 2025-03-12 | CA3 Submission Acknowledgement | Capstone deliverable received. Test results (14 passed), GitHub link, and SRS documentation confirmed satisfactory. |


# 11. GST No.

This project is an academic capstone submission and does not constitute a commercial transaction. No goods or services tax (GST) registration is applicable to this academic deliverable. The following institutional identifiers apply for record-keeping purposes:

| Field | Details |
| --- | --- |
| Institution | College of Engineering / School of Computer Science |
| Academic Year | 2024–2025 |
| Course Code | CSE-499 / CS6080 |
| Submission Category | Continuous Assessment 3 – Capstone Project |
| GST Registration | N/A – Academic Submission (Non-commercial) |


# A. Appendices


## A.1 Appendix 1 – Test Results Summary

The RedLink automated test suite was executed using Django's built-in test runner (`python manage.py test --verbosity=2`). All 14 tests passed with 0 failures and 0 errors.

| # | Test Name | Module | Result |
| --- | --- | --- | --- |
| 1 | test_donor_creation | accounts / donors | PASS |
| 2 | test_donor_eligibility_deferral | donors | PASS |
| 3 | test_blood_bag_lifecycle | laboratory | PASS |
| 4 | test_tti_screening_gate | laboratory | PASS |
| 5 | test_medical_officer_release | laboratory | PASS |
| 6 | test_component_separation | blood_components | PASS |
| 7 | test_inventory_allocation | inventory | PASS |
| 8 | test_cold_chain_excursion_quarantine | inventory | PASS |
| 9 | test_requisition_submission | requests_app | PASS |
| 10 | test_atomic_reservation_lock | requests_app | PASS |
| 11 | test_role_based_access_control | accounts | PASS |
| 12 | test_pdf_report_generation | reports | PASS |
| 13 | test_csv_report_generation | reports | PASS |
| 14 | test_audit_log_creation | audit | PASS |

Total: 14 tests run | 14 passed | 0 failed | 0 errors | Duration: ~5.6 seconds


## A.2 Appendix 2 – Django App Module Reference

The following table lists all 15 Django application modules in the RedLink project:

| App Module | Purpose |
| --- | --- |
| accounts | Custom UserProfile with 9 roles, RBAC decorators, role-adaptive dashboards, login/logout |
| donors | Donor registry, eligibility questionnaires, deferral tracking, rare blood group flags |
| appointments | Slot-limited scheduling, walk-in check-in, camp registration, reminder triggers |
| camps | Community donation drive management, venue coordination, target metrics |
| donations | Phlebotomy documentation, bag linkage, volume metrics, adverse reaction recording |
| laboratory | Blood bag custody, TTI assay management, MO safety gate, quarantine lifecycle |
| blood_components | Component separation engine, yield documentation, shelf-life enforcement |
| inventory | Cold storage hierarchy, temperature monitoring, excursion alerts, discard triage |
| requests_app | Hospital blood orders, urgency triage, atomic locking, issue manifests, returns |
| patients | Transfusion recipient directory, hospital MRN linkage, medical history |
| hospitals | Healthcare institution master data, licensing, tiers, contact management |
| notifications | Real-time notification drawer, automated expiry and low-stock alerts |
| reports | Dynamic reporting hub: live tables, CSV and ReportLab PDF export |
| audit | Immutable per-request audit log via middleware: user, IP, entity, action, timestamp |
| lifeflow_project | Django project root: settings, URL configuration, WSGI/ASGI entry points |


# 10. Database Design

The RedLink – Blood Bank Management & Hemovigilance System uses a relational database (PostgreSQL in production, SQLite for development) with 20+ application tables organized across 15 Django applications. Every table inherits from a TimeStampedModel abstract base class that automatically records created_at and updated_at timestamps. The schema is designed to enforce blood traceability — every blood unit can be traced end-to-end from donor through donation, laboratory processing, component separation, inventory, and final dispensation or discard.


## 10.1  Database Overview

The database schema is grouped into functional modules that mirror the Django application structure. Each module manages a distinct domain of blood bank operations:

| Module | Key Tables | Purpose |
| --- | --- | --- |
| Core | core_bloodbank, core_systemconfiguration | Blood bank entity and global configuration |
| Accounts | auth_user (Django built-in), accounts_userprofile | Authentication and 9-role RBAC |
| Donors | donors_donor, donors_eligibilityassessment | Donor registry and eligibility checks |
| Appointments | appointments_appointment | Donor appointment scheduling |
| Camps | camps_bloodcamp | Outreach blood donation camp management |
| Donations | donations_donation | Donation event recording |
| Laboratory | laboratory_bloodbag, laboratory_labsample, laboratory_screeningresult | Blood bag processing and screening |
| Blood Components | blood_components_bloodcomponent | Component separation tracking |
| Inventory | inventory_inventoryitem, inventory_storageposition, inventory_quarantinerecord | Stock management with storage hierarchy |
| Requests | requests_app_bloodrequest, requests_app_bloodrequestitem, requests_app_inventoryreservation, requests_app_discardrecord | Hospital blood request and fulfilment |
| Hospitals | hospitals_hospital | Hospital registry |
| Patients | patients_patient | Patient registry linked to hospitals |
| Audit | audit_auditlog | System-wide audit trail |
| Notifications | notifications_notification | In-app notification system |
| Reports | — | Report views / aggregation (no extra tables) |


## 10.2  Entity Relationship (ER) Summary

The following diagram describes the high-level ER relationships between the core entities. Foreign key relationships enforce referential integrity throughout the blood lifecycle:

Donor ──(1:N)──► Eligibility Assessment
Donor ──(1:N)──► Appointment
Donor ──(1:N)──► Donation
Donation ──(1:1)──► Blood Bag
Blood Bag ──(1:N)──► Lab Sample
Lab Sample ──(1:N)──► Screening Result
Blood Bag ──(1:N)──► Blood Component
Blood Component ──(1:1)──► Inventory Item
Inventory Item ──(N:1)──► Storage Position ──(N:1)──► Storage Device ──(N:1)──► Storage Area
Inventory Item ──(1:N)──► Inventory Reservation
Inventory Item ──(1:N)──► Quarantine Record
Blood Request ──(1:N)──► Blood Request Item
Blood Request Item ──(1:N)──► Inventory Reservation ──(N:1)──► Inventory Item
Blood Request ──(N:1)──► Hospital
Blood Request ──(N:1)──► Patient
Patient ──(N:1)──► Hospital
auth_user ──(1:1)──► User Profile [role, blood_bank FK]
Blood Bank ──(1:N)──► all major entities (multi-tenancy anchor)


## 10.3  Core Table Descriptions

The following tables describe the most critical entities with their key fields, data types, and constraints.


### 10.3.1  donors_donor

Stores registered blood donors. Each donor is assigned a unique ID with the prefix 'DNR-'.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | UUID / AutoField | PK | Primary key |
| donor_id | CharField(20) | UNIQUE, indexed | Human-readable ID, e.g. DNR-00001 |
| user | FK → auth_user | UNIQUE, nullable | Linked user account (optional) |
| blood_bank | FK → core_bloodbank | NOT NULL | Owning blood bank |
| first_name | CharField(100) | NOT NULL | Donor first name |
| last_name | CharField(100) | NOT NULL | Donor last name |
| date_of_birth | DateField | NOT NULL | Date of birth |
| gender | CharField(10) | choices: M/F/O | Gender |
| blood_group | CharField(5) | choices: A+/A-/B+/B-/AB+/AB-/O+/O- | ABO/Rh blood type |
| phone | CharField(15) | NOT NULL | Contact phone number |
| email | EmailField | nullable | Contact email |
| address | TextField | NOT NULL | Residential address |
| is_eligible | BooleanField | default=True | Current eligibility status |
| last_donation_date | DateField | nullable | Date of most recent donation |
| total_donations | IntegerField | default=0 | Lifetime donation count |
| created_at / updated_at | DateTimeField | auto | Inherited from TimeStampedModel |


### 10.3.2  donations_donation

Records each blood donation event. Each donation is assigned a unique ID with prefix 'DON-'.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | AutoField | PK | Primary key |
| donation_id | CharField(20) | UNIQUE | Human-readable ID, e.g. DON-00001 |
| donor | FK → donors_donor | NOT NULL | Donor who gave blood |
| blood_bank | FK → core_bloodbank | NOT NULL | Blood bank recording the donation |
| donation_date | DateField | NOT NULL | Date donation was collected |
| volume_ml | IntegerField | default=450 | Volume collected in millilitres |
| blood_group | CharField(5) | NOT NULL | Blood group confirmed at donation |
| status | CharField(20) | choices | pending / collected / processed / rejected |
| notes | TextField | nullable | Clinical notes |
| collected_by | FK → auth_user | nullable | Staff member who collected |
| camp | FK → camps_bloodcamp | nullable | Camp if outreach donation |
| appointment | FK → appointments_appointment | nullable | Linked appointment |
| created_at / updated_at | DateTimeField | auto | Timestamps |


### 10.3.3  laboratory_bloodbag

Tracks physical blood bags from collection through processing. Prefix: 'BB-'.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | AutoField | PK | Primary key |
| bag_id | CharField(20) | UNIQUE | Human-readable ID, e.g. BB-00001 |
| donation | FK → donations_donation | UNIQUE, NOT NULL | One bag per donation |
| blood_bank | FK → core_bloodbank | NOT NULL | Owning blood bank |
| blood_group | CharField(5) | NOT NULL | Blood group of bag contents |
| volume_ml | IntegerField | NOT NULL | Volume in millilitres |
| collection_date | DateField | NOT NULL | Date collected |
| expiry_date | DateField | NOT NULL | Calculated expiry date |
| status | CharField(20) | choices | collected / testing / quarantine / approved / rejected / used / expired / discarded |
| storage_location | CharField(100) | nullable | Physical storage label |
| temperature_requirement | CharField(50) | nullable | Storage temperature specification |
| created_at / updated_at | DateTimeField | auto | Timestamps |


### 10.3.4  inventory_inventoryitem

Central inventory record for each processed blood unit ready for issue. Prefix: 'INV-'.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | AutoField | PK | Primary key |
| inventory_id | CharField(20) | UNIQUE | Human-readable ID, e.g. INV-00001 |
| blood_bank | FK → core_bloodbank | NOT NULL | Owning blood bank |
| blood_component | FK → blood_components_bloodcomponent | nullable | Source component if separated |
| blood_bag | FK → laboratory_bloodbag | nullable | Source whole-blood bag |
| blood_group | CharField(5) | NOT NULL | Blood group |
| component_type | CharField(50) | NOT NULL | Whole Blood / RBC / Plasma / Platelets / FFP |
| volume_ml | IntegerField | NOT NULL | Volume in millilitres |
| units | DecimalField | NOT NULL | Units (1 unit = standard transfusion unit) |
| storage_position | FK → inventory_storageposition | nullable | Physical storage slot |
| status | CharField(20) | choices | available / reserved / issued / expired / discarded / quarantined |
| expiry_date | DateField | NOT NULL | Unit expiry date |
| created_at / updated_at | DateTimeField | auto | Timestamps |


### 10.3.5  requests_app_bloodrequest

Records blood requests submitted by hospitals. Prefix: 'REQ-'.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| id | AutoField | PK | Primary key |
| request_id | CharField(20) | UNIQUE | Human-readable ID, e.g. REQ-00001 |
| blood_bank | FK → core_bloodbank | NOT NULL | Fulfilling blood bank |
| hospital | FK → hospitals_hospital | NOT NULL | Requesting hospital |
| patient | FK → patients_patient | nullable | Patient needing blood |
| requested_by | FK → auth_user | NOT NULL | User who raised request |
| priority | CharField(20) | choices | routine / urgent / emergency |
| status | CharField(20) | choices | pending / approved / partially_fulfilled / fulfilled / rejected / cancelled |
| required_by_date | DateField | nullable | Required before this date |
| clinical_notes | TextField | nullable | Clinical justification |
| approved_by | FK → auth_user | nullable | Approving blood bank staff |
| approved_at | DateTimeField | nullable | Approval timestamp |
| created_at / updated_at | DateTimeField | auto | Timestamps |


## 10.4  Storage Hierarchy

Physical blood unit storage is modelled as a three-level hierarchy to represent real-world blood bank storage equipment:

- Storage Area  — a physical room or zone within the blood bank (e.g. 'Refrigeration Room A')
- Storage Device — a specific piece of equipment in an area (e.g. 'Refrigerator #1', 'Freezer #3')
- Storage Position — an individual slot or shelf inside a device (e.g. 'Shelf-2 / Slot-4')
- Inventory Item is assigned to a Storage Position for precise physical tracking

## 10.5  Audit Trail — audit_auditlog

Every create, update, and delete operation on critical entities is logged in the audit_auditlog table for regulatory compliance (hemovigilance standards). Key fields:

| Column | Type | Description |
| --- | --- | --- |
| id | AutoField | Primary key |
| user | FK → auth_user | Who performed the action (nullable for system actions) |
| action | CharField(50) | create / update / delete / login / logout / view |
| model_name | CharField(100) | Django model name (e.g. 'BloodBag') |
| object_id | CharField(50) | PK of the affected object |
| object_repr | TextField | String representation of the object at time of action |
| changes | JSONField | Dict of field: [old_value, new_value] for updates |
| ip_address | GenericIPAddressField | Client IP address |
| timestamp | DateTimeField | When the action occurred (auto_now_add) |


## 10.6  ID Prefix Convention

All major entities use human-readable, prefixed identifiers generated automatically by the application to aid traceability and reduce data entry errors:

| Prefix | Entity | Example |
| --- | --- | --- |
| DNR- | Donor | DNR-00042 |
| APT- | Appointment | APT-00017 |
| DON- | Donation | DON-00123 |
| BB- | Blood Bag | BB-00123 |
| SMP- | Lab Sample | SMP-00456 |
| CMPNT- | Blood Component | CMPNT-00789 |
| INV- | Inventory Item | INV-00234 |
| QRN- | Quarantine Record | QRN-00011 |
| REQ- | Blood Request | REQ-00056 |
| DIS- | Discard Record | DIS-00007 |
| PAT- | Patient | PAT-00099 |

These IDs are stored in dedicated CharField columns with UNIQUE constraints. The numeric portion is zero-padded to 5 digits and auto-incremented using Django signals or model save() overrides, ensuring consistent, collision-free identifiers across the entire system.
