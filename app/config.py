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

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    CELERY_QUEUE_NAME = os.getenv("CELERY_QUEUE_NAME", "notifications")

    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "Jianying-Notification")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Video API Configuration
    VIDEO_API_BASE_URL = os.getenv("VIDEO_API_BASE_URL", "http://localhost:5000")
    VIDEO_API_TOKEN = os.getenv("VIDEO_API_TOKEN", "")


config = Config()
