from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: int
    profile_slug: str
    is_active: bool
    is_admin: bool
    is_starter: bool = False
    two_factor_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    session_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# Magic Link schemas
class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerify(BaseModel):
    token: str


# 2FA schemas
class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code_url: str


class TwoFactorVerifyRequest(BaseModel):
    code: str


class TwoFactorToggleRequest(BaseModel):
    enabled: bool
    code: Optional[str] = None


# Admin schemas
class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class TestEmailRequest(BaseModel):
    email: EmailStr
    email_type: str = Field(..., description="Type: welcome, password_reset, account_activated, account_deactivated, test_simple")
    user_name: Optional[str] = None


# Token refresh schemas
class RefreshTokenRequest(BaseModel):
    session_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Generic response
class MessageResponse(BaseModel):
    message: str


# Project schemas
class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    funding_goal: Optional[float] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    project_type: str = Field(default="crowdfunding", description="Type: crowdfunding, fundraising, private")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    funding_goal: Optional[float] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    project_type: Optional[str] = Field(None, description="Type: crowdfunding, fundraising, private")


class ProjectOwner(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: EmailStr
    profile_slug: str

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    status: str
    funding_current: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    financing_start: Optional[datetime] = None
    financing_end: Optional[datetime] = None
    owner: Optional[ProjectOwner] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    status: str
    project_type: str = "crowdfunding"
    funding_goal: Optional[float] = None
    funding_current: float
    image_url: Optional[str] = None
    created_at: datetime
    owner: Optional[ProjectOwner] = None

    class Config:
        from_attributes = True


class SlugSuggestion(BaseModel):
    slug: str


# Admin Project schemas
class AdminProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    funding_goal: Optional[float] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    project_type: Optional[str] = Field(None, description="Type: crowdfunding, fundraising, private")
    status: Optional[str] = Field(None, description="Status: draft, submitted, verified, financing, ended_success, ended_failed, rejected")


class AdminProjectResponse(ProjectBase):
    id: int
    owner_id: int
    status: str
    funding_current: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    financing_start: Optional[datetime] = None
    financing_end: Optional[datetime] = None
    owner: Optional[ProjectOwner] = None

    class Config:
        from_attributes = True


# Public Profile schemas
class PublicProjectResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    status: str
    project_type: str = "crowdfunding"
    funding_goal: Optional[float] = None
    funding_current: float
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PublicProfileResponse(BaseModel):
    id: int
    profile_slug: str
    full_name: str
    is_starter: bool = False
    created_at: datetime
    projects: list[PublicProjectResponse] = []

    class Config:
        from_attributes = True


class SuccessfulStarterResponse(BaseModel):
    id: int
    profile_slug: str
    full_name: str
    created_at: datetime
    successful_projects_count: int = 0
    total_funding_raised: float = 0

    class Config:
        from_attributes = True


class StarterResponse(BaseModel):
    id: int
    profile_slug: str
    full_name: str
    created_at: datetime
    project_count: int = 0
    total_funding_raised: float = 0

    class Config:
        from_attributes = True
