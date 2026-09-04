# LIFEFlow ? Blood Bank Management & Hemovigilance System

![Django Version](https://img.shields.io/badge/Django-6.0.6-green.svg)
![Python Version](https://img.shields.io/badge/Python-3.14.7-blue.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Build Status](https://img.shields.io/badge/Tests-14%20Passed-brightgreen.svg)
![Traceability](https://img.shields.io/badge/Traceability-Unit--Level-red.svg)

LIFEFlow is a complete, modular, production-ready Django web application designed for enterprise blood transfusion services, regional blood banks, and affiliated healthcare networks.

It models the entire lifecycle of blood donation and transfusion with unit-level cold chain traceability, validated state transitions, atomic concurrency-safe reservations, immutable audit logging, role-based access control, responsive Bootstrap 5 UI, and automated hemovigilance reporting.

---

## Table of Contents
1. [Core Principles & Medical Safety Boundary](#core-principles--medical-safety-boundary)
2. [Architecture & 15 Django Apps](#architecture--15-django-apps)
3. [User Roles & Access Control](#user-roles--access-control)
4. [Prerequisites & Installation](#prerequisites--installation)
5. [Configuration & Environment](#configuration--environment)
6. [Database Migrations & Demo Seeding](#database-migrations--demo-seeding)
7. [Running the Application](#running-the-application)
8. [Automated Testing](#automated-testing)
9. [Production Deployment Outline](#production-deployment-outline)
10. [Documentation Index](#documentation-index)

---

## Core Principles & Medical Safety Boundary

### The Traceable Lifecycle
`
Donor Registration
   ?
   ?
Eligibility Assessment (Weight, Hb, BP, Pulse, Deferral Rules)
   ?
   ?
Appointment / Walk-in Check-in
   ?
   ?
Donation Session & Phlebotomy (Volume, Bag Type, Phlebotomist)
   ?
   ?
Blood Bag (Unique ID: BB-YYYY-NNNNNN, Quarantined)
   ?
   ?
Laboratory Screening (ABO/Rh, HIV, HBV, HCV, Syphilis, Malaria)
   ?
   ?
Medical Officer Verification & Safety Release Gate
   ?
   ?
Component Processing & Separation (PRBC, Platelets, FFP, Cryo)
   ?
   ?
Unit-Level Inventory (Storage Area, Device, Rack, Shelf, Position)
   ?
   ?
Temperature Cold-Chain Monitoring & Excursion Logging
   ?
   ?
Hospital Blood Requisition (Routine, Urgent, STAT Emergency)
   ?
   ?
Medical Officer Review & Authorization
   ?
   ?
Atomic Concurrency-Safe Reservation (select_for_update Row Locking)
   ?
   ?
Crossmatch Confirmation & Dispatch Issue (ISS-YYYY-NNNNNN)
   ?
   ???> Transfusion & Bedside Receipt
   ?
   ???> Blood Return & Clinical Triage (Cold Chain Check, Disposition)
   ?
   ???> Authorized Biohazard Discard (Wastage Tracking & Manifest)
`

> [!IMPORTANT]
> **Medical Safety Boundary:** Medical and regulatory decisions are never hardcoded as arbitrary heuristics. Eligibility criteria, infectious disease testing rules, storage limits, and compatibility rules are implemented as configurable business rules that can be validated against approved blood centre Standard Operating Procedures (SOPs) and NBTC / WHO / FDA regulations.

---

## Architecture & 15 Django Apps

The codebase is split into 15 specialized applications:
- **core**: Blood bank organization master, configurable system parameters, base models, error handlers (400, 403, 404, 500), context processors.
- **ccounts**: Custom role-based authentication, user profiles, 9 distinct roles, role decorators, customized dashboard dispatcher.
- **donors**: Voluntary donor registry, demographic records, contact details, donor statuses, next eligible donation dates.
- **ppointments**: Appointment scheduling, time-slot management, check-in workflow, and cancellation tracking.
- **camps**: Mobile and corporate blood donation drives, organizer liaison, venue tracking, and donor registrations.
- **donations**: Phlebotomy collection records, bag types, volume metrics, adverse event logging.
- **laboratory**: Blood bag registry, sample tubes, TTI screening assays, reactive isolation, Medical Officer verification.
- **lood_components**: Component processing (Whole Blood, PRBC, Platelet, FFP, Cryoprecipitate), default shelf lives.
- **inventory**: Physical cold storage hierarchy (Area -> Device -> Position), automated expiry tracking, unit status transitions.
- **
equests_app**: Hospital requisitions, clinical triage, emergency STAT alerts, atomic reservations, issue generation, returns, and discards.
- **patients**: Transfusion recipient records, hospital MRN linkage, medical history.
- **hospitals**: Affiliated hospital directory, verification statuses, authorized representatives.
- **
otifications**: Real-time in-app notification alerts for low stock, expiring units, emergency requests, and lab actions.
- **
eports**: Operational reporting engine with date filtering, CSV export, and ReportLab PDF document generation.
- **udit**: Immutable regulatory audit logging of all entity updates, approvals, reservations, issues, and discards.

---

## User Roles & Access Control

LIFEFlow implements 9 distinct operational roles with restricted dashboards and permission gates:
1. **Super Administrator** (SUPER_ADMIN): Full system control, user account provisioning, system settings.
2. **Blood Bank Administrator** (BLOOD_BANK_ADMIN): Facility operations, staff management, audit trail inspection.
3. **Medical Officer** (MEDICAL_OFFICER): Donor eligibility assessment, lab screening verification, requisition approval, return disposition, discard sign-off.
4. **Laboratory Technician** (LAB_TECHNICIAN): Sample collection, TTI assay result entry, temperature logging.
5. **Blood Bank Technician** (BLOOD_BANK_TECH): Phlebotomy recording, component separation, cold storage management, reservation, and issue.
6. **Receptionist** (RECEPTIONIST): Donor registration, appointment scheduling, camp coordination, donor check-in.
7. **Hospital User** (HOSPITAL_USER): Blood requisitions, patient record entry, crossmatch status tracking.
8. **Donor** (DONOR): Personal donation history, certificate download, eligibility calendar, appointment booking.
9. **Patient** (PATIENT): Transfusion history and patient recipient records.

---

## Prerequisites & Installation

### Requirements
- Python 3.10 to 3.14
- Git
- SQLite (default for development) or PostgreSQL 14+ (for production)

### Setup Steps
`ash
# 1. Clone repository
git clone https://github.com/phanindra267/Hemovigilance.git
cd Hemovigilance

# 2. Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
`

---

## Configuration & Environment

Copy the example environment file:
`ash
cp .env.example .env
`

Configure parameters in .env:
`ini
DEBUG=True
SECRET_KEY=your-secure-random-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (default sqlite for local development)
DB_ENGINE=sqlite

# For PostgreSQL production:
# DB_ENGINE=postgresql
# DB_NAME=lifeflow_db
# DB_USER=lifeflow_user
# DB_PASSWORD=your_secure_password
# DB_HOST=localhost
# DB_PORT=5432
`

---

## Database Migrations & Demo Seeding

Run migrations and seed realistic synthetic test data across all 15 apps:
`ash
# Apply migrations
python manage.py migrate

# Seed complete synthetic demo data
python manage.py seed_demo_data

# Collect static assets
python manage.py collectstatic --noinput
`

### Pre-configured Demo Accounts
All seeded accounts use password: password123

| Username | Role | Full Name | Primary Responsibility |
|---|---|---|---|
| dmin | Super Administrator | Super Admin | Full System Configuration |
| b_admin | Blood Bank Admin | Vikram Malhotra | Operations & Compliance |
| doctor_rajesh | Medical Officer | Dr. Rajesh Khurana | Eligibility, Lab Sign-off, Issues |
| 	ech_priya | Laboratory Tech | Priya Sharma | Serological Screening & Assays |
| 	ech_arun | Blood Bank Tech | Arun Patel | Phlebotomy, Components, Storage |
| 
ecep_meena | Receptionist | Meena Iyer | Front Desk, Camps, Check-in |
| hospital_user| Hospital User | Dr. Sanjay Mehta | Hospital Requisitions (Metro Hosp) |
| donor_user | Voluntary Donor | Rahul Deshmukh | Donor Portal & Appointments |
| patient_user| Patient / Recipient | Ananya Sen | Patient Portal & Transfusions |

---

## Running the Application

Start the development web server:
`ash
python manage.py runserver
`
Navigate to: **http://127.0.0.1:8000/**

### Management Commands
`ash
# Audit cold-chain stock levels and detect low stock
python manage.py check_inventory

# Scan inventory for expired units and alert staff
python manage.py check_expiry

# Generate routine appointment and emergency alerts
python manage.py generate_notifications
`

---

## Automated Testing

Execute the complete automated test suite (14 test cases covering models, workflows, security, exports, and end-to-end integration):
`ash
python manage.py test
`

### Key Tested Scenarios:
- **Full End-to-End Lifecycle:** Donor -> Eligibility -> Phlebotomy -> Bag -> Lab -> Screening -> Medical Officer Verification -> Component Preparation -> Inventory -> Hospital Requisition -> Approval -> Atomic Concurrency Reservation -> Crossmatched Issue -> Return.
- **Negative Workflow Tests:** Rejection of expired units, blocking of quarantined units, double reservation prevention via row-level locks, reactive assay safety gating.
- **Security & RBAC:** Role-based access control permission gates (403 Forbidden on unauthorized access), CSRF protection.
- **Reporting Engine:** Validation of CSV data streams and ReportLab binary PDF file generation.

---

## Production Deployment Outline

### Recommended Stack
- **Web Server:** Nginx (reverse proxy, SSL termination, static file caching)
- **WSGI Application Server:** Gunicorn (with 4-8 worker processes)
- **Database:** PostgreSQL 16 with daily backup snapshotting
- **Static Assets:** WhiteNoise / CDN
- **Containerization:** Docker & Docker Compose (configs provided)

See [DEPLOYMENT.md](DEPLOYMENT.md) for full systemd service units, Nginx virtual hosts, and Docker configurations.

---

## Documentation Index
- [ARCHITECTURE.md](ARCHITECTURE.md): Comprehensive system architecture & domain design.
- [DATABASE.md](DATABASE.md): Data dictionary, ER model, constraints, and indexes.
- [WORKFLOWS.md](WORKFLOWS.md): Clinical and operational lifecycle procedures.
- [SECURITY.md](SECURITY.md): RBAC matrix, encryption, audit trails, and data hygiene.
- [TESTING.md](TESTING.md): Testing methodology, test cases, and execution guidelines.
- [DEPLOYMENT.md](DEPLOYMENT.md): Production deployment guides for Ubuntu/Linux, Docker, and Nginx.
- [API_OR_URL_REFERENCE.md](API_OR_URL_REFERENCE.md): Complete list of named routes, URL converters, and permissions.
