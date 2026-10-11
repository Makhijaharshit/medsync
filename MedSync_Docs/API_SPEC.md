# API Specification

## Auth
POST /auth/register
POST /auth/login
GET /auth/me

## Documents
GET /documents
POST /documents/upload
GET /documents/:id
POST /documents/:id/verify

## Timeline
GET /timeline

## Emergency
GET /emergency/profile
PUT /emergency/profile
POST /emergency/sos

## Doctor
GET /doctor/patient/:id
POST /doctor/events
