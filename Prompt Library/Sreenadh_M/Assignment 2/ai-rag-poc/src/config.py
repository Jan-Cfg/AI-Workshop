"""
Configuration Management for AI RAG Project
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


class Config:
    """Base configuration"""

    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # Database Settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "rag_database")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # RAG Settings
    RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

    # Security
    API_KEY = os.getenv("API_KEY", "default-api-key")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-encryption-key")

    # Application
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        required = [cls.DB_HOST, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD]
        if not all(required):
            raise ValueError("Missing required database configuration")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


def get_config(env: str = "development") -> Config:
    """Factory function to get appropriate config"""
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return configs.get(env, DevelopmentConfig)