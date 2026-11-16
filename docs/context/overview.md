# Institutional Portal

> A Progressive Web App (PWA) for tertiary institutions to manage students, staff, attendance, grades, and examination results in one place.

---

## 1. Project Overview

### 1.1 Summary

**Institutional Portal** is a web-based, installable (PWA) academic management platform for universities, colleges, technical institutes, and other tertiary institutions. It centralises the records and day-to-day workflows that are usually scattered across spreadsheets, paper registers, notice boards, and disconnected systems: student and staff records, course registration, attendance, coursework marks, exam results, transcripts, and institutional communication.

The portal gives each type of user (students, lecturers, administrators, registrars, heads of department, and optionally parents/sponsors) a role-specific view of the same trusted data, accessible from any phone, tablet, or computer, including under poor or intermittent internet connectivity.

### 1.2 Problem Statement

Many tertiary institutions still depend on manual or fragmented processes:

- Attendance recorded on paper and tallied at the end of term, if at all.
- Marks and results compiled in spreadsheets, prone to errors, version conflicts, and delays.
- Students queuing at the registrar's office to confirm registration, results, or transcript status.
- Limited visibility for management into enrolment, staff workload, pass rates, and performance trends.
- Weak audit trails: it is hard to know who changed a mark, when, and why.
- Unreliable internet access, making purely online systems frustrating to use.
- **Heavy manual paperwork** that consumes staff time, slows decisions, and is easy to lose, duplicate, or falsify (see 1.2.1).

#### 1.2.1 The Manual Paperwork Problem

Day-to-day academic administration at many institutions still runs on paper: forms are filled by hand, signed, stamped, carried between offices, and filed in cabinets. This creates recurring problems:

| Paper-based process | Resulting problem |
|---------------------|-------------------|
| Paper attendance registers and sign-in sheets | Manual tallying, lost sheets, proxy signing, no real-time visibility |
| Handwritten mark sheets and result broadcast sheets | Transcription errors, slow collation, delayed result release |
| Paper course registration and add/drop forms | Queues, multiple signatures, lost forms, registration disputes |
| Result slips, transcripts, and clearance forms requested in person | Long waits, repeated trips to the registry, heavy front-desk workload |
| Hard-copy student and staff files | Physical storage costs, difficulty retrieving records, risk of fire/water damage and loss |
| Paper-based approvals (leave, deferment, remarking, change of programme, amendments to marks) | Slow, untraceable approval chains with no status visibility |
| Printed notices and circulars | Poor reach, late information, printing costs |
| Retyping the same data into several forms and registers | Duplication of effort and inconsistent records |

**Impact:** wasted staff hours, delays for students, high printing and storage costs, weak audit trails, inconsistent data, and limited ability to produce timely reports for management and regulators.

**How the portal addresses it:** replace paper forms, registers, and sign-offs with digital records and workflows. Data is captured once at the source and reused everywhere, approvals are routed electronically with a visible status, and documents such as result slips and transcripts are generated on demand as PDFs. Digital records become the source of truth, so paper is only produced when an official hard copy is genuinely required.

### 1.3 Vision

A single, reliable, accessible source of truth for academic and administrative records at an institution, one that largely replaces paper-based processes and works well even on low-end phones and weak connections.

### 1.4 Goals and Objectives

| # | Objective | Outcome |
|---|-----------|---------|
| 1 | Centralise student and staff records | One authoritative profile per person, with full academic/employment history |
| 2 | Digitise attendance | Lecturers mark attendance in seconds; students and admin see live rates |
| 3 | Streamline grading and results | Structured entry, moderation, approval, and publication of marks and exam results |
| 4 | Give students self-service access | Students view timetable, registration, attendance, results, and statements without visiting an office |
| 5 | Provide management insight | Dashboards and reports on enrolment, attendance, performance, and staff load |
| 6 | Ensure integrity and accountability | Role-based access control and a complete audit log of sensitive changes |
| 7 | Work in low-connectivity environments | Offline-capable PWA with background sync |
| 8 | Reduce manual paperwork | Paperless forms, registers, and approvals; data captured once and reused; documents generated on demand |

### 1.5 Target Users

| Role | Primary needs |
|------|---------------|
| **Student** | View profile, registered courses, timetable, attendance, results, fees/clearance status, notices |
| **Lecturer / Instructor** | Class lists, mark attendance, enter coursework and exam marks, view course analytics |
| **Head of Department / Dean** | Approve/moderate results, monitor attendance and performance, staff allocation |
| **Registrar / Academic Office** | Admissions records, course registration, result publication, transcripts, graduation lists |
| **Administrator (Super/Institution Admin)** | Users, roles, academic structure, system settings, audit logs |
| **Finance / Bursar (optional)** | Fees clearance status feeding into registration and exam eligibility |
| **Parent / Sponsor (optional)** | Read-only view of a linked student's attendance and results (with consent) |

### 1.6 Scope

#### In scope (core)

- **Identity and access**: authentication, role-based permissions, and optional multi-factor authentication.
- **Institution structure**: faculties/schools, departments, programmes, courses/units, academic years, semesters/terms.
- **Student management**: records, enrolment status, programme and year of study, registration per semester.
- **Staff management**: records, roles, departmental assignment, course allocation.
- **Attendance tracking**: per class session, per course, with summaries and eligibility thresholds.
- **Grades and assessments**: continuous assessment components, weights, and final grade computation.
- **Exam results**: entry, moderation, approval workflow, publication, and result slips.
- **Transcripts and statements**: generation of academic transcripts and results statements (PDF).
- **Notifications and announcements**: in-app, email, and optionally SMS and push notifications.
- **Reports and dashboards**: operational and management reporting with export.
- **Audit logging**: who did what, when, and from where.
- **Paperless workflows**: digital forms and electronic approvals (registration, add/drop, deferment, remarking, change of programme, clearance, leave requests), with status tracking and e-sign-off.
- **Document generation and digital archive**: on-demand result slips, transcripts, and letters as PDFs; scanned/uploaded supporting documents stored against the relevant record.

#### Candidate extensions (later phases)

- Timetable and venue scheduling
- Fees and payments integration, including mobile money
- Library and hostel/accommodation modules
- Learning management (LMS) integration
- Admissions and online application
- Alumni records and graduation management
- Parent/sponsor portal
- Staff leave and payroll integration
- Analytics for at-risk student early warning

#### Out of scope (initially)

- Full learning management (content delivery, quizzes, assignments)
- Full payroll and HR management
- Native mobile apps (the PWA covers mobile access)

### 1.7 Core Modules

```
Institutional Portal
├── Identity & Access
├── Academic Structure (faculties, departments, programmes, courses, terms)
├── Student Management
├── Staff Management
├── Attendance
├── Assessment & Grading
├── Examinations & Results
├── Transcripts & Documents
├── Communication (notices, notifications)
├── Reports & Analytics
└── Administration & Audit
```

### 1.8 Key Features

**For students**
- Personal dashboard with registered courses, attendance percentage, and latest results
- Semester course registration and registration confirmation
- Results and cumulative GPA/CGPA view, downloadable result slips
- Notices and deadline reminders

**For lecturers**
- Class lists per course and session
- Fast attendance marking (list, bulk, or QR-assisted), available offline
- Coursework and exam mark entry with import from CSV/Excel
- Course-level performance summary

**For academic leadership and registry**
- Results moderation and approval workflow (draft, submitted, approved, published)
- Locking of published results, with controlled amendments that require justification
- Transcript and certificate data generation
- Institution-wide dashboards (enrolment, attendance, pass rates, staff workload)

**Platform-wide**
- Installable PWA with offline support and background sync
- Responsive, mobile-first design with low-bandwidth friendliness
- Role-based access control and full audit trail
- Paperless workflows: digital request forms, multi-step approval chains, status tracking, and notifications at each step
- On-demand documents (result slips, transcripts, letters) with a verifiable reference or QR code
- Digital archive replacing physical student and staff files
- Data import/export (CSV, Excel, PDF)
- Multi-institution capability (optional): one deployment serving several institutions with separate data

### 1.9 Why a PWA

| Reason | Benefit |
|--------|---------|
| Installable from the browser | No app store dependency; one codebase for all devices |
| Offline-first capability | Attendance and mark entry continue without internet and sync later |
| Lightweight | Suits low-end devices and limited data bundles |
| Instant updates | No manual updates for users; easier maintenance for the team |
| Push notifications | Timely alerts on results, notices, and deadlines |

### 1.10 High-Level Architecture (proposed)

```
┌─────────────────────────────────────────────┐
│  Clients: Students · Staff · Admin (PWA)    │
│  Service Worker · Offline cache · Sync queue│
└───────────────────┬─────────────────────────┘
                    │ HTTPS
┌───────────────────▼─────────────────────────┐
│  Application / API layer                    │
│  Auth & RBAC · Business logic · Workflows   │
└───────┬───────────────┬──────────────┬──────┘
        │               │              │
┌───────▼──────┐ ┌──────▼─────┐ ┌──────▼──────────┐
│ Relational DB│ │ File/Object│ │ Background jobs │
│ (core data)  │ │ storage    │ │ Email/SMS/PDF   │
└──────────────┘ └────────────┘ └─────────────────┘
```

> The technology stack is intentionally left open at the overview stage. It will be decided in the technical design document.

### 1.11 Non-Functional Requirements

| Area | Requirement |
|------|-------------|
| **Security** | Role-based access, encrypted transport and storage of sensitive data, secure password policies, audit logging |
| **Privacy** | Compliance with applicable data protection law (e.g. Uganda's Data Protection and Privacy Act, 2019); least-privilege access to student data |
| **Performance** | Fast on low-end devices and slow networks; paginated and cached data |
| **Availability** | Reliable during peak periods (registration, results release) |
| **Offline support** | Core attendance and mark-entry workflows usable offline with conflict-safe sync |
| **Scalability** | Handle thousands of concurrent users during peak load |
| **Usability** | Simple, accessible UI (including accessibility standards) for varied digital literacy |
| **Auditability** | Immutable history for grade and record changes |
| **Backup and recovery** | Scheduled backups with tested restore procedures |
| **Interoperability** | Import/export and API access for integration with other systems |

### 1.12 Assumptions and Constraints

**Assumptions**
- Institutions can supply their academic structure, grading scales, and assessment rules.
- Users have at least a basic smartphone or shared computer access.
- Institutional leadership sponsors adoption and data migration.

**Constraints**
- Intermittent connectivity and data cost for many users.
- Varying grading systems across institutions (GPA scales, weighting, classification rules), so grading must be **configurable**.
- Sensitive academic data requires careful access control and handling.
- Existing data may be in inconsistent spreadsheet or paper formats.
- Some official processes may still legally or institutionally require signed or stamped hard copies, so the portal must support a hybrid period and printable, verifiable outputs.

### 1.13 Success Metrics

| Metric | Indicative target |
|--------|-------------------|
| Attendance recorded digitally | > 90% of sessions |
| Time from marks submission to results publication | Reduced by 50% or more |
| Student self-service usage (vs. office visits) | Majority of result and registration enquiries handled online |
| Grade-entry errors / amendments | Measurable reduction |
| Paper-based forms/registers replaced by digital workflows | > 80% of routine forms and registers |
| Average turnaround for common requests (e.g. result slip, registration approval) | Reduced from days to hours or minutes |
| Printing and physical storage costs | Measurable reduction per semester |
| Active user adoption (students and staff) | > 80% within first full semester |
| System uptime during results release and registration | ≥ 99% |

### 1.14 Delivery Approach (indicative phases)

| Phase | Focus | Key deliverables |
|-------|-------|------------------|
| **0. Discovery** | Requirements, institution workflows, grading rules | Requirements document, data model draft |
| **1. Foundation** | Auth, RBAC, academic structure, student and staff records | Working core with admin tools |
| **2. Attendance** | Session management, offline attendance, summaries | Attendance module (PWA, offline-ready) |
| **3. Assessment and results** | Grade entry, moderation workflow, result publication, transcripts | Results module and PDF outputs |
| **4. Insights and communication** | Dashboards, reports, notifications | Management reporting, notifications |
| **5. Pilot and rollout** | Pilot with one department or institution, training, feedback | Pilot report, production release |
| **6. Extensions** | Timetabling, fees, LMS integration, parent portal | Roadmap items by priority |

### 1.15 Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Poor connectivity | Low usage, data loss | Offline-first design, background sync, light assets |
| Resistance to change | Low adoption | Training, pilot champions, simple UX |
| Grading rule variability | Incorrect results | Configurable grading engine, validation, moderation workflow |
| Data migration quality | Inaccurate records | Import validation, reconciliation reports, phased migration |
| Security or privacy breach | Reputational and legal harm | RBAC, encryption, audit logs, security reviews |
| Peak-load failures (results release) | Downtime at critical moments | Load testing, caching, scalable deployment |
| Parallel paper and digital processes persist | Double work, benefits not realised | Set cut-over dates per process, leadership mandate, retire paper forms once digital is live |
| Scope creep | Delays | Phased roadmap, clear in/out-of-scope list |

### 1.16 Glossary

| Term | Meaning |
|------|---------|
| **PWA** | Progressive Web App: a web app that can be installed and works offline |
| **RBAC** | Role-Based Access Control |
| **CA** | Continuous Assessment (coursework, tests, assignments) |
| **GPA / CGPA** | Grade Point Average / Cumulative Grade Point Average |
| **Moderation** | Review and approval of marks before publication |
| **Transcript** | Official record of a student's courses and grades |
| **Paperless workflow** | A process (form, approval, filing) carried out digitally end to end instead of on paper |

---

*Document status: Draft v0.1: project overview. Next sections to follow: functional requirements, data model, user stories, technical design.*