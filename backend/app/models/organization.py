import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import OrganizationType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.profiles import ClinicianProfile, ResponderProfile


_ORG_TYPES = ", ".join(f"'{t.value}'" for t in OrganizationType)


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    __table_args__ = (
        CheckConstraint(
            f"type IN ({_ORG_TYPES})",
            name="ck_organizations_type_allowed",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)

    clinicians: Mapped[list["ClinicianProfile"]] = relationship(
        back_populates="organization"
    )
    responders: Mapped[list["ResponderProfile"]] = relationship(
        back_populates="organization"
    )
