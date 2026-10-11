import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.models.models import User, Patient, EmergencyProfile
from backend.app.schemas.schemas import UserRegister, UserLogin, Token, UserOut
from backend.app.routers.deps import get_current_user
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, request: Request, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Validate role
    role = user_in.role.lower()
    if role not in ["patient", "doctor", "paramedic", "admin"]:
        role = "patient"

    # Create user in PostgreSQL
    user = User(
        email=user_in.email.lower(),
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # If role is patient, initialize blank patient and emergency profile
    if role == "patient":
        patient_record = Patient(
            user_id=user.id,
            blood_group="Unknown",
            emergency_contacts="[]",
            allergies="[]",
            chronic_conditions="[]",
            notes=None,
        )
        db.add(patient_record)

        emerg_profile = EmergencyProfile(
            patient_id=user.id,
            blood_group="Unknown",
            allergies="[]",
            chronic_conditions="[]",
            notes=None,
        )
        db.add(emerg_profile)
        db.commit()

    # Audit log
    audit_service.log_action(
        db,
        action="USER_REGISTER",
        actor_id=user.id,
        actor_email=user.email,
        details=f"User registered with role: {user.role}",
        ip_address=request.client.host if request.client else None,
    )

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Audit log
    audit_service.log_action(
        db,
        action="USER_LOGIN",
        actor_id=user.id,
        actor_email=user.email,
        details=f"Successful login for {user.role}",
        ip_address=request.client.host if request.client else None,
    )

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
