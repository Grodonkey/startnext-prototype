import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
import models
from routers import auth, users, admin, two_factor, projects, profiles, ai_coach
from security import get_password_hash
from config import settings

# Skip migrations in test mode - use create_all instead
if os.environ.get("TESTING") != "true":
    from migrations import run_migrations
    if not run_migrations(engine):
        # Fallback to create_all if migrations fail
        models.Base.metadata.create_all(bind=engine)
else:
    # In test mode, just create all tables
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Startnext Prototype Backend Service",
    description="API Services for user- and project-management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(two_factor.router)
app.include_router(projects.router)
app.include_router(profiles.router)
app.include_router(ai_coach.router)


@app.on_event("startup")
def create_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = models.User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Admin User",
                profile_slug="admin-user",
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: {settings.ADMIN_EMAIL}")
        else:
            # Ensure existing admin has a profile_slug
            if not admin.profile_slug:
                admin.profile_slug = "admin-user"
                db.commit()
            print("Admin user already exists")
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "Startnext Prototype Backend Service",
        "docs": "/docs",
        "version": "1.0.0",
        "author": "Elias Groesel"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
