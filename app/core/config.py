from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Stock Portfolio Tracker"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # production, development, testing
    
    # Authentication
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    CORS_ORIGINS: list[str] = ["*"]
    ENCRYPTION_KEY: str  # Pro šifrování citlivých dat v DB
    
    # External Services
    PRICE_PROVIDER: str = "alpha_vantage"  # nebo jiný provider
    PRICE_PROVIDER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()