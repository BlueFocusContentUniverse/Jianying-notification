"""
Celery application configuration and initialization
"""

import os
import sys

# Add project root to sys.path to allow running this script directly
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from celery import Celery

from app.config import config

# Create Celery application instance
celery_app = Celery(
    config.APP_NAME,
    include=["app.tasks.video_tasks", "app.tasks.worker_status"],
)

# Configure Celery
celery_config = {
    "broker_url": config.CELERY_BROKER_URL,
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 30 * 60,  # 30 minutes
    "task_soft_time_limit": 25 * 60,  # 25 minutes
    "task_default_queue": config.CELERY_QUEUE_NAME,
}

# Windows compatibility: Use solo pool by default on Windows
if sys.platform == "win32":
    celery_config["worker_pool"] = "solo"

celery_app.conf.update(celery_config)

if __name__ == "__main__":
    # If no arguments are provided, default to starting a worker
    args = sys.argv[1:]
    if not args:
        args = ["worker", "-l", "info", "-Q", config.CELERY_QUEUE_NAME]
    celery_app.start(args)
