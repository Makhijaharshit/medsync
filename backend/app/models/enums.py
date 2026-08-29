from enum import Enum


class RoleName(str, Enum):
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    RESPONDER = "RESPONDER"
    ADMIN = "ADMIN"


class OrganizationType(str, Enum):
    HOSPITAL = "HOSPITAL"
    CLINIC = "CLINIC"
    LAB = "LAB"
    EMS = "EMS"
    OTHER = "OTHER"
