# RedLink Documentation Hub

This directory contains the complete technical documentation, regulatory specifications, architectural models, and academic reports for the **RedLink – Blood Bank Management & Hemovigilance System**.

---

## Documentation Index

| Document | Format | Description |
|---|---|---|
| [`ProjectReport.docx`](ProjectReport.docx) | Word (.docx) | Complete IEEE Std 830-1998 Software Requirements Specification with Client Proofs & Database Design |
| [`ProjectReport.md`](ProjectReport.md) | Markdown | Complete SRS Report (text mirror) |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Markdown | Multi-tier architecture, component hierarchy (Mermaid), and 15-app separation of concerns |
| [`DATABASE.md`](DATABASE.md) | Markdown | Database specification, Mermaid ER diagram, indexing strategy, and identifier standards |
| [`WORKFLOWS.md`](WORKFLOWS.md) | Markdown | 12-stage vein-to-vein transfusion lifecycle state machine |
| [`SECURITY.md`](SECURITY.md) | Markdown | RBAC privilege boundaries, session security, CSRF protection, and audit middleware |
| [`TESTING.md`](TESTING.md) | Markdown | Automated test plan, test matrix, negative workflow checks, and CLI instructions |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Markdown | Cloud (Render/Railway), Docker Compose, traditional Ubuntu VPS, and local LAN access |
| [`API_OR_URL_REFERENCE.md`](API_OR_URL_REFERENCE.md) | Markdown | Comprehensive route catalog covering all 260+ system endpoints |
| [`CURRICULUM_MAPPING.md`](CURRICULUM_MAPPING.md) | Markdown | Academic syllabus compliance matrix across Units I through VI |
| [`screenshots/`](screenshots/) | Directory | Application UI walkthroughs and interface screenshots |

---

## Key System Concepts

- **12-Stage Lifecycle:** Donor Registration $\rightarrow$ Clinical Eligibility $\rightarrow$ Appointment $\rightarrow$ Phlebotomy $\rightarrow$ Quarantine $\rightarrow$ TTI Screening $\rightarrow$ Component Separation $\rightarrow$ Inventory $\rightarrow$ Requisition $\rightarrow$ Atomic Reservation $\rightarrow$ Issue/Dispatch $\rightarrow$ Transfusion/Audit.
- **Atomic Locking:** Concurrency-safe reservation using PostgreSQL `select_for_update()` inside `transaction.atomic()`.
- **Hemovigilance Compliance:** Universal thread-local audit trail (`audit.middleware.AuditMiddleware`) capturing actor, IP, timestamp, and field-level change deltas for every mutation.
