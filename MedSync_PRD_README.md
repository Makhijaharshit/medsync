# MedSync — Technical Product Requirements Document (PRD)

## 1. Product Overview

**MedSync** is a secure healthcare information platform designed around two core technical problems:

1. **Fragmented medical records** — medical information is distributed across hospitals, clinics, laboratories, prescriptions, PDFs, scanned documents, and different providers.
2. **Insufficient critical information during emergencies** — paramedics and emergency clinicians may not have immediate access to verified, relevant patient information.

MedSync combines:

- Intelligent medical-document ingestion and structuring
- A unified longitudinal medical timeline
- Role-based medical-record access
- A dedicated emergency medical profile
- Secure emergency access for authorized responders
- Emergency notification to configured contacts
- Emergency location sharing
- Consent, authorization, auditability, and security controls

The platform must be designed as an information and decision-support system, not as an autonomous diagnostic or treatment system.

---

## 2. Product Goals

### 2.1 Primary Goals

- Convert heterogeneous medical documents into structured, searchable medical information.
- Preserve a link between extracted data and its original source document.
- Build a longitudinal patient timeline from verified clinical events.
- Provide authorized clinicians with relevant patient history without requiring manual reconstruction.
- Provide emergency responders with a fast, minimal, emergency-specific patient profile.
- Detect or receive emergency events through explicitly supported triggers.
- Notify configured emergency contacts with an emergency message and the patient's location when an emergency event is confirmed.
- Maintain auditable records of medical-data access and emergency-data access.
- Support interoperability with healthcare systems using standards such as HL7 FHIR where practical.
- Keep the SIH prototype implementable using synthetic/sample data.

### 2.2 Non-Goals

- Autonomous diagnosis.
- Autonomous treatment recommendations.
- Replacing doctors, paramedics, hospitals, or emergency services.
- Public access to a patient's complete medical history.
- Unrestricted access through a static/public QR code.
- Storing or processing real patient data in the prototype unless appropriate authorization, security, and compliance requirements are satisfied.
- Replacing existing hospital information systems.

---

## 3. Core User Roles

### 3.1 Patient

Capabilities:

- Register/login.
- Maintain profile and identity information.
- Upload medical documents.
- View extracted information.
- Verify/correct extracted information.
- View medical timeline.
- Configure emergency profile.
- Configure emergency contacts.
- Enable/disable supported emergency triggers.
- Review consent and access history.
- Revoke permissions where applicable.
- View emergency events and notification history.

### 3.2 Doctor / Clinician

Capabilities:

- Authenticate using clinician credentials.
- Search or identify an authorized patient.
- Request/access permitted medical information.
- View structured medical history.
- View the longitudinal timeline.
- Open original source documents.
- Add clinical events or upload new records.
- Review AI-extracted information.
- Generate/view an authorized clinical summary.

### 3.3 Paramedic / Emergency Responder

Capabilities:

- Authenticate using responder credentials or approved emergency-access workflow.
- Identify a patient through the supported emergency mechanism.
- Access the emergency medical profile when authorized.
- View critical alerts, allergies, medications, conditions, procedures, and other configured emergency data.
- Request additional information when permitted.
- Record/associate an emergency event.
- All access must be logged.

### 3.4 Healthcare Provider / Hospital

Capabilities:

- Upload or contribute verified medical records.
- Associate records with a patient.
- Add clinical events.
- Access information according to organization and patient authorization policies.

### 3.5 System Administrator

Capabilities:

- Manage system configuration.
- Manage organizations and roles.
- Monitor system health.
- Review security/audit events according to administrative policy.

Administrators must not receive unrestricted access to clinical data by default.

---

# 4. Functional Requirements

## 4.1 Authentication and Identity

The system shall provide:

- Secure account creation/login.
- Multi-factor authentication for privileged roles.
- Role-based authorization.
- Session management.
- Account recovery.
- Device/session management.
- Optional stronger identity verification for production deployments.
- Patient identity matching before medical records are attached to a profile.

The emergency-access workflow must not rely solely on possession of an easily copied/static QR code.

---

## 4.2 Medical Document Ingestion

Supported input types should include:

- PDF
- JPEG/PNG scans
- Images of prescriptions/reports
- Digitally generated reports
- Structured healthcare data when available

Pipeline:

```text
Upload
  ↓
Virus/malware validation
  ↓
Document classification
  ↓
OCR (if required)
  ↓
Text normalization
  ↓
Medical entity extraction
  ↓
Field normalization
  ↓
Confidence scoring
  ↓
Patient/clinician verification
  ↓
Structured record
  ↓
Timeline indexing
```

The original document must remain available as a source artifact subject to access permissions and retention policies.

---

## 4.3 AI Medical Information Extraction

The extraction service may identify:

- Diagnoses
- Conditions
- Medications
- Dosage/frequency where available
- Allergies
- Symptoms
- Laboratory observations
- Procedures
- Surgeries
- Hospitalizations
- Immunizations where available
- Clinical dates
- Healthcare organizations
- Providers
- Important medical alerts

Every extracted field should support:

- Source document reference
- Source page/region where technically possible
- Extraction timestamp
- Model/version identifier
- Confidence score
- Verification state

Example:

```json
{
  "field": "allergy",
  "value": "Penicillin",
  "sourceDocumentId": "doc_123",
  "sourceLocation": {
    "page": 2
  },
  "confidence": 0.96,
  "verificationStatus": "patient_verified",
  "extractedBy": "medical-ner-v2"
}
```

AI extraction must not silently overwrite verified clinical information.

---

## 4.4 Structured Medical Record

A patient's structured record should support entities such as:

```text
Patient
 ├── Conditions
 ├── Allergies
 ├── Medications
 ├── Procedures
 ├── Investigations
 ├── Hospitalizations
 ├── Clinical Events
 ├── Documents
 ├── Emergency Profile
 ├── Emergency Contacts
 └── Access/Consent Records
```

Clinical data should support temporal fields such as:

- Event date
- Start date
- End date
- Recorded date
- Last verified date

Where appropriate, data should distinguish between:

- Patient-reported
- Clinician-entered
- Hospital-provided
- AI-extracted
- Verified
- Unverified
- Historical
- Current/active

---

# 5. Smart Clinical Timeline

The platform shall construct a chronological clinical timeline.

Example:

```text
2019
 └── Diabetes diagnosis

2021
 └── Medication initiated

2023
 └── Blood investigation

2024
 └── Hospital admission

2025
 └── Medication changed

2026
 └── Current clinical status
```

Requirements:

- Sort clinical events chronologically.
- Group related events where appropriate.
- Allow filtering by event type.
- Allow filtering by date range.
- Allow opening the original source.
- Display verification status.
- Distinguish active vs historical information.
- Prevent unsupported inference from being presented as confirmed clinical history.

---

# 6. Clinical Summary

For authorized clinicians, MedSync may generate a concise summary from structured and verified information.

Summary should prioritize:

- Active conditions
- Current medications
- Allergies
- Recent hospitalizations
- Recent investigations
- Major procedures
- Significant historical events
- Relevant timeline changes

Requirements:

- Summary must be traceable to source records.
- Generated content must be clearly marked as AI-assisted.
- Clinicians must be able to inspect underlying records.
- The system must not present an AI summary as a medical diagnosis.

---

# 7. Emergency Medical Profile

The emergency profile is a deliberately smaller data view than the full medical record.

Recommended fields:

### Identity

- Patient name
- Age/date of birth where appropriate
- Emergency identifier

### Critical Information

- Blood group, if verified/available
- Severe allergies
- Critical medications
- Important chronic conditions
- Major surgeries/procedures
- Important implanted devices, if available
- Critical medical alerts
- Other patient-configured emergency information

### Contacts

- Emergency contacts
- Relationship
- Contact number

The UI must prioritize critical alerts visually and place them before non-critical information.

---

# 8. Emergency Access

## 8.1 Access Model

Emergency access must support:

- Responder authentication where available.
- Patient identification.
- Authorization checks.
- Minimum-necessary data exposure.
- Time-limited access where appropriate.
- Full audit logging.

A QR code should act as an identifier/access mechanism, not as a public database containing medical information.

Recommended flow:

```text
Emergency Identifier
        ↓
Patient Identification
        ↓
Responder Authentication / Verification
        ↓
Authorization Check
        ↓
Emergency Profile
        ↓
Optional Additional Access
        ↓
Audit Log
```

## 8.2 Break-Glass Access

If emergency conditions require access beyond normal consent:

- The responder must explicitly initiate emergency access.
- A reason/category should be captured.
- Access should be limited to necessary information.
- The event must be logged.
- The patient should be notified where operationally appropriate.
- Repeated or suspicious emergency access should be detectable by audit systems.

Production implementation must be adapted to applicable healthcare privacy laws, institutional policy, and deployment requirements.

---

# 9. Emergency Detection and Alerting

MedSync should support multiple emergency triggers without assuming that the platform can independently determine that an accident has occurred.

## 9.1 Supported Trigger Types

### A. Manual SOS

The patient presses an SOS button in the MedSync application.

### B. Integrated Device Trigger

A future version may receive an emergency event from an authorized wearable/device capable of detecting events such as a severe fall or impact.

The device event should be treated as a trigger requiring configurable confirmation logic rather than unquestioned proof of an accident.

### C. Authorized External Trigger

An integrated healthcare/emergency system may submit an emergency event through a secure API.

---

# 10. Emergency Contact Notification

When an emergency event is confirmed, MedSync shall notify configured emergency contacts.

Notification should contain only the minimum necessary information.

Example:

```text
EMERGENCY ALERT

An emergency event has been triggered for:
[Patient Name]

Possible emergency detected / SOS activated.

Location:
[Map/Location Link]

Time:
[Timestamp]

Please contact the patient or emergency services if appropriate.
```

The exact message must be configurable and must not make unsupported claims such as "accident confirmed" when the system only detected a possible event.

## 10.1 Notification Channels

Prototype:

- SMS or simulated SMS
- Push notification
- Email

Production:

- SMS gateway
- Push notification service
- Email service
- Optional integration with approved emergency-service infrastructure

## 10.2 Notification Rules

- Patient can configure emergency contacts.
- Contacts must be verified where feasible.
- Multiple contacts may be configured.
- Notification attempts must be logged.
- Delivery status should be tracked.
- Failed delivery should be visible to the system.
- The system should avoid repeatedly notifying contacts for the same event.
- Contact information must be encrypted/protected.

---

# 11. Emergency Location Sharing

When an emergency event is triggered and location permission has been granted, MedSync should capture the device's current location.

Data:

```text
Latitude
Longitude
Timestamp
Accuracy
Source
```

Example:

```json
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "accuracyMeters": 18,
  "capturedAt": "2026-08-11T18:10:00+05:30",
  "source": "mobile_gps"
}
```

The emergency contact notification may contain a secure location link.

Requirements:

- Location must only be collected according to explicit permission and applicable platform rules.
- Location must be encrypted in transit and at rest.
- Location access must be logged.
- Location retention must be configurable.
- The system should display timestamp and accuracy.
- If current location is unavailable, the system should not fabricate one.
- The system may optionally provide the most recent known location, clearly labeled with its timestamp, if the patient has enabled this feature.

---

# 12. Emergency Event State Machine

Recommended states:

```text
IDLE
  ↓
TRIGGERED
  ↓
AWAITING_CONFIRMATION
  ├── CANCELLED
  └── CONFIRMED
          ↓
    LOCATION_CAPTURED
          ↓
    CONTACTS_NOTIFIED
          ↓
    RESPONDER_ACCESS
          ↓
    RESOLVED
```

For a manual SOS, confirmation may be immediate.

For automated/device-based detection:

```text
Possible Event
     ↓
Confirmation Window
     ├── User cancels → CANCELLED
     └── No cancellation / confirmed → CONFIRMED
```

This reduces false emergency notifications.

---

# 13. Emergency Access vs Emergency Notification

These must be treated as separate capabilities.

### Emergency Notification

Purpose:

> Tell configured contacts that an emergency event has occurred and provide location when available.

Recipient:

> Patient-configured emergency contacts.

### Emergency Medical Access

Purpose:

> Give authorized responders critical patient medical information.

Recipient:

> Authorized paramedics/emergency clinicians.

One must not automatically imply the other.

---

# 14. Consent and Permission Model

Permission categories should include:

```text
PROFILE_ACCESS
MEDICAL_RECORD_ACCESS
EMERGENCY_PROFILE_ACCESS
EMERGENCY_LOCATION_ACCESS
EMERGENCY_CONTACT_NOTIFICATION
DOCUMENT_ACCESS
CLINICAL_SUMMARY_ACCESS
```

Each permission should support:

- Granted/revoked status
- Scope
- Grantor
- Recipient/role
- Timestamp
- Expiration where applicable
- Audit reference

Emergency access should follow a separately defined emergency policy.

---

# 15. Security Requirements

## 15.1 Data Security

- TLS for all network communication.
- Encryption at rest.
- Secure secret management.
- Password hashing using a modern password-hashing algorithm.
- Token expiration and rotation.
- Secure session management.
- API authentication.
- Input validation.
- File-type validation.
- Malware scanning for uploaded documents.
- Rate limiting.
- Protection against common web/API attacks.

## 15.2 Authorization

Use RBAC plus resource-level authorization.

Example:

```text
Patient A
   ↓
Own Records

Doctor B
   ↓
Only Authorized Patient Records

Paramedic C
   ↓
Emergency Profile
   +
Emergency Authorization

Admin D
   ↓
System Metadata / Operational Data
```

Do not rely only on frontend restrictions. Authorization must be enforced server-side.

## 15.3 Audit Logging

Log events such as:

- Login
- Failed login
- Document upload
- Document access
- Record modification
- Consent change
- Emergency trigger
- Location capture
- Emergency notification
- Emergency-profile access
- Break-glass access
- Permission change

Audit events should contain:

```text
actorId
actorRole
patientId/resourceId
action
timestamp
reason/context
result
sourceIP/device metadata where appropriate
```

Audit logs should be tamper-resistant and access-controlled.

---

# 16. Data Model

A conceptual relational model:

```text
User
 ├── PatientProfile
 ├── ClinicianProfile
 └── ResponderProfile

Patient
 ├── MedicalDocument
 ├── ClinicalEvent
 ├── Condition
 ├── Medication
 ├── Allergy
 ├── Procedure
 ├── Investigation
 ├── EmergencyProfile
 ├── EmergencyContact
 ├── Consent
 ├── EmergencyEvent
 └── AccessAudit

EmergencyEvent
 ├── Trigger
 ├── Location
 ├── Notification
 └── EmergencyAccess
```

Suggested tables/entities:

- users
- roles
- patients
- clinicians
- organizations
- medical_documents
- document_extractions
- conditions
- medications
- allergies
- procedures
- investigations
- clinical_events
- emergency_profiles
- emergency_contacts
- emergency_events
- emergency_locations
- emergency_notifications
- consents
- access_audits
- devices
- sessions

---

# 17. Suggested API Architecture

Example REST endpoints:

```text
POST   /auth/register
POST   /auth/login
POST   /auth/refresh

POST   /patients
GET    /patients/{patientId}

POST   /patients/{patientId}/documents
GET    /patients/{patientId}/documents
GET    /documents/{documentId}

POST   /documents/{documentId}/extract
GET    /documents/{documentId}/extraction

GET    /patients/{patientId}/timeline
GET    /patients/{patientId}/summary

GET    /patients/{patientId}/emergency-profile
PUT    /patients/{patientId}/emergency-profile

GET    /patients/{patientId}/emergency-contacts
POST   /patients/{patientId}/emergency-contacts
DELETE /patients/{patientId}/emergency-contacts/{contactId}

POST   /emergency/events
GET    /emergency/events/{eventId}

POST   /emergency/events/{eventId}/confirm
POST   /emergency/events/{eventId}/cancel

POST   /emergency/events/{eventId}/location
POST   /emergency/events/{eventId}/notify

POST   /emergency/access
GET    /emergency/access/{accessId}

GET    /patients/{patientId}/consents
POST   /patients/{patientId}/consents
DELETE /patients/{patientId}/consents/{consentId}

GET    /patients/{patientId}/audit
```

API responses must enforce authorization before returning patient data.

---

# 18. Interoperability

The architecture should support healthcare interoperability instead of creating an isolated data silo.

Consider:

- HL7 FHIR resources
- Patient
- Observation
- Condition
- MedicationRequest / MedicationStatement as appropriate
- AllergyIntolerance
- Procedure
- DiagnosticReport
- DocumentReference
- Encounter

Original documents should be represented through appropriate document references while structured clinical information is stored in normalized form.

The implementation should allow future integration with hospitals, laboratories, healthcare providers, and India's digital-health ecosystem without requiring a complete rewrite.

---

# 19. Technology Stack

A practical SIH prototype could use:

## Frontend

- React / Next.js for web
- React Native or Flutter if mobile application is required

## Backend

- FastAPI / Python or Node.js / TypeScript
- REST APIs
- WebSocket or server-sent events if real-time emergency status is needed

## Database

- PostgreSQL for structured healthcare data
- Redis for short-lived sessions/caching
- Object storage for original documents

## Search

- PostgreSQL full-text search initially
- OpenSearch/Elasticsearch if scale requires it

## AI

- OCR engine
- Medical NER/information extraction model
- LLM-based normalization/summarization with strict source grounding
- Validation layer

## Notifications

- SMS provider
- Push notification provider
- Email provider

## Maps/Location

- Device GPS
- Mapping provider for secure location visualization

## Authentication

- OAuth 2.0 / OpenID Connect where applicable
- JWT or secure server-side sessions
- MFA for privileged roles

For the SIH prototype, individual components can be simplified while keeping the interfaces modular.

---

# 20. AI Processing Architecture

```text
Medical Document
      ↓
Document Classifier
      ↓
OCR / Text Extraction
      ↓
Medical NLP
      ↓
Entity Normalization
      ↓
Clinical Data Validator
      ↓
Confidence Scoring
      ↓
Human Verification
      ↓
Structured Medical Record
      ↓
Timeline / Search / Summary
```

The AI layer must not directly publish unverified critical medical information into the emergency profile.

Recommended rule:

```text
AI Extracted
    ↓
Verification Required
    ↓
Verified
    ↓
Eligible for Emergency Profile
```

Critical fields such as allergies should have stricter verification policies.

---

# 21. Emergency Notification Architecture

```text
Emergency Trigger
      ↓
Event Validation
      ↓
Confirmation / False-Alarm Window
      ↓
Emergency Event Created
      ↓
Permission Check
      ↓
Location Capture
      ↓
Emergency Contact Resolution
      ↓
Notification Service
      ├── SMS
      ├── Push
      └── Email
      ↓
Delivery Status
      ↓
Audit Log
```

The notification service must be asynchronous so that failure of one provider does not block emergency-event creation.

---

# 22. Emergency Contact Data

Each emergency contact should contain:

```json
{
  "contactId": "ec_001",
  "patientId": "patient_001",
  "name": "Emergency Contact",
  "relationship": "Parent",
  "phone": "+91XXXXXXXXXX",
  "email": "contact@example.com",
  "priority": 1,
  "verified": true,
  "notificationChannels": [
    "SMS",
    "PUSH"
  ],
  "active": true
}
```

Do not expose emergency-contact information to unauthorized users.

---

# 23. Emergency Location Data

Each location record should contain:

```json
{
  "locationId": "loc_001",
  "emergencyEventId": "evt_001",
  "latitude": 0.0,
  "longitude": 0.0,
  "accuracyMeters": 20,
  "capturedAt": "ISO-8601 timestamp",
  "source": "mobile_gps"
}
```

Avoid storing continuous location history unless it is explicitly required and consented to. Emergency location should be event-based by default.

---

# 24. Emergency False-Positive Handling

Automated emergency detection may produce false positives.

Therefore:

- Device-based detection should support a cancellation period.
- Patient should receive an audible/visual confirmation request where feasible.
- Contacts should not receive repeated alerts for the same event.
- Event state must be persisted.
- False-positive events should be recorded separately from confirmed emergencies.
- Automated detection should never claim certainty when the input is probabilistic.

---

# 25. Availability and Failure Handling

Emergency functionality must degrade gracefully.

Examples:

### GPS unavailable

Use:

```text
No current location available
```

Optionally include last known location with timestamp if enabled.

### SMS provider unavailable

Attempt configured alternative notification channel.

### Internet unavailable

Mobile client may queue an emergency event and retry when connectivity returns, subject to platform capabilities.

### Medical database unavailable

Do not display stale or fabricated information as current. Cache only explicitly approved emergency data under an appropriate security model.

### AI service unavailable

Document upload should still succeed; extraction can be queued for later.

---

# 26. Observability

Monitor:

- API latency
- Error rate
- Authentication failures
- Document-processing failures
- OCR failures
- AI extraction failures
- Emergency-event creation latency
- Notification delivery latency
- Notification failure rate
- Location capture success rate
- Unauthorized-access attempts
- Database health
- Queue health

Emergency workflows should have dedicated monitoring and alerting.

---

# 27. Scalability

The architecture should allow independent scaling of:

- API services
- Document processing workers
- OCR workers
- AI inference workers
- Notification workers
- Search services
- Database read replicas
- Object storage

Use asynchronous queues for computationally expensive tasks such as:

- OCR
- AI extraction
- document indexing
- notification delivery

---

# 28. MVP Scope

The SIH prototype should implement:

### Patient

- Registration/login
- Document upload
- OCR
- AI extraction of selected fields
- Verification/editing
- Timeline
- Emergency profile
- Emergency contacts
- Emergency QR/identifier
- Manual SOS
- Location capture
- Emergency-contact notification
- Access history

### Doctor

- Login
- Patient lookup with authorization
- Timeline
- Structured medical information
- Original-document access
- Add/update clinical events

### Paramedic

- Responder login/verification
- Emergency patient identification
- Emergency profile
- Critical alerts
- Controlled emergency access
- Emergency access audit

### Backend

- Authentication
- RBAC
- Consent
- Medical-record APIs
- Emergency-event service
- Location service
- Notification service
- Audit service

### AI

- OCR
- Document classification
- Medical entity extraction
- Basic normalization
- Source-linked extraction
- Timeline generation
- Basic source-grounded summary

---

# 29. Production Extensions

Potential future capabilities:

- Hospital information-system integrations
- Laboratory integrations
- Wearable/device integrations
- Advanced accident/fall detection
- More sophisticated emergency routing
- Interoperable FHIR APIs
- Digital identity integration
- Advanced consent management
- Multilingual medical-document processing
- Offline emergency workflows
- Regional/organization-specific emergency policies
- Advanced clinical search
- Medical-record deduplication
- Cross-provider data reconciliation

---

# 30. Technical Acceptance Criteria

The MVP should satisfy at minimum:

### Medical Records

- A PDF/image can be uploaded successfully.
- OCR can extract text from supported documents.
- Selected medical entities can be extracted.
- Each extracted entity has a source reference.
- A user can verify/edit extracted information.
- Verified information appears in the timeline.
- Original documents remain accessible to authorized users.

### Emergency

- A patient can configure emergency contacts.
- A patient can configure an emergency profile.
- Manual SOS can create an emergency event.
- The system can capture device location when permission/connectivity allow it.
- Configured contacts receive an emergency notification through the implemented channel.
- Notification includes timestamp and location when available.
- Emergency responders can access the emergency profile through the authorized workflow.
- Emergency access is logged.
- Break-glass access, if implemented, records a reason.
- Unauthorized users cannot access medical information.

### Security

- APIs enforce server-side authorization.
- Sensitive data is encrypted in transit.
- Sensitive data is encrypted at rest where applicable.
- Authentication tokens/sessions are protected.
- Access events are auditable.
- Public possession of an emergency QR does not expose the complete medical record.

---

# 31. Key Architectural Principle

MedSync should maintain a strict separation between:

```text
RAW MEDICAL DOCUMENTS
        ↓
STRUCTURED MEDICAL DATA
        ↓
VERIFIED CLINICAL TIMELINE
        ↓
┌──────────────────────────────┐
│                              │
NORMAL CLINICAL VIEW     EMERGENCY VIEW
│                              │
Full authorized history   Critical minimum data
│                              │
Doctor/Patient             Authorized Responder
└──────────────────────────────┘
```

The emergency view should be optimized for **minimum necessary information, speed, security, and reliability**.

The emergency notification layer is separate:

```text
EMERGENCY EVENT
   ├── Emergency Medical Access
   │       └── Authorized responder
   │
   └── Emergency Notification
           ├── Emergency contacts
           └── Location (if available/authorized)
```

This separation is a core architectural requirement.

---

# 32. Core Product Definition

**MedSync is a secure, AI-assisted medical information platform that transforms fragmented healthcare documents into a verified longitudinal patient record and provides a separate emergency layer that enables authorized responders to access critical patient information while notifying configured emergency contacts with the patient's emergency status and location when available.**
