import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://crm_user:crm_secret_password@localhost:5432/crm_db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey123changeinproduction")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # First superuser
    FIRST_SUPERUSER: Optional[str] = os.getenv("FIRST_SUPERUSER", "admin")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")
    
    # App
    APP_NAME: str = "CRM System"
    APP_VERSION: str = "1.0.0"

settings = Settings()
