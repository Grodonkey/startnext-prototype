from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    profile_slug = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 2FA fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Magic link login
    magic_link_token = Column(String(255), nullable=True)
    magic_link_expires = Column(DateTime(timezone=True), nullable=True)

    # Project starter role
    is_starter = Column(Boolean, default=False)

    # Avatar
    avatar_url = Column(String(500), nullable=True)

    # Relationship to projects
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    # Funding details
    funding_goal = Column(Numeric(12, 2), nullable=True)
    funding_current = Column(Numeric(12, 2), default=0)

    # Status: draft, submitted, verified, financing, ended_success, ended_failed
    status = Column(String(50), default="draft")

    # Project type: crowdfunding, fundraising, private
    project_type = Column(String(50), default="crowdfunding")

    # Plan and provision
    plan = Column(String(50), nullable=True)  # basic, pro, premium, enterprise
    provision = Column(Numeric(5, 2), nullable=True)  # percentage, e.g. 7.00 for 7%
    voucher_code = Column(String(50), nullable=True)

    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)  # Planned start date (user input)
    financing_start = Column(DateTime(timezone=True), nullable=True)  # Actual financing start
    financing_end = Column(DateTime(timezone=True), nullable=True)

    # Media
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    # AI generated flag
    ai_generated = Column(Boolean, default=False)
    ai_thread_id = Column(String(36), nullable=True)  # Reference to AI thread that created this

    # Relationship
    owner = relationship("User", back_populates="projects")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)


# AI Coach Models
class AIThread(Base):
    __tablename__ = "ai_threads"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    openai_thread_id = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional for anonymous
    session_id = Column(String(255), nullable=True, index=True)  # For anonymous users
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    messages = relationship("AIMessage", back_populates="thread", cascade="all, delete-orphan")
    draft = relationship("AIDraft", back_populates="thread", uselist=False)
    user = relationship("User")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    thread_id = Column(String(36), ForeignKey("ai_threads.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_assistant = Column(Boolean, default=False)  # True = AI, False = User
    is_system = Column(Boolean, default=False)  # True = hidden system prompt
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    thread = relationship("AIThread", back_populates="messages")


class AIDraft(Base):
    __tablename__ = "ai_drafts"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(36), ForeignKey("ai_threads.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)  # For anonymous users

    # Project fields (matching Project model)
    title = Column(String(255), nullable=True)
    slug = Column(String(255), nullable=True)
    short_description = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    funding_goal = Column(Numeric(12, 2), nullable=True)
    project_type = Column(String(50), default="crowdfunding")
    plan = Column(String(50), nullable=True)  # basic, pro, premium, enterprise
    start_date = Column(DateTime(timezone=True), nullable=True)
    duration_days = Column(Integer, nullable=True)

    # Status
    status = Column(String(50), default="draft")  # draft, converted
    converted_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    thread = relationship("AIThread", back_populates="draft")
    user = relationship("User")
    converted_project = relationship("Project")
