# Architecture

## Routing

- /dashboard
- /documents
- /documents/upload
- /documents/[id]
- /timeline
- /emergency
- /doctor
- /paramedic
- /audit

## Layers
Frontend → REST API → PostgreSQL

## RBAC
Patient: own records
Doctor: authorized records
Paramedic: emergency profile only
