import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import User, PatientProfile, EmergencyEvent
from backend.app.schemas.schemas import (
    EmergencyProfileOut,
    EmergencyProfileUpdate,
    SOSCreate,
    EmergencyEventOut,
)
from backend.app.routers.deps import get_current_user
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/emergency", tags=["Emergency & SOS"])

def parse_json_safely(val, default):
    if not val:
        return default
    try:
        return json.loads(val)
    except Exception:
        return default

@router.get("/profile", response_model=EmergencyProfileOut)
def get_emergency_profile(
    patient_id: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = current_user.id
    if current_user.role in ["paramedic", "doctor", "admin"] and patient_id:
        target_id = patient_id

    patient_user = db.query(User).filter(User.id == target_id).first()
    if not patient_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == target_id).first()
    if not profile:
        profile = PatientProfile(user_id=target_id, blood_group="Unknown")
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Audit log if viewed by paramedic or doctor
    if current_user.role in ["paramedic", "doctor"]:
        audit_service.log_action(
            db,
            action="EMERGENCY_PROFILE_ACCESSED",
            actor_id=current_user.id,
            actor_email=current_user.email,
            details=f"Accessed emergency profile for patient {patient_user.full_name} ({patient_user.id})",
            ip_address=request.client.host if (request and request.client) else None,
        )

    return EmergencyProfileOut(
        user_id=patient_user.id,
        full_name=patient_user.full_name,
        email=patient_user.email,
        blood_group=profile.blood_group or "Unknown",
        dob=profile.dob,
        phone=profile.phone,
        emergency_contacts=parse_json_safely(profile.emergency_contacts, []),
        allergies=parse_json_safely(profile.allergies, []),
        chronic_conditions=parse_json_safely(profile.chronic_conditions, []),
        notes=profile.notes,
        updated_at=profile.updated_at,
    )

@router.put("/profile", response_model=EmergencyProfileOut)
def update_emergency_profile(
    profile_in: EmergencyProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()
    if not profile:
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)

    if profile_in.blood_group is not None:
        profile.blood_group = profile_in.blood_group
    if profile_in.dob is not None:
        profile.dob = profile_in.dob
    if profile_in.phone is not None:
        profile.phone = profile_in.phone
    if profile_in.emergency_contacts is not None:
        profile.emergency_contacts = json.dumps(profile_in.emergency_contacts)
    if profile_in.allergies is not None:
        profile.allergies = json.dumps(profile_in.allergies)
    if profile_in.chronic_conditions is not None:
        profile.chronic_conditions = json.dumps(profile_in.chronic_conditions)
    if profile_in.notes is not None:
        profile.notes = profile_in.notes

    db.commit()
    db.refresh(profile)

    audit_service.log_action(
        db,
        action="EMERGENCY_PROFILE_UPDATED",
        actor_id=current_user.id,
        actor_email=current_user.email,
        details="Updated emergency profile parameters",
        ip_address=request.client.host if request.client else None,
    )

    return EmergencyProfileOut(
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        blood_group=profile.blood_group or "Unknown",
        dob=profile.dob,
        phone=profile.phone,
        emergency_contacts=parse_json_safely(profile.emergency_contacts, []),
        allergies=parse_json_safely(profile.allergies, []),
        chronic_conditions=parse_json_safely(profile.chronic_conditions, []),
        notes=profile.notes,
        updated_at=profile.updated_at,
    )

@router.post("/sos", response_model=EmergencyEventOut, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    sos_in: SOSCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = EmergencyEvent(
        patient_id=current_user.id,
        status="active",
        latitude=sos_in.latitude or 28.6139,
        longitude=sos_in.longitude or 77.2090,
        location_name=sos_in.location_name or "Emergency Beacon Active",
        notes=sos_in.notes or "Immediate distress signal triggered by patient.",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    audit_service.log_action(
        db,
        action="SOS_TRIGGERED",
        actor_id=current_user.id,
        actor_email=current_user.email,
        details=f"SOS triggered at coordinates ({event.latitude}, {event.longitude})",
        ip_address=request.client.host if request.client else None,
    )

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == current_user.id).first()

    return EmergencyEventOut(
        id=event.id,
        patient_id=current_user.id,
        patient_name=current_user.full_name,
        patient_blood_group=profile.blood_group if profile else "Unknown",
        patient_phone=profile.phone if profile else None,
        status=event.status,
        latitude=event.latitude,
        longitude=event.longitude,
        location_name=event.location_name,
        notes=event.notes,
        triggered_at=event.triggered_at,
        resolved_at=event.resolved_at,
    )

@router.get("/events", response_model=List[EmergencyEventOut])
def get_emergency_events(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(EmergencyEvent).join(User, EmergencyEvent.patient_id == User.id)

    if current_user.role == "patient":
        query = query.filter(EmergencyEvent.patient_id == current_user.id)

    if status_filter:
        query = query.filter(EmergencyEvent.status == status_filter)

    events = query.order_by(EmergencyEvent.triggered_at.desc()).all()

    result = []
    for ev in events:
        profile = db.query(PatientProfile).filter(PatientProfile.user_id == ev.patient_id).first()
        patient_user = db.query(User).filter(User.id == ev.patient_id).first()
        result.append(
            EmergencyEventOut(
                id=ev.id,
                patient_id=ev.patient_id,
                patient_name=patient_user.full_name if patient_user else "Unknown Patient",
                patient_blood_group=profile.blood_group if profile else "Unknown",
                patient_phone=profile.phone if profile else None,
                status=ev.status,
                latitude=ev.latitude,
                longitude=ev.longitude,
                location_name=ev.location_name,
                notes=ev.notes,
                triggered_at=ev.triggered_at,
                resolved_at=ev.resolved_at,
            )
        )
    return result

@router.post("/events/{event_id}/resolve", response_model=EmergencyEventOut)
def resolve_emergency_event(
    event_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency event not found")

    if current_user.role not in ["doctor", "paramedic", "admin"] and event.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot resolve this SOS signal")

    event.status = "resolved"
    event.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)

    audit_service.log_action(
        db,
        action="SOS_RESOLVED",
        actor_id=current_user.id,
        actor_email=current_user.email,
        details=f"SOS event {event.id} resolved by {current_user.role}",
        ip_address=request.client.host if request.client else None,
    )

    profile = db.query(PatientProfile).filter(PatientProfile.user_id == event.patient_id).first()
    patient_user = db.query(User).filter(User.id == event.patient_id).first()

    return EmergencyEventOut(
        id=event.id,
        patient_id=event.patient_id,
        patient_name=patient_user.full_name if patient_user else "Unknown Patient",
        patient_blood_group=profile.blood_group if profile else "Unknown",
        patient_phone=profile.phone if profile else None,
        status=event.status,
        latitude=event.latitude,
        longitude=event.longitude,
        location_name=event.location_name,
        notes=event.notes,
        triggered_at=event.triggered_at,
        resolved_at=event.resolved_at,
    )
