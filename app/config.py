"""
Configuration module for the application.
Loads settings from environment variables.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL"
    )
    CELERY_QUEUE_NAME = os.getenv("CELERY_QUEUE_NAME", "notifications")

    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "Jianying-Notification")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Video API Configuration
    VIDEO_API_BASE_URL = os.getenv("VIDEO_API_BASE_URL", "http://localhost:9001")

    # Cognito M2M Configuration
    COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN", "")
    COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "")
    COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET", "")
    COGNITO_SCOPE = os.getenv("COGNITO_SCOPE", "")


config = Config()
