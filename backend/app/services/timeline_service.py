import logging
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.models import TimelineEvent, MedicalEntity

logger = logging.getLogger(__name__)

class TimelineService:
    @staticmethod
    def generate_timeline_events(
        db: Session,
        patient_id: str,
        document_id: str,
        verified_entities: List[MedicalEntity]
    ) -> List[TimelineEvent]:
        """
        Creates timeline_events in PostgreSQL from verified entities.
        Only called after human verification.
        Ignores unverified or deleted entities.
        Marks events as verified = True.
        """
        events: List[TimelineEvent] = []
        now_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for entity in verified_entities:
            if not entity.verified:
                continue

            event_date = entity.date_recorded or now_date_str

            desc_parts = []
            if entity.details:
                desc_parts.append(entity.details)
            if entity.source_page:
                desc_parts.append(f"Source Page: {entity.source_page}")
            desc = " • ".join(desc_parts) if desc_parts else None

            timeline_event = TimelineEvent(
                patient_id=patient_id,
                event_type=entity.type,
                title=entity.value,
                description=desc,
                event_date=event_date,
                source_id=document_id,
                verified=True,
            )
            db.add(timeline_event)
            events.append(timeline_event)

        db.commit()
        for ev in events:
            db.refresh(ev)

        logger.info(f"Generated {len(events)} verified timeline events for patient {patient_id}")
        return events

timeline_service = TimelineService()
