from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import schemas
from typing import List

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


@router.get("/starters/all", response_model=List[schemas.StarterResponse])
def get_all_starters(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all users who have created at least one project (visible to public)."""
    # Find users with public projects (verified, financing, ended_success, ended_failed)
    starters = db.query(
        models.User.id,
        models.User.profile_slug,
        models.User.full_name,
        models.User.avatar_url,
        models.User.created_at,
        func.count(models.Project.id).label("project_count"),
        func.coalesce(func.sum(models.Project.funding_current), 0).label("total_funding_raised")
    ).join(
        models.Project, models.User.id == models.Project.owner_id
    ).filter(
        models.Project.status.in_(["verified", "financing", "ended_success", "ended_failed"])
    ).group_by(
        models.User.id
    ).order_by(
        func.sum(models.Project.funding_current).desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": starter.id,
            "profile_slug": starter.profile_slug,
            "full_name": starter.full_name,
            "avatar_url": starter.avatar_url,
            "created_at": starter.created_at,
            "project_count": starter.project_count,
            "total_funding_raised": float(starter.total_funding_raised or 0)
        }
        for starter in starters
    ]


@router.get("/starters/successful", response_model=List[schemas.SuccessfulStarterResponse])
def get_successful_starters(
    limit: int = 4,
    db: Session = Depends(get_db)
):
    """Get users who have successfully funded projects."""
    # Find users with ended_success projects
    successful_starters = db.query(
        models.User.id,
        models.User.profile_slug,
        models.User.full_name,
        models.User.avatar_url,
        models.User.created_at,
        func.count(models.Project.id).label("successful_projects_count"),
        func.coalesce(func.sum(models.Project.funding_current), 0).label("total_funding_raised")
    ).join(
        models.Project, models.User.id == models.Project.owner_id
    ).filter(
        models.Project.status == "ended_success"
    ).group_by(
        models.User.id
    ).order_by(
        func.sum(models.Project.funding_current).desc()
    ).limit(limit).all()

    return [
        {
            "id": starter.id,
            "profile_slug": starter.profile_slug,
            "full_name": starter.full_name,
            "avatar_url": starter.avatar_url,
            "created_at": starter.created_at,
            "successful_projects_count": starter.successful_projects_count,
            "total_funding_raised": float(starter.total_funding_raised or 0)
        }
        for starter in successful_starters
    ]


@router.get("/{profile_slug}", response_model=schemas.PublicProfileResponse)
def get_public_profile(
    profile_slug: str,
    db: Session = Depends(get_db)
):
    """Get a public profile by profile slug."""
    user = db.query(models.User).filter(models.User.profile_slug == profile_slug).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Only get public projects (verified, financing, ended_success, ended_failed)
    public_projects = db.query(models.Project).filter(
        models.Project.owner_id == user.id,
        models.Project.status.in_(["verified", "financing", "ended_success", "ended_failed"])
    ).order_by(models.Project.created_at.desc()).all()

    return {
        "id": user.id,
        "profile_slug": user.profile_slug,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "is_starter": user.is_starter,
        "created_at": user.created_at,
        "projects": public_projects
    }
