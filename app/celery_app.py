"""
Celery application configuration and initialization
"""

from celery import Celery
from app.config import config

# Create Celery application instance
celery_app = Celery(
    config.APP_NAME,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=['app.tasks.video_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

if __name__ == '__main__':
    celery_app.start()
