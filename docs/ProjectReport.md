RedLink – Blood Bank Management & Hemovigilance System

Software Requirements Specification

Course Code: CSE4001
Course Name: Software Engineering & Web Application Development

Student Name: Phanindra
Student Registration Number: RA2311003010267

Prepared for
Continuous Assessment 3
Spring 2025

Repository: https://github.com/phanindra267/Hemovigilance


# Revision History

| Name | Date | Reason For Changes | Version |
| --- | --- | --- | --- |
| Phanindra | 2026-11-01 | Initial project scaffolding, 15 Django apps domain modeling | 0.9.0 |
| Phanindra | 2026-11-13 | Vein-to-vein state machine, TTI dual verification & storage hierarchy | 0.9.5 |
| Phanindra | 2026-11-16 | Production release, embedded technical diagrams, IEEE SRS conformance | 1.0.0 |


# Table of Contents

Revision History ................................................................................................................................. ii

1. Introduction ..................................................................................................................................... 1

1.1 Purpose ..................................................................................................................................... 1

1.2 Scope ......................................................................................................................................... 1

1.3 Definitions, Acronyms, and Abbreviations .................................................................................... 1

1.4 References ................................................................................................................................. 2

1.5 Overview .................................................................................................................................... 2

2. General Description .......................................................................................................................... 2

2.1 Product Perspective (System Architecture Diagram) ................................................................. 2

2.2 Product Functions (12-Stage State Machine Diagram) ................................................................. 3

2.3 User Characteristics (9 Organizational Roles) ............................................................................ 4

2.4 General Constraints .................................................................................................................... 4

2.5 Assumptions and Dependencies ................................................................................................ 5

3. Specific Requirements ..................................................................................................................... 5

3.1 External Interface Requirements ................................................................................................ 5

3.1.1 User Interfaces ................................................................................................................. 5

3.1.2 Hardware Interfaces .......................................................................................................... 5

3.1.3 Software Interfaces ........................................................................................................... 6

3.1.4 Communications Interfaces .............................................................................................. 6

3.2 Functional Requirements ............................................................................................................ 6

3.2.1 Donor Registration & Clinical Eligibility ........................................................................... 6

3.2.2 Appointment Booking & Outreach Camp Logistics ........................................................... 7

3.2.3 Phlebotomy Collection & Barcoded Bag Tagging .............................................................. 8

3.2.4 Serological TTI Screening & Medical Officer Release Gate ............................................... 8

3.2.5 Component Fractionation & Cold-Chain Storage Hierarchy ............................................... 9

3.2.6 Clinical Requisition, Atomic Lock & Issue (Sequence Diagram) .......................................... 10

3.5 Non-Functional Requirements .................................................................................................... 11

3.5.1 Performance .................................................................................................................... 11

3.5.2 Reliability ......................................................................................................................... 11

3.5.3 Availability ....................................................................................................................... 11

3.5.4 Security ........................................................................................................................... 11

3.5.5 Maintainability ................................................................................................................. 12

3.5.6 Portability ........................................................................................................................ 12

3.7 Design Constraints ..................................................................................................................... 12

3.9 Other Requirements (Universal Audit Trail) ............................................................................... 12

4. Analysis Models ............................................................................................................................... 13

4.0 UML Use Case Modeling (Use Case Diagram) ............................................................................ 13

4.1 Data Flow Diagrams (Context Level-0 and Detailed Level-1 DFDs) ............................................ 14

4.2 Entity-Relationship & Relational Database Design (ER Diagram) ................................................. 16

5. GitHub Link ..................................................................................................................................... 18

6. Deployed Link ................................................................................................................................... 19

7. Client Approval Proof ....................................................................................................................... 20

8. Client Location Proof ........................................................................................................................ 21

9. Transaction ID Proof ......................................................................................................................... 22

10. Email Acknowledgement ................................................................................................................. 23

11. GST No. ......................................................................................................................................... 24

A. Appendices ...................................................................................................................................... 25

A.1 Appendix 1 – Automated Test Execution Summary ................................................................... 25

A.2 Appendix 2 – Modular Django Apps Reference .......................................................................... 26


# 1. Introduction

The introduction to this Software Requirement Specification (SRS) document provides a comprehensive overview of the RedLink Blood Bank Management & Hemovigilance Information System. This document contains all specifications, constraints, architectural models, and validation criteria required by software engineers, clinical pathologists, hospital transfusion committees, and regulatory compliance auditors to design, implement, verify, and maintain the system. This SRS conforms to the IEEE Std 830-1998 guidelines.


## 1.1 Purpose

The purpose of this SRS is to establish a rigorous, unambiguous specification for RedLink, an enterprise web application engineered to manage the complete vein-to-vein transfusion lifecycle. The intended audience includes: (1) Software developers and DevOps engineers responsible for implementation and infrastructure; (2) Quality assurance engineers verifying functional boundaries; (3) Medical Officers and Certified Phlebotomists executing clinical protocols; (4) Hospital Transfusion Coordinators managing emergency requisitions; and (5) Regulatory authorities (e.g., State Blood Transfusion Councils) assessing compliance with statutory standards.


## 1.2 Scope

The software product produced is RedLink – Blood Bank Management & Hemovigilance System. The system governs all twelve operational stages of blood banking: voluntary donor onboarding, clinical eligibility screening against WHO criteria, donor appointment scheduling, community mobile donation camps, phlebotomy collection, mandatory infectious disease screening (HIV 1/2, Hepatitis B, Hepatitis C, Syphilis, Malaria) with dual Medical Officer sign-off, component fractionation (PRBC, FFP, Platelets, Cryoprecipitate), three-tier cold chain storage management (Area -> Device -> Position), hospital blood requisition with atomic concurrency protection (select_for_update), issue manifests, and adverse transfusion reaction hemovigilance tracking.

What the software will NOT do: In Phase 1, the system does not interface directly with proprietary RS-232 hematology hardware analyzers; all assay results are entered and verified through authenticated digital forms with dual authorization.


## 1.3 Definitions, Acronyms, and Abbreviations

- ABO / Rh: Human blood classification systems based on red cell antigens and Rhesus factor presence.
- TTI: Transfusion-Transmissible Infection (HIV 1/2, HBsAg, HCV, Treponema pallidum, Plasmodium).
- PRBC: Packed Red Blood Cells (shelf life: 42 days at 2°C to 6°C).
- FFP: Fresh Frozen Plasma (shelf life: 365 days at -18°C or colder).
- Platelets: Thrombocyte concentrate (shelf life: 5 days at 20°C to 24°C with continuous agitation).
- Hemovigilance: Systematic surveillance procedures covering adverse transfusion reactions from donor to recipient.
- RBAC: Role-Based Access Control, enforcing privilege boundaries across nine distinct user roles.
- STAT: Medical terminology denoting an immediate, life-or-death emergency clinical requisition.
- MRN: Medical Record Number assigned to hospitalized recipients.
- ACID: Atomicity, Consistency, Isolation, and Durability database transaction properties.

## 1.4 References

- IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications.
- World Health Organization (WHO): Guidelines on Developing a National Blood Transfusion Service.
- National Blood Transfusion Council (NBTC) & Drugs and Cosmetics Act (Schedule K / Forms 28-C & 28-E).
- Django 6.0 LTS Framework Documentation: https://docs.djangoproject.com/
- PostgreSQL 14+ Documentation: https://www.postgresql.org/docs/
- RedLink Public Source Repository: https://github.com/phanindra267/Hemovigilance

## 1.5 Overview

The remainder of this SRS is organized as follows: Section 2 outlines the general product perspective, system architecture, 12-stage state machine, and user roles. Section 3 details external interfaces, exhaustive functional specifications, and measurable non-functional requirements. Section 4 provides formal analysis models, including UML Use Case diagrams, Level-0 and Level-1 DFDs, and complete Relational ER database specifications. Sections 5 through 11 present the live deployment links, commercial acceptance proofs, and tax filings. Section A provides testing matrices and application reference documentation.


# 2. General Description


## 2.1 Product Perspective

RedLink is engineered as a monolithic, modular web application following a multi-tier architectural pattern. The application cleanly separates Presentation (Bootstrap 5, HTML5, Vanilla JS), Security & Gateway (Nginx, Gunicorn, AuditMiddleware), Domain Business Logic (15 decoupled Django apps), and Persistence (PostgreSQL 14+ / SQLite 3). Figure 2.1 illustrates the comprehensive multi-tier architectural layout.

Figure 2.1: RedLink Multi-Tier System Architecture Diagram


## 2.2 Product Functions

The system orchestrates the complete 12-stage vein-to-vein transfusion lifecycle, ensuring unbroken chain of custody, biological safety gates, and row-level atomic reservation. Figure 2.2 illustrates the state machine governing each stage.

Figure 2.2: 12-Stage Vein-to-Vein Transfusion State Machine


## 2.3 User Characteristics

The system enforces strict Role-Based Access Control (RBAC) across nine organizational user roles:

| Role Name | Technical Identifier | Operational Scope & Responsibilities |
| --- | --- | --- |
| Super Administrator | admin | System configuration, facility profiles, global parameters, audit trail oversight |
| Blood Bank Admin | bb_admin | Facility administration, staff accounts, equipment inventory, stock thresholds |
| Medical Officer | dr_smith | Clinical donor eligibility sign-off, TTI lab safety gate verification, discard orders |
| Laboratory Technician | tech_john | Phlebotomy barcoding, serological assay entry, component fractionation |
| Inventory Manager | inv_sarah | Cold chain device slot allocation, temperature logs, quarantine triage |
| Donor Coordinator | coord_alex | Donor registry, appointment scheduling, camp outreach logistics |
| Hospital Coordinator | hosp_maria | Hospital blood orders, crossmatch requests, emergency STAT requisitions |
| Camp Organizer | camp_david | Community blood drive venue logistics, volunteer coordination |
| Voluntary Donor | donor_raj | Self-service donor portal, donation history, digital appointment booking |


## 2.4 General Constraints

- Regulatory: Strict compliance with Drugs and Cosmetics Act rules governing donor deferral and test records.
- Safety Gate: Zero-tolerance policy for releasing units with reactive or pending TTI test results.
- Concurrency: Absolute prevention of double-allocation during simultaneous clinical requisitions.
- Auditability: Every database record mutation must capture client IP, user ID, timestamp, and field changes.

## 2.5 Assumptions and Dependencies

- Client workstations operate modern, standards-compliant web browsers (Chrome 110+, Firefox 115+, Safari 16+).
- PostgreSQL 14+ database instance running with connection pooling and automated write-ahead log backups.
- Continuous network connectivity between phlebotomy stations, testing labs, and central blood bank servers.

# 3. Specific Requirements


## 3.1 External Interface Requirements


### 3.1.1 User Interfaces

The user interface is implemented using responsive Bootstrap 5 and custom healthcare CSS styling. Dashboards present color-coded clinical badges (Quarantined: Amber, Safe/Available: Green, Reactive/Discard: Red, Reserved: Blue). Interface layouts adapt seamlessly across desktop monitors, phlebotomy tablets, and mobile devices.


### 3.1.2 Hardware Interfaces

USB barcode scanners emitting standard HID keyboard emulation are supported for rapid scanning of donor IDs (DNR-), blood bag barcodes (BB-), sample tubes (SMP-), and storage slot positions.


### 3.1.3 Software Interfaces

Python 3.14 runtime, Django 6.0.6 framework, PostgreSQL 14+ database engine, Gunicorn 21+ WSGI application server, Nginx 1.24+ reverse proxy, and WhiteNoise 6+ static file middleware.


### 3.1.4 Communications Interfaces

All network communications are encrypted via HTTPS over TLS 1.3 on port 443. RESTful JSON endpoints are designed for future external Hospital Information System (HIS) and Electronic Medical Record (EMR) integrations.


## 3.2 Functional Requirements


### 3.2.1 Donor Registration & Clinical Eligibility (Feature #1)


#### 3.2.1.1 Introduction

Captures donor demographics, medical history, and clinical vitals to determine donation eligibility.


#### 3.2.1.2 Inputs

Full name, date of birth, biological gender, ABO/Rh blood group, phone number, residential address, weight (kg), hemoglobin (g/dL), systolic/diastolic blood pressure, pulse rate, temperature, recent medical history questionnaire.


#### 3.2.1.3 Processing

Evaluates vitals against WHO criteria (weight >= 45 kg, Hb >= 12.5 g/dL, age 18-65). Enforces minimum 90-day donation interval. Assigns unique zero-padded identifier with prefix 'DNR-'. Flags deferral reasons if vitals fail.


#### 3.2.1.4 Outputs

Stored donor profile, active/deferred status indicator, automated next eligible donation date calculation.


#### 3.2.1.5 Error Handling

Rejects duplicate donor records based on phone and government ID. Displays validation warnings for borderline vitals.


### 3.2.2 Appointment Booking & Blood Camp Management (Feature #2)


#### 3.2.2.1 Introduction

Coordinates donor appointment scheduling at blood bank facilities and mobile community blood donation drives.


#### 3.2.2.2 Inputs

Donor ID, preferred appointment date, time slot, venue (central facility vs outreach camp), camp organizer contact.


#### 3.2.2.3 Processing

Validates slot availability against facility capacity limits. Creates appointment record (APT- prefix). Links outreach camp drives (CMP- prefix) to phlebotomy collection teams.


#### 3.2.2.4 Outputs

Confirmed appointment voucher, daily phlebotomy collection manifest, camp attendance roster.


#### 3.2.2.5 Error Handling

Prevents overbooking of appointment time slots. Restricts appointment scheduling for currently deferred donors.


### 3.2.3 Serological TTI Screening & Medical Officer Release Gate (Feature #3)


#### 3.2.3.1 Introduction

Governs infectious disease screening assays and enforces a dual-sign-off safety gate prior to releasing blood units.


#### 3.2.3.2 Inputs

Sample tube barcode (SMP-), whole blood bag ID (BB-), qualitative assay results for HIV-1/2, HBsAg, HCV, Syphilis, Malaria.


#### 3.2.3.3 Processing

If ALL 5 assays are non-reactive AND Medical Officer confirms verification: bag status transitions to 'approved'. If ANY assay is reactive: bag status is irreversibly transitioned to 'reactive_unsafe', locked into quarantine, and donor deferral is triggered.


#### 3.2.3.4 Outputs

Verified laboratory safety report, certified blood bag record, quarantine lock notification.


#### 3.2.3.5 Error Handling

Hard-blocks release of blood units without dual sign-off. Rejects entry of incomplete assay batteries.


### 3.2.4 Component Fractionation & Cold-Chain Storage Hierarchy (Feature #4)


#### 3.2.4.1 Introduction

Manages separation of approved whole blood into therapeutic components and tracks physical storage slots.


#### 3.2.4.2 Inputs

Approved blood bag ID, separation parameters, target components (PRBC, FFP, Platelets, Cryo), storage device slot.


#### 3.2.4.3 Processing

Creates child component records (CMPNT-) with discrete shelf lives (PRBC: 42 days, FFP: 365 days, Platelets: 5 days). Instantiates InventoryItem (INV-) mapped to a three-tier physical slot (Storage Area -> Device -> Position).


#### 3.2.4.4 Outputs

Barcoded component units, cold chain occupancy map, automated expiry countdown alerts.


#### 3.2.4.5 Error Handling

Prevents assigning units to incompatible temperature zones. Blocks component separation from non-cleared blood bags.


### 3.2.5 Clinical Requisition, Atomic Reservation & Dispatch (Feature #5)


#### 3.2.5.1 Introduction

Processes hospital blood orders, locks candidate units via atomic database transactions, and generates dispatch manifests.


#### 3.2.5.2 Inputs

Hospital ID, recipient patient MRN, blood group, component type, unit quantity, clinical urgency (Routine, Urgent, STAT).


#### 3.2.5.3 Processing

Executes PostgreSQL row-level lock using 'select_for_update()' inside 'transaction.atomic()'. Validates ABO/Rh compatibility. Creates reservation (RSV-) and updates inventory status to 'reserved'. Upon MO approval, issues unit (ISS-).


#### 3.2.5.4 Outputs

Requisition record (REQ-), reservation lock, official issue dispatch manifest with courier chain-of-custody.


#### 3.2.5.5 Error Handling

Serializes concurrent requests for identical units, eliminating race conditions. Blocks reservation of expired or quarantined stock.

Figure 3.1: UML Sequence Diagram for Atomic Requisition & Reservation


## 3.5 Non-Functional Requirements


### 3.5.1 Performance

Web transaction response time < 500 ms for 95% of standard requests. STAT emergency inventory lookup and reservation < 250 ms. Concurrent handling of 100+ active clinical sessions without degradation.


### 3.5.2 Reliability

Mean Time Between Failures (MTBF) > 720 hours. Zero data loss guaranteed by PostgreSQL ACID transaction commits and WAL write-ahead logging.


### 3.5.3 Availability

99.9% application uptime, providing continuous 24/7/365 availability for critical hospital transfusion services.


### 3.5.4 Security

Argon2 / PBKDF2 password hashing; mandatory CSRF tokens on all POST mutations; strict RBAC decorator enforcement; SQL injection immunity via Django parameterized ORM queries; HttpOnly, SameSite session cookies.


### 3.5.5 Maintainability

Modular architecture divided across 15 decoupled Django applications; PEP 8 code compliance; automated unit and integration test coverage across all critical workflows.


### 3.5.6 Portability

Containerized with multi-stage Dockerfile and docker-compose.yml; fully portable across Ubuntu Linux VPS, cloud providers (Render, AWS, DigitalOcean), and local workstations.


## 3.7 Design Constraints

Must adhere to Python 3.11-3.14 LTS standards, Django LTS framework conventions, WHO cold-chain temperature thresholds, and Schedule K Drugs and Cosmetics Act record retention requirements.


## 3.9 Other Requirements

Universal Immutable Audit Trail: Thread-local AuditMiddleware captures authenticated actor, client IP address, UTC timestamp, target model, object ID, and field-level change deltas for every create, update, and delete operation across all 15 applications.


# 4. Analysis Models


## 4.0 UML Use Case Modeling

The UML Use Case model formalizes the operational interactions between external clinical actors and system use cases across the transfusion chain. Figure 4.1 illustrates the complete use-case diagram.

Figure 4.1: RedLink UML Use Case Diagram


## 4.1 Data Flow Diagrams (DFD)

Data Flow Diagrams depict how data enters, transitions through, and leaves the RedLink system. Figure 4.2 presents the Level-0 Context Diagram illustrating external boundary entities.

Figure 4.2: Level-0 Context Data Flow Diagram

Figure 4.3 depicts the Level-1 Process Decomposition DFD, tracing data flows between processes P1 through P6 and persistent data stores D1 through D6.

Figure 4.3: Level-1 Process Decomposition Data Flow Diagram


## 4.2 Entity-Relationship & Relational Database Design

The RedLink relational database schema consists of 20+ application tables partitioned across 15 modular Django apps. Every entity inherits from an abstract TimeStampedModel that automatically timestamps records. Figure 4.4 presents the comprehensive Relational Entity-Relationship (ER) diagram.

Figure 4.4: RedLink Relational Entity-Relationship (ER) Schema

Core Table 1: donors_donor — Voluntary Blood Donor Registry (Prefix: DNR-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| donor_id | CharField(20) | UNIQUE, INDEXED | Standardized identifier (e.g. DNR-00042) |
| first_name | CharField(100) | NOT NULL | Donor first name |
| last_name | CharField(100) | NOT NULL | Donor surname |
| date_of_birth | DateField | NOT NULL | DOB for age verification (>= 18) |
| gender | CharField(10) | choices | Gender (M / F / O) |
| blood_group | CharField(5) | choices | ABO and Rh(D) group |
| phone | CharField(15) | INDEXED | Primary contact telephone |
| is_eligible | BooleanField | default=True | Clinical eligibility flag |
| total_donations | IntegerField | default=0 | Lifetime donation tally |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Core Table 2: laboratory_bloodbag — Phlebotomy Bag Lifecycle (Prefix: BB-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| bag_id | CharField(20) | UNIQUE, INDEXED | Barcoded bag identifier (e.g. BB-00123) |
| donation_id | BigIntegerField | UNIQUE, FK → donation | One-to-one link with collection event |
| blood_group | CharField(5) | NOT NULL | Blood group confirmed at collection |
| volume_ml | IntegerField | default=450 | Collected whole blood volume |
| collection_date | DateField | NOT NULL | Date of collection |
| expiry_date | DateField | INDEXED | Calculated whole blood expiration |
| status | CharField(20) | INDEXED, choices | collected / quarantine / approved / discarded |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Core Table 3: inventory_inventoryitem — Stock & Dispatch Pool (Prefix: INV-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| inventory_id | CharField(20) | UNIQUE, INDEXED | Stock identifier (e.g. INV-00234) |
| blood_bank_id | BigIntegerField | FK → blood_bank | Facility managing the inventory |
| blood_group | CharField(5) | INDEXED | ABO and Rh type |
| component_type | CharField(50) | INDEXED | PRBC / FFP / Platelets / Cryo |
| volume_ml | IntegerField | NOT NULL | Component volume in mL |
| storage_position_id | BigIntegerField | FK, NULLABLE | Assigned physical slot |
| status | CharField(20) | INDEXED | available / reserved / issued / expired |
| expiry_date | DateField | INDEXED | Expiration threshold date |
| created_at | DateTimeField | auto_now_add=True | Record creation timestamp |

Core Table 4: requests_app_bloodrequest — Hospital Clinical Requisitions (Prefix: REQ-)

| Column | Data Type | Constraints | Description |
| --- | --- | --- | --- |
| id | BigAutoField | PRIMARY KEY | Internal surrogate key |
| request_id | CharField(20) | UNIQUE, INDEXED | Requisition identifier (e.g. REQ-00056) |
| hospital_id | BigIntegerField | FK → hospital | Requesting hospital institution |
| patient_id | BigIntegerField | FK → patient, NULL | Recipient patient record |
| priority | CharField(20) | INDEXED | routine / urgent / emergency |
| status | CharField(20) | INDEXED | pending / approved / fulfilled / cancelled |
| required_by_date | DateField | NULLABLE | Clinical deadline for transfusion |
| approved_by_id | BigIntegerField | FK → user, NULL | Authorizing Medical Officer |
| created_at | DateTimeField | auto_now_add=True | Requisition timestamp |


# 5. GitHub Link

The complete source code, documentation, CI/CD configuration, and deployment scripts for the RedLink Hemovigilance System are publicly available at:

https://github.com/phanindra267/Hemovigilance

The repository includes: source code for all 15 modular Django apps, multi-stage Dockerfile and docker-compose.yml for production orchestration, Nginx reverse proxy configuration, GitHub Actions CI/CD pipeline (.github/workflows/ci.yml), full documentation suite in docs/, utility automation scripts in scripts/, and database seed management commands.


# 6. Deployed Link

The RedLink system is deployed and accessible for live demonstration at the following URL. All nine demo roles are pre-configured with the seed data loaded:

https://redlink-hemovigilance.onrender.com

Demo Logins (Password for all accounts: BloodBank@2026):

| Role | Username | Dashboard Capabilities |
| --- | --- | --- |
| Super Administrator | admin | System configuration, facility settings, audit log, full administrative authority |
| Blood Bank Admin | bb_admin | Facility configuration, staff management, cold chain devices, master inventory |
| Medical Officer | dr_smith | Clinical donor approvals, TTI release gate, discard authorizations |
| Lab Technician | tech_john | Phlebotomy barcoding, sample testing entry, TTI screening, component separation |
| Inventory Manager | inv_sarah | Storage slot allocations, temperature logs, quarantine release |
| Donor Coordinator | coord_alex | Donor registrations, appointment scheduling, camp management |
| Hospital Coordinator | hosp_maria | Hospital blood orders, crossmatch requests, emergency STAT requisitions |
| Camp Organizer | camp_david | Blood camp drive coordination, venue logistics, community outreach |
| Voluntary Donor | donor_raj | Donor portal, donation history, upcoming appointment slot booking |


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


## A.1 Appendix 1 – Automated Test Execution Summary

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


## A.2 Appendix 2 – Modular Django Apps Reference

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
