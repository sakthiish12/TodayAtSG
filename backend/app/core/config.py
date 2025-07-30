from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "TodayAtSG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://todayatsg.com", 
        "https://www.todayatsg.com",
        "https://todayatsg.vercel.app",
        "http://localhost:3000", 
        "http://localhost:5173"
    ]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    EVENTBRITE_API_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@todayatsg.com"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File uploads
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Geolocation
    DEFAULT_SEARCH_RADIUS_KM: float = 10.0
    MAX_SEARCH_RADIUS_KM: float = 100.0
    SINGAPORE_CENTER_LAT: float = 1.3521
    SINGAPORE_CENTER_LNG: float = 103.8198
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_REQUESTS_PER_MINUTE: int = 5
    
    # Event submission
    EVENT_SUBMISSION_PRICE_SGD: float = 10.0
    FREE_EVENTS_PER_ORGANIZER_PER_MONTH: int = 1
    
    # Web scraping
    SCRAPING_USER_AGENT: str = "TodayAtSG Bot 1.0 (+https://todayatsg.com/robots)"
    SCRAPING_DELAY: float = 1.0
    SCRAPING_CONCURRENT_REQUESTS: int = 10
    SCRAPING_TIMEOUT: int = 30
    SCRAPING_MAX_RETRIES: int = 3
    SCRAPING_RETRY_DELAY: float = 2.0
    SCRAPING_BATCH_SIZE: int = 50
    SCRAPING_ENABLE_JS: bool = False
    SCRAPING_RESPECT_ROBOTS_TXT: bool = True
    SCRAPING_MAX_EVENTS_PER_SOURCE: int = 500
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Admin settings
    ADMIN_EMAIL: str = "admin@todayatsg.com"
    SUPER_ADMIN_EMAIL: Optional[str] = None
    
    # Vercel-specific settings
    VERCEL_ENV: Optional[str] = None
    VERCEL_URL: Optional[str] = None
    VERCEL_REGION: Optional[str] = None
    VERCEL_GIT_COMMIT_REF: Optional[str] = None
    
    @property
    def upload_path(self) -> Path:
        """Get the upload directory path."""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string or list with Vercel URL support."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        else:
            origins = self.ALLOWED_ORIGINS.copy()
        
        # Add Vercel URL if available
        if self.VERCEL_URL:
            vercel_url = f"https://{self.VERCEL_URL}"
            if vercel_url not in origins:
                origins.append(vercel_url)
        
        # Add branch-specific preview URL if not main branch
        if self.VERCEL_GIT_COMMIT_REF and self.VERCEL_GIT_COMMIT_REF != "main":
            branch_url = f"https://todayatsg-git-{self.VERCEL_GIT_COMMIT_REF}-your-team.vercel.app"
            if branch_url not in origins:
                origins.append(branch_url)
        
        return origins
    
    def get_cors_methods(self) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(self.ALLOWED_METHODS, str):
            return [method.strip() for method in self.ALLOWED_METHODS.split(",")]
        return self.ALLOWED_METHODS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Update CORS settings with parsed values
settings.ALLOWED_ORIGINS = settings.get_cors_origins()
settings.ALLOWED_METHODS = settings.get_cors_methods()