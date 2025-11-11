from pydantic_settings import BaseSettings 
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Azure Document Intelligence
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: str = "rbi-circulars"
    
    # Database (Neon Postgres Cloud)
    DATABASE_URL: str  # Required - use Neon connection string
    POSTGRES_USER: str = "anaya"
    POSTGRES_PASSWORD: str = "anaya_secure_password_2025"
    POSTGRES_DB: str = "anaya_watchtower"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # Neon Data API (for serverless HTTP queries)
    NEON_DATA_API_URL: Optional[str] = None
    NEON_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Qdrant Vector DB settings (replaced Chroma with Qdrant)
    # For local Docker:
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    # For Qdrant Cloud (SaaS):
    QDRANT_URL: Optional[str] = None  # https://xyz.qdrant.io
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PERSIST_DIR: str = "/qdrant/storage"
    
    # Slack Notifications
    SLACK_WEBHOOK_URL: Optional[str] = None
    
    # RBI Monitoring Configuration
    RBI_RSS_FEED_URL: str = "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx"
    RBI_CIRCULARS_PAGE_URL: str = "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx"
    RBI_EMAIL_IMAP_SERVER: Optional[str] = "imap.gmail.com"
    RBI_EMAIL_ADDRESS: Optional[str] = None
    RBI_EMAIL_PASSWORD: Optional[str] = None
    RBI_CHECK_INTERVAL_MINUTES: int = 30
    
    # Application Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # LangGraph Configuration
    LANGGRAPH_CHECKPOINT_ENABLED: bool = True
    
    # Optional: Gemini Fallback
    GOOGLE_API_KEY: Optional[str] = None
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def qdrant_connection_url(self) -> str:
        """Construct Qdrant connection URL (use Cloud URL if available, else local)"""
        if self.QDRANT_URL:
            return self.QDRANT_URL
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()