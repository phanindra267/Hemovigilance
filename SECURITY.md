# LIFEFlow Security & Hemovigilance Governance

## 1. Authentication & Authorization
- Django standard authentication with Argon2 / PBKDF2 password hashing.
- Explicit Role-Based Access Control (RBAC) enforced via @role_required decorators and RoleRequiredMixin.
- Superuser bypass permitted only for emergency system maintenance.

## 2. CSRF & Session Security
- All state-mutating requests (POST) require CSRF tokens.
- CsrfViewMiddleware enabled globally.
- Session cookies restricted to HttpOnly and SameSite=Lax (configurable to Secure in production HTTPS).

## 3. Immutable Audit Trail
- udit.middleware.AuditMiddleware captures the client IP and acting user on every HTTP request.
- log_audit() records every creation, modification, approval, reservation, issue, quarantine, and discard event.
- AuditLog records cannot be modified or deleted via Django admin.

## 4. Cold Chain Integrity Protection
- Physical storage devices enforce configurable temperature threshold warnings.
- Any unit experiencing a cold chain excursion is automatically locked into QUARANTINED state until formally released with written justification.
