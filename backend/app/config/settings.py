"""
Application Settings

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # App config
    APP_NAME: str = "3R Analyzer Intelligence"
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    )

    # Database Configuration
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # ML Configuration
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
    EMBEDDING_BATCH_SIZE: int = Field(default=512)
    
    # HDBSCAN Configuration
    MIN_CLUSTER_SIZE: int = Field(default=5)
    MIN_SAMPLES: int = Field(default=3)
    CLUSTER_SELECTION_METHOD: str = Field(default="eom")
    CLUSTER_METRIC: str = Field(default="euclidean")
    
    # 3R Classifier & Processing Thresholds
    SIMILARITY_THRESHOLD: float = Field(default=0.85)
    PROBLEM_CANDIDATE_THRESHOLD: int = Field(default=50)

    # Note: Priority weights remain a constant dict but could be configured if needed
    PRIORITY_WEIGHTS: dict = {
        "P1": 5,
        "P2": 4,
        "P3": 3,
        "P4": 2,
        "P5": 1
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Global settings instance
settings = Settings()
