"""Configuration management for the documentation enricher."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-5-nano"  # Fixo: GPT-5 nano
    
    # API Testing Settings
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "90"))  # Increased for AI analysis
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "120"))  # Per AI request
    
    # Production Operations Control
    ENABLE_PRODUCTION_OPERATIONS = os.getenv("ENABLE_PRODUCTION_OPERATIONS", "false").lower() == "true"
    
    # API Credentials (fallback - prefer input/credentials.json)
    API_AUTH_TYPE = os.getenv("API_AUTH_TYPE", "")
    API_TOKEN = os.getenv("API_TOKEN", "")
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")
    API_KEY = os.getenv("API_KEY", "")
    API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in .env file or environment variables."
            )

