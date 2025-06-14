from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import api_router
from .models import base, books, users, loans  # Importer les modèles pour Alembic

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5000", "http://127.0.0.1:5000", "http://127.0.0.1:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Inclusion des routes API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Management System API"}


from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models import User
from passlib.hash import bcrypt

def create_admin_if_not_exists():
    db: Session = SessionLocal()
    admin_email = "admin@biblio.fr"

    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin = User(
            full_name="Admin Root",
            email=admin_email,
            hashed_password=bcrypt.hash("admin123"),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin créé : admin@biblio.fr / admin123")
    else:
        print("ℹ️ Admin déjà présent")

create_admin_if_not_exists()
