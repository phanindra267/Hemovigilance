# Changelog

All notable changes to **RedLink – Blood Bank Management & Hemovigilance System** are documented here.

This project adheres to [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Planned
- Mobile-responsive PWA support
- SMS/WhatsApp notification integration
- Advanced analytics dashboard with Chart.js
- Multi-tenancy support for multiple blood banks
- REST API for third-party integrations

---

## [1.0.0] – 2026-11-16

### Added
- **Core System**: Blood bank management with configurable system settings
- **User Management**: Nine roles — Admin, Blood Bank Manager, Lab Technician, Donor Coordinator, Inventory Manager, Hospital Coordinator, Camp Organizer, Auditor, Receptionist
- **Donor Management**: Donor registration, eligibility assessment (DNR- prefix IDs)
- **Appointment System**: Donor appointment scheduling and status tracking (APT- prefix IDs)
- **Donation Workflow**: Complete donation recording and lifecycle management (DON- prefix IDs)
- **Laboratory Module**: Blood bag processing (BB-), lab sampling (SMP-), and screening results
- **Blood Component Processing**: Separation and tracking of blood components (CMPNT- prefix IDs)
- **Inventory Management**: Storage area/device/position hierarchy, inventory items (INV-), quarantine records (QRN-)
- **Blood Request Workflow**: Hospital blood requests (REQ-), item tracking, inventory reservations, discard records (DIS-)
- **Hospital & Patient Management**: Hospital registration and patient records (PAT- prefix IDs)
- **Blood Camp Management**: Outreach donation camp scheduling and coordination
- **Audit Trail**: Comprehensive action logging across all modules
- **Notifications**: In-app notification system
- **Reports**: Exportable reports module
- **CI/CD**: GitHub Actions workflow for automated testing
- **Docker**: Full containerized deployment with Nginx and PostgreSQL
- **Documentation**: README, Architecture, Database, Deployment, Security, Testing, Workflows guides

### Technical Stack
- Python 3.14, Django 6.0.6
- PostgreSQL (production), SQLite (development)
- Bootstrap 5 (UI), Gunicorn (WSGI), Nginx (reverse proxy)
- Docker Compose for containerized deployment

---

## [0.9.0] – 2026-11-01 (Pre-release / Internal Beta)

### Added
- Initial project scaffolding with 15 Django applications
- Base model with `created_at`, `updated_at` timestamps
- Authentication system with role-based access control
- Basic CRUD for core entities
- Initial database migrations

---

[Unreleased]: https://github.com/phanindra267/Hemovigilance/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/phanindra267/Hemovigilance/releases/tag/v1.0.0
[0.9.0]: https://github.com/phanindra267/Hemovigilance/releases/tag/v0.9.0
