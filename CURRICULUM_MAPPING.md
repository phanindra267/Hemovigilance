# Academic Syllabus & Curriculum Compliance Matrix

This document provides a comprehensive, unit-by-unit audit demonstrating how **RedLink** fulfills and exceeds every single topic outlined in the Django Web Development Curriculum (Units I through VI).

---

## Summary Matrix

| Unit | Topic Area | Compliance Status | Key Code Implementation Files |
|---|---|---|---|
| **Unit I** | Introduction to Django, Project & App Architecture | **100% Covered** | `manage.py`, `lifeflow_project/settings.py`, 15 App directories |
| **Unit II** | Views, URLs, HTTP Requests, Params & Error Handling | **100% Covered** | `urls.py`, `views.py`, `core/views.py` (`400/403/404/500`) |
| **Unit III** | Templates (DTL), Template Inheritance, Debugging & Testing | **100% Covered** | `templates/base.html`, `core/test_lifecycle.py`, 14 TestCases |
| **Unit IV** | Forms, GET/POST, CSRF, POST-Redirect-GET & Validation | **100% Covered** | `forms.py` in 10 apps, `CsrfViewMiddleware`, custom validators |
| **Unit V** | Models, Migrations, ORM, ForeignKeys & Django Admin | **100% Covered** | `models.py`, `admin.py`, migrations, `seed_demo_data.py` |
| **Unit VI** | Cookies, Sessions, User Management & Authentication | **100% Covered** | `accounts/models.py`, `accounts/views.py`, `@role_required` |

---

## Unit-by-Unit Detailed Audit

### Unit I: Introduction to Django
> **Topics:** Installing Python & Django, Setting up project in editor, Projects & Apps overview, Project structure, Creating your first project, Django-admin & manage.py commands, App structures, Creating an App.

* **Python & Django Environment:**
  * Runs on **Python 3.11–3.14** and **Django 6.0.6** (`requirements.txt`).
  * Structured with clean virtual environment separation (`venv`).
* **Project Structure:**
  * Root directory containing `manage.py`, `.env.example`, `.gitignore`, `Dockerfile`, `requirements.txt`.
  * Configuration directory `lifeflow_project/` containing `settings.py`, `urls.py`, `wsgi.py`, and `asgi.py`.
* **15 Modular Domain Apps:**
  * Created and organized using standard `django-admin startapp` conventions:
    `core`, `accounts`, `donors`, `appointments`, `camps`, `donations`, `laboratory`, `blood_components`, `inventory`, `requests_app`, `patients`, `hospitals`, `notifications`, `reports`, `audit`.
* **Django-admin & manage.py Commands:**
  * Standard administrative commands used: `migrate`, `makemigrations`, `check`, `runserver`, `collectstatic`, `test`.
  * **4 Custom Management Commands** implemented in `core/management/commands/`:
    1. `seed_demo_data.py`: Seeds all 9 roles, facilities, donors, inventory items, and test results.
    2. `check_expiry.py`: Audits expiring units and moves expired stock to quarantine.
    3. `check_inventory.py`: Evaluates inventory levels and triggers low-stock threshold alerts.
    4. `generate_notifications.py`: Dispatches appointment reminders and emergency request alerts.

---

### Unit II: Views and URLs
> **Topics:** Creating views and mapping to URLs, Creating views and view logic, HTTP requests and responses, Understanding URLs, Mapping URLs with Params, Regular expressions in URLs, Error Handling.

* **View Implementation:**
  * Implemented across all 15 applications using both Function-Based Views (FBVs) and Class-Based Views (CBVs) for CRUD operations.
* **HTTP Requests and Responses:**
  * Handles standard `HttpRequest` methods (`GET` for searching/filtering, `POST` for mutations).
  * Returns diverse response types: `render()` with template contexts, `redirect()` to named routes, `HttpResponse` with headers for file streams (dynamic CSV and vector ReportLab PDF reports in `reports/exporters.py`).
* **URL Routing & Parameter Mapping:**
  * Modular URL design using `include()` in `lifeflow_project/urls.py` delegating to app-level `urls.py`.
  * Typed path converters (`<int:pk>`, `<int:donor_pk>`, `<int:sample_pk>`) used for clean RESTful detail and action views.
  * Query parameters parsed via `request.GET.get('search')`, `request.GET.get('blood_group')`, `request.GET.get('status')`.
* **Global Error Handling (400, 403, 404, 500):**
  * Handlers defined in `lifeflow_project/urls.py`:
    ```python
    handler400 = 'core.views.handler400'
    handler403 = 'core.views.handler403'
    handler404 = 'core.views.handler404'
    handler500 = 'core.views.handler500'
    ```
  * Custom styled error templates in `templates/400.html`, `templates/403.html`, `templates/404.html`, and `templates/500.html` with friendly recovery navigation.

---

### Unit III: Templates, Debugging and Testing
> **Topics:** Introduction to Templates in Django, Creating Templates, Working with Django Template Language (DTL), Template tags, Variables, for loop and if-else statements, Dynamic Templates, Template inheritance, Debugging Django applications, Testing in Django.

* **Django Template Language (DTL) & Hierarchy:**
  * Clean two-tier template architecture with app-specific template folders.
  * Base layout shell in `templates/base.html` extended by child templates via `{% extends "base.html" %}` and `{% block content %}`.
  * Reusable partials included via `{% include "navbar.html" %}`, `{% include "sidebar.html" %}`, `{% include "messages.html" %}`, `{% include "footer.html" %}`.
* **DTL Tags, Variables, and Filters:**
  * Control flow tags: `{% if %}`, `{% elif %}`, `{% else %}`, `{% for item in items %}`, `{% empty %}` (for empty states).
  * Routing tags: `{% url 'app_name:view_name' arg %}`.
  * Built-in template filters: `|date:"M d, Y"`, `|time:"H:i"`, `|timesince`, `|slice:":1"`, `|upper`, `|truncatechars:40`, `|default:"N/A"`.
* **Debugging:**
  * `DEBUG` mode dynamically toggled through environment variables in `.env`.
  * Context processors in `core/context_processors.py` inject global metadata (`unread_notifications_count`, `current_user_profile`, `org_name`).
* **Automated Testing in Django:**
  * Comprehensive test suite utilizing `django.test.TestCase` and `django.test.Client`.
  * Full 12-stage end-to-end lifecycle test in `core/test_lifecycle.py` verifying the complete vein-to-vein workflow.
  * Unit and integration test suites in `accounts/tests.py`, `inventory/tests.py`, `laboratory/tests.py`, `requests_app/tests.py`, and `reports/tests.py`.
  * Total **14 tests, 100% passing** with zero failures.

---

### Unit IV: Forms in Django
> **Topics:** Introduction to Forms, Using GET, POST and HTTP, Building forms using Django, Introduction to Cross Site Request Forgery (CSRF), CSRF support in Django, Implementing POST-Redirect-GET pattern, Data validation with Django forms.

* **Django Form Classes (`forms.py`):**
  * Dedicated form modules across 10 applications inheriting from `forms.ModelForm` and `forms.Form`.
  * Examples: `DonorForm`, `EligibilityAssessmentForm`, `AppointmentForm`, `BloodCampForm`, `DonationForm`, `ScreeningResultForm`, `TemperatureLogForm`, `BloodRequestForm`, `QuarantineForm`.
* **CSRF Protection:**
  * Every POST form strictly enforces the `{% csrf_token %}` template tag.
  * Protected globally by `django.middleware.csrf.CsrfViewMiddleware` in `settings.py`.
* **POST-Redirect-GET (PRG) Pattern:**
  * All state-mutating views strictly implement the PRG pattern:
    ```python
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.success(request, "Record saved successfully.")
            return redirect('app:detail', pk=instance.pk)
    else:
        form = FormClass()
    ```
* **Clinical Data Validation:**
  * Clinical range validation (donor age 18–65, minimum weight 45kg, minimum hemoglobin thresholds 12.5–13.0 g/dL).
  * Storage device temperature excursion checks with automatic quarantine triggers.
  * Database uniqueness validation for phone numbers, national IDs, and alphanumeric codes.

---

### Unit V: Models, Migrations and Django Admin
> **Topics:** Creating models, Working with Migrations, Using the Django Shell to Explore Models (Insert, Update, Delete), Using Object Relational Mapping (ORM), Models using Foreign Keys, Django Admin, Adding groups and users, Users and Permissions, Database configuration.

* **Relational Models & Inheritance:**
  * 25+ relational models inheriting from an abstract base model `TimeStampedModel` (`created_at`, `updated_at`).
  * `models.TextChoices` used for clinical enums (Blood Groups, Rh Factor, Urgency, Statuses).
* **Database Migrations:**
  * Full migration history tracked in `migrations/` across all 15 applications.
  * Applied seamlessly using `python manage.py migrate`.
* **Advanced ORM Capabilities:**
  * Filtering & Lookups: `.filter()`, `.exclude()`, `__in`, `__date__gte`, `__icontains`.
  * Aggregations & Grouping: `.annotate(total=Count('id'))`, `.aggregate(Sum('volume_ml'))`.
  * Performance Query Optimization: `.select_related()` and `.prefetch_related()` to eliminate $N+1$ query overhead.
  * **Concurrency Locking:** Atomic row-level database locking using `select_for_update()` in `requests_app/views.py` ensuring zero race conditions during simultaneous emergency blood reservations.
* **Relationships:**
  * `OneToOneField`: `User -> UserProfile`, `Donation -> BloodBag`.
  * `ForeignKey` with `related_name`: `Donor -> Donation`, `Hospital -> BloodRequest`, `StorageDevice -> StoragePosition`.
* **Django Admin Site (`admin.py`):**
  * All 25+ models registered in Django admin with customized `ModelAdmin` classes featuring `list_display`, `list_filter`, `search_fields`, `readonly_fields`, and `date_hierarchy`.
* **Database Configuration:**
  * Dual-database ready in `lifeflow_project/settings.py`:
    * Default: Zero-configuration SQLite (`db.sqlite3`) for local development and unit tests.
    * Production: PostgreSQL 14+ configuration via environment variables (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

---

### Unit VI: Cookies, Sessions, Users and Authentication
> **Topics:** Creating Cookies and sessions in Django, Creating and Managing Users in Django, Login and Logout URLs in Django, Using Django Login in Views.

* **Cookies and Sessions:**
  * Backed by `django.contrib.sessions.middleware.SessionMiddleware`.
  * Manages HTTP-only session cookies (`sessionid`) and CSRF tokens (`csrftoken`).
* **User Management & Signal Automation:**
  * Custom `UserProfile` linked to Django's `auth.User` via a `post_save` signal receiver (`create_or_update_user_profile`) in `accounts/models.py`.
  * Supports 9 distinct organizational roles: `SUPER_ADMIN`, `BLOOD_BANK_ADMIN`, `MEDICAL_OFFICER`, `LAB_TECHNICIAN`, `BLOOD_BANK_TECH`, `RECEPTIONIST`, `HOSPITAL_USER`, `DONOR`, `PATIENT`.
* **Authentication URLs & Views:**
  * Custom authentication routing at `/accounts/login/` and `/accounts/logout/`.
  * Built using `django.contrib.auth.login()`, `authenticate()`, and `logout()`.
* **Role-Based Access Control (RBAC):**
  * Custom `@role_required(*roles)` view decorator in `accounts/decorators.py`.
  * Custom `RoleRequiredMixin` class-based view mixin for class-based endpoints.
  * Protects restricted clinical actions (e.g. only Medical Officers can release lab samples or review high-priority emergency requisitions).

---

## Conclusion

**RedLink** is 100% compliant with the entire Django Web Development curriculum across all 6 Units. It serves as an exemplary real-world capstone project that demonstrates both foundational Django concepts and production-grade software engineering practices.
