"""File upload endpoints for avatars and project images."""
import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from database import get_db
import models
from security import get_current_user

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])

# Configure upload directory
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "./uploads"))
AVATARS_DIR = UPLOAD_DIR / "avatars"
PROJECT_IMAGES_DIR = UPLOAD_DIR / "projects"

# Allowed image types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_upload_dirs():
    """Create upload directories if they don't exist."""
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)
    PROJECT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower() if filename else ".jpg"


def validate_image(file: UploadFile) -> None:
    """Validate uploaded image file."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )


async def save_upload(file: UploadFile, directory: Path, prefix: str) -> str:
    """Save uploaded file and return the relative path."""
    ensure_upload_dirs()
    validate_image(file)

    # Generate unique filename
    ext = get_file_extension(file.filename)
    filename = f"{prefix}_{uuid.uuid4().hex}{ext}"
    file_path = directory / filename

    # Check file size by reading content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Return relative path from uploads directory
    return f"/uploads/{directory.name}/{filename}"


def delete_old_file(url: str) -> None:
    """Delete old file if it exists."""
    if not url or not url.startswith("/uploads/"):
        return

    try:
        file_path = UPLOAD_DIR.parent / url.lstrip("/")
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # Ignore errors when deleting old files


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or update user avatar."""
    # Delete old avatar if exists
    if current_user.avatar_url:
        delete_old_file(current_user.avatar_url)

    # Save new avatar
    avatar_url = await save_upload(file, AVATARS_DIR, f"avatar_{current_user.id}")

    # Update user
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}


@router.delete("/avatar")
async def delete_avatar(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user avatar."""
    if current_user.avatar_url:
        delete_old_file(current_user.avatar_url)
        current_user.avatar_url = None
        db.commit()

    return {"message": "Avatar deleted"}


@router.post("/project/{project_id}/image")
async def upload_project_image(
    project_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or update project header image."""
    # Get project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check ownership (unless admin)
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )

    # Delete old image if exists
    if project.image_url:
        delete_old_file(project.image_url)

    # Save new image
    image_url = await save_upload(file, PROJECT_IMAGES_DIR, f"project_{project_id}")

    # Update project
    project.image_url = image_url
    db.commit()
    db.refresh(project)

    return {"image_url": image_url}


@router.delete("/project/{project_id}/image")
async def delete_project_image(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project header image."""
    # Get project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check ownership (unless admin)
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )

    if project.image_url:
        delete_old_file(project.image_url)
        project.image_url = None
        db.commit()

    return {"message": "Project image deleted"}
