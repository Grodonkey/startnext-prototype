from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from security import get_current_user
from two_factor import generate_2fa_secret, verify_2fa_code, generate_qr_code

router = APIRouter(prefix="/api/2fa", tags=["Two-Factor Authentication"])


@router.post("/setup", response_model=schemas.TwoFactorSetupResponse)
def setup_2fa(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="Two-factor authentication is already enabled"
        )

    secret = generate_2fa_secret()
    qr_code_url = generate_qr_code(secret, current_user.email)

    current_user.two_factor_secret = secret
    db.commit()

    return {
        "secret": secret,
        "qr_code_url": qr_code_url
    }


@router.post("/verify", response_model=schemas.MessageResponse)
def verify_2fa(
    verify_data: schemas.TwoFactorVerifyRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=400,
            detail="Two-factor authentication not set up"
        )

    if not verify_2fa_code(current_user.two_factor_secret, verify_data.code):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )

    current_user.two_factor_enabled = True
    db.commit()

    return {"message": "Two-factor authentication enabled successfully"}


@router.post("/disable", response_model=schemas.MessageResponse)
def disable_2fa(
    verify_data: schemas.TwoFactorVerifyRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="Two-factor authentication is not enabled"
        )

    if not verify_2fa_code(current_user.two_factor_secret, verify_data.code):
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )

    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.commit()

    return {"message": "Two-factor authentication disabled successfully"}
