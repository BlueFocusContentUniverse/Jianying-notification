"""Celery task that reports worker health to the CapCut API."""

import logging
from typing import Any, Dict, Optional

from app.api.video_api_client import report_worker_status
from app.celery_app import celery_app
from app.config import config

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="jianying_notification.update_worker_status",
    queue=config.CELERY_QUEUE_NAME,
)
def update_worker_status(
    self,
    worker_name: str,
    hostname: Optional[str] = None,
    is_available: bool = True,
    task_id: Optional[str] = None,
    error_message: Optional[str] = None,
    traceback: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Report that a worker has started, failed, or recovered."""

    logger.info(
        "Received worker status update: %s available=%s", worker_name, is_available
    )
    success = report_worker_status(
        worker_name=worker_name,
        hostname=hostname,
        is_available=is_available,
        task_id=task_id,
        error_message=error_message,
        traceback=traceback,
        extra=extra,
    )
    if not success:
        logger.warning("Worker status report failed for %s; will retry next worker event", worker_name)
    return {"success": success}