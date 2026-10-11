from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import User, AuditLog
from backend.app.schemas.schemas import AuditLogOut
from backend.app.routers.deps import get_current_user, require_roles

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogOut])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_roles(["admin", "doctor"])),
    db: Session = Depends(get_db),
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [AuditLogOut.model_validate(l) for l in logs]
