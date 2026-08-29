"""
Phase 1.1 model tests.

Covers requirements 1-11 of the Phase 1.1 spec:
users can exist without a profile; can have each of the three profile
kinds but not two of the same kind; can have multiple roles; roles are
restricted to the supported values; organizations can have many
clinicians and many responders; FK behavior is correct.
"""
import uuid
from typing import Optional

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import (
    ClinicianProfile,
    Organization,
    OrganizationType,
    PatientProfile,
    ResponderProfile,
    Role,
    RoleName,
    User,
)
from app.models.role import UserRole


def _user(email: Optional[str] = None) -> User:
    return User(
        email=email or f"{uuid.uuid4()}@example.com",
        password_hash="not-a-real-hash",
    )


def _role(name: RoleName) -> Role:
    return Role(name=name.value)


# --- 1. A User can exist without a profile ---------------------------------
def test_user_can_exist_without_a_profile(db):
    u = _user()
    db.add(u)
    db.flush()
    assert u.id is not None
    assert u.patient_profile is None
    assert u.clinician_profile is None
    assert u.responder_profile is None


# --- 2. A User can have a PatientProfile -----------------------------------
def test_user_can_have_a_patient_profile(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(PatientProfile(user_id=u.id))
    db.flush()
    db.refresh(u)
    assert u.patient_profile is not None


# --- 3. A User cannot have two PatientProfiles -----------------------------
def test_user_cannot_have_two_patient_profiles(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(PatientProfile(user_id=u.id))
    db.flush()
    db.add(PatientProfile(user_id=u.id))
    with pytest.raises(IntegrityError):
        db.flush()


# --- 4. A User can have a ClinicianProfile ---------------------------------
def test_user_can_have_a_clinician_profile(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(ClinicianProfile(user_id=u.id))
    db.flush()
    db.refresh(u)
    assert u.clinician_profile is not None


def test_user_cannot_have_two_clinician_profiles(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(ClinicianProfile(user_id=u.id))
    db.flush()
    db.add(ClinicianProfile(user_id=u.id))
    with pytest.raises(IntegrityError):
        db.flush()


# --- 5. A User can have a ResponderProfile ---------------------------------
def test_user_can_have_a_responder_profile(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(ResponderProfile(user_id=u.id))
    db.flush()
    db.refresh(u)
    assert u.responder_profile is not None


def test_user_cannot_have_two_responder_profiles(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(ResponderProfile(user_id=u.id))
    db.flush()
    db.add(ResponderProfile(user_id=u.id))
    with pytest.raises(IntegrityError):
        db.flush()


# --- 6. A User can have multiple roles -------------------------------------
def test_user_can_have_multiple_roles(db):
    u = _user()
    patient_role = _role(RoleName.PATIENT)
    admin_role = _role(RoleName.ADMIN)
    db.add_all([u, patient_role, admin_role])
    db.flush()
    u.roles.extend([patient_role, admin_role])
    db.flush()
    db.refresh(u)
    assert {r.name for r in u.roles} == {"PATIENT", "ADMIN"}


# --- 7. Roles are restricted to supported prototype roles ------------------
def test_role_name_check_constraint_rejects_arbitrary_values(db):
    db.add(Role(name="SUPERUSER"))
    with pytest.raises(IntegrityError):
        db.flush()


def test_all_four_supported_role_names_are_accepted(db):
    for name in ("PATIENT", "CLINICIAN", "RESPONDER", "ADMIN"):
        db.add(Role(name=name))
    db.flush()
    stored = {r.name for r in db.query(Role).all()}
    assert stored == {"PATIENT", "CLINICIAN", "RESPONDER", "ADMIN"}


# --- 8. A ClinicianProfile can belong to an Organization -------------------
def test_clinician_profile_can_belong_to_an_organization(db):
    org = Organization(name="General Hospital", type=OrganizationType.HOSPITAL.value)
    u = _user()
    db.add_all([org, u])
    db.flush()
    profile = ClinicianProfile(user_id=u.id, organization_id=org.id)
    db.add(profile)
    db.flush()
    db.refresh(profile)
    assert profile.organization.id == org.id


# --- 9. Multiple clinicians can belong to one Organization -----------------
def test_multiple_clinicians_can_belong_to_one_organization(db):
    org = Organization(name="City Clinic", type=OrganizationType.CLINIC.value)
    u1, u2 = _user(), _user()
    db.add_all([org, u1, u2])
    db.flush()
    db.add_all([
        ClinicianProfile(user_id=u1.id, organization_id=org.id),
        ClinicianProfile(user_id=u2.id, organization_id=org.id),
    ])
    db.flush()
    db.refresh(org)
    assert len(org.clinicians) == 2


# --- 10. Multiple responders can belong to one Organization ----------------
def test_multiple_responders_can_belong_to_one_organization(db):
    org = Organization(name="Metro EMS", type=OrganizationType.EMS.value)
    u1, u2 = _user(), _user()
    db.add_all([org, u1, u2])
    db.flush()
    db.add_all([
        ResponderProfile(user_id=u1.id, organization_id=org.id),
        ResponderProfile(user_id=u2.id, organization_id=org.id),
    ])
    db.flush()
    db.refresh(org)
    assert len(org.responders) == 2


# --- 11. Foreign-key relationships behave correctly ------------------------
def test_profile_with_nonexistent_user_is_rejected(db):
    db.add(PatientProfile(user_id=uuid.uuid4()))
    with pytest.raises(IntegrityError):
        db.flush()


def test_deleting_a_user_cascades_to_their_profiles(db):
    u = _user()
    db.add(u)
    db.flush()
    db.add(PatientProfile(user_id=u.id))
    db.flush()
    patient_id_before = u.patient_profile.id
    db.delete(u)
    db.flush()
    assert db.get(PatientProfile, patient_id_before) is None


def test_deleting_an_organization_nulls_clinician_link(db):
    org = Organization(name="Temp Hospital", type=OrganizationType.HOSPITAL.value)
    u = _user()
    db.add_all([org, u])
    db.flush()
    profile = ClinicianProfile(user_id=u.id, organization_id=org.id)
    db.add(profile)
    db.flush()
    db.delete(org)
    db.flush()
    db.refresh(profile)
    assert profile.organization_id is None
    assert db.get(ClinicianProfile, profile.id) is not None


def test_user_role_link_is_removed_when_user_is_deleted(db):
    u = _user()
    role = _role(RoleName.CLINICIAN)
    db.add_all([u, role])
    db.flush()
    u.roles.append(role)
    db.flush()
    db.delete(u)
    db.flush()
    remaining = db.execute(select(UserRole)).all()
    assert remaining == []


# --- Bonus: organization.type is also restricted ---------------------------
def test_organization_type_check_constraint_rejects_arbitrary_values(db):
    db.add(Organization(name="Weird", type="ZOO"))
    with pytest.raises(IntegrityError):
        db.flush()


# --- Bonus: email uniqueness -----------------------------------------------
def test_user_email_is_unique(db):
    email = f"{uuid.uuid4()}@example.com"
    db.add(_user(email=email))
    db.flush()
    db.add(_user(email=email))
    with pytest.raises(IntegrityError):
        db.flush()
