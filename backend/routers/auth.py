from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_session_token,
    create_reset_token,
    get_current_user
)
from two_factor import verify_2fa_code
from email_service import send_password_reset_email, send_welcome_email
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_admin=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    send_welcome_email(db_user.email, db_user.full_name)

    return db_user


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    login_data: schemas.LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    if user.two_factor_enabled:
        if not login_data.two_factor_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Two-factor authentication code required"
            )

        if not verify_2fa_code(user.two_factor_secret, login_data.two_factor_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid two-factor authentication code"
            )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    session_token = create_session_token()
    session = models.Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(session)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(models.Session).filter(models.Session.user_id == current_user.id).delete()
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/password-reset-request", response_model=schemas.MessageResponse)
def password_reset_request(
    request_data: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == request_data.email).first()

    if user:
        reset_token = create_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        send_password_reset_email(user.email, reset_token, user.full_name)

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm", response_model=schemas.MessageResponse)
def password_reset_confirm(
    reset_data: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.reset_token == reset_data.token,
        models.User.reset_token_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None

    db.query(models.Session).filter(models.Session.user_id == user.id).delete()

    db.commit()

    return {"message": "Password has been reset successfully"}
