# Database Schema

## users
- id UUID PK
- role
- email
- password_hash

## patients
- user_id FK
- blood_group
- dob

## medical_documents
- patient_id FK
- file_url
- ocr_text
- status

## medical_entities
- type
- value
- confidence
- verified

## emergency_events
- status
- latitude
- longitude

## audit_logs
- actor_id
- action
- timestamp
