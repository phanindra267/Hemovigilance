# RedLink Documentation Hub

This directory contains the complete technical documentation, regulatory specifications, architectural models, and academic reports for the **RedLink – Blood Bank Management & Hemovigilance System**.

---

## Documentation Index

| Document | Format | Description |
|---|---|---|
| [`ProjectPresentation.pptx`](ProjectPresentation.pptx) | PowerPoint (.pptx) | Complete 24-Slide Redesigned Master Presentation (16:9 Widescreen, Clickable Navigation, 20 Embedded High-Res Graphics & Infographics, 70/30 Visual Balance, Viva-Ready) |
| [`ProjectPresentation.pdf`](ProjectPresentation.pdf) | PDF (.pdf) | Complete Presentation Slide Deck Export (24 High-Resolution Slides) |
| [`ProjectReport.pdf`](ProjectReport.pdf) | PDF (.pdf) | Complete Official IEEE Std 830-1998 Software Requirements Specification (28 Pages, 7 Embedded High-Res Diagrams) |
| [`ProjectReport.docx`](ProjectReport.docx) | Word (.docx) | Editable IEEE Std 830-1998 Software Requirements Specification with Client Proofs & Database Design |
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
