from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.models import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        actor_id: Optional[str] = None,
        actor_email: str = "anonymous",
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        audit_entry = AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            details=details,
            ip_address=ip_address,
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

audit_service = AuditService()
