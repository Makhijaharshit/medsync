from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import User, MedicalEntity, MedicalDocument, TimelineEvent
from backend.app.schemas.schemas import TimelineItemOut
from backend.app.routers.deps import get_current_user
from backend.app.services.audit_service import audit_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeline", tags=["Medical Timeline"])

@router.get("", response_model=List[TimelineItemOut])
def get_timeline(
    patient_id: Optional[str] = None,
    category: Optional[str] = Query(None, description="diagnosis, medication, allergy, procedure, doctor_note"),
    only_verified: bool = Query(True, description="Show only verified records"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_patient_id = current_user.id
    if current_user.role in ["doctor", "admin", "paramedic"] and patient_id:
        target_patient_id = patient_id
    elif current_user.role == "patient" and patient_id and patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access other patient timelines")

    query = db.query(MedicalEntity, MedicalDocument.title.label("doc_title")).outerjoin(
        MedicalDocument, MedicalEntity.document_id == MedicalDocument.id
    ).filter(MedicalEntity.patient_id == target_patient_id)

    if only_verified:
        query = query.filter(MedicalEntity.verified == True)

    if category:
        query = query.filter(MedicalEntity.type == category.lower())

    results = query.order_by(MedicalEntity.created_at.desc()).all()

    timeline_items = []
    for entity, doc_title in results:
        timeline_items.append(
            TimelineItemOut(
                id=entity.id,
                type=entity.type,
                value=entity.value,
                details=entity.details,
                confidence=entity.confidence,
                verified=entity.verified,
                date_recorded=entity.date_recorded or (entity.created_at.strftime("%Y-%m-%d") if entity.created_at else None),
                created_at=entity.created_at,
                source_document_id=entity.document_id,
                source_document_title=doc_title or "Clinical Entry",
            )
        )

    return timeline_items

@router.delete("/{record_id}")
def delete_medical_record(
    record_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entity = db.query(MedicalEntity).filter(MedicalEntity.id == record_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    if current_user.role == "patient" and entity.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "paramedic":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Paramedic roles cannot delete records")

    val = entity.value
    ent_type = entity.type

    # Delete any timeline events associated with this entity value / type
    db.query(TimelineEvent).filter(
        TimelineEvent.patient_id == entity.patient_id,
        TimelineEvent.title == entity.value,
        TimelineEvent.event_type == entity.type,
    ).delete()

    # Audit log
    audit_service.log_action(
        db,
        action="RECORD_DELETED",
        actor_id=current_user.id,
        actor_email=current_user.email,
        details=f"Deleted {ent_type} record: '{val}'",
        ip_address=request.client.host if request.client else None,
    )

    db.delete(entity)
    db.commit()

    return {"success": True, "message": f"Medical record '{val}' deleted successfully"}

