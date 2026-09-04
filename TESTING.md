# LIFEFlow Testing Strategy & Quality Assurance

## 1. Test Suite Overview
The project contains comprehensive unit and integration tests verifying every layer of the hemovigilance system:

| Test Module | Coverage | Status |
|---|---|---|
| core.test_lifecycle | Complete End-to-End Transfusion Lifecycle (12 stages) | Passed |
| ccounts.tests | Authentication, Login, Role Restrictions, 403 Forbidden | Passed |
| laboratory.tests | Blood Bag, Sample Tubes, TTI Reactive Rejections | Passed |
| inventory.tests | Cold Storage, Expiry Detection, Quarantine Release | Passed |
| 
equests_app.tests| Atomic Reservation, Double-Reservation Prevention, Discards | Passed |
| 
eports.tests | CSV Data Stream & ReportLab PDF Document Generation | Passed |

## 2. Executing Tests
`ash
# Run entire test suite
python manage.py test

# Run lifecycle integration test specifically
python manage.py test core.test_lifecycle

# Run with verbose output
python manage.py test -v 2
`

## 3. Negative Workflow Testing
- Attempting to issue an expired unit is strictly blocked with a safety error.
- Attempting to issue a quarantined unit is blocked.
- Attempting to approve a sample with reactive screening is forbidden.
- Unauthorized users accessing staff management routes are rejected with HTTP 403.
