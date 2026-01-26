from datetime import datetime, timedelta
import re
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
    get_current_user,
    validate_session
)
from two_factor import verify_2fa_code
from email_service import send_password_reset_email, send_welcome_email, send_magic_link_email
from config import settings


def generate_profile_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    if not name:
        return ""
    # Convert to lowercase
    slug = name.lower()
    # Replace umlauts and special chars
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c'
    }
    for char, replacement in replacements.items():
        slug = slug.replace(char, replacement)
    # Replace spaces and non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def get_unique_profile_slug(db: Session, base_slug: str, exclude_user_id: int = None) -> str:
    """Get a unique profile slug by appending numbers if necessary."""
    slug = base_slug
    counter = 1
    while True:
        query = db.query(models.User).filter(models.User.profile_slug == slug)
        if exclude_user_id:
            query = query.filter(models.User.id != exclude_user_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate unique profile slug from full_name
    base_slug = generate_profile_slug(user.full_name)
    if not base_slug:
        raise HTTPException(status_code=400, detail="Full name is required")
    profile_slug = get_unique_profile_slug(db, base_slug)

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        profile_slug=profile_slug,
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
        expires_at=datetime.utcnow() + timedelta(hours=settings.SESSION_TOKEN_EXPIRE_HOURS),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(session)
    db.commit()

    return {
        "access_token": access_token,
        "session_token": session_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/refresh", response_model=schemas.RefreshTokenResponse)
def refresh_token(
    refresh_data: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh the access token using a valid session token"""
    user = validate_session(db, refresh_data.session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
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


# Magic Link endpoints
@router.post("/magic-link/request", response_model=schemas.MessageResponse)
def request_magic_link(
    request_data: schemas.MagicLinkRequest,
    db: Session = Depends(get_db)
):
    """Request a magic link for passwordless login"""
    user = db.query(models.User).filter(models.User.email == request_data.email).first()

    if user and user.is_active:
        magic_token = create_reset_token()  # Reuse token generation
        user.magic_link_token = magic_token
        user.magic_link_expires = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        send_magic_link_email(user.email, magic_token, user.full_name)

    # Always return success to prevent email enumeration
    return {"message": "Wenn die E-Mail existiert, wurde ein Login-Link gesendet"}


@router.post("/magic-link/verify", response_model=schemas.LoginResponse)
def verify_magic_link(
    verify_data: schemas.MagicLinkVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify magic link token and login user"""
    user = db.query(models.User).filter(
        models.User.magic_link_token == verify_data.token,
        models.User.magic_link_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Ungültiger oder abgelaufener Login-Link"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account ist deaktiviert")

    # Clear the magic link token
    user.magic_link_token = None
    user.magic_link_expires = None

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # Create session
    session_token = create_session_token()
    session = models.Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.SESSION_TOKEN_EXPIRE_HOURS),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(session)
    db.commit()

    return {
        "access_token": access_token,
        "session_token": session_token,
        "token_type": "bearer",
        "user": user
    }
