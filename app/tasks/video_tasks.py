"""
Celery tasks for video render status updates
"""

import logging
from typing import Any, Dict, Optional

from app.api import call_video_task_status_api, create_video_record
from app.celery_app import celery_app
from app.config import config

# Configure logging
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="jianying_notification.update_video_render_status", queue=config.CELERY_QUEUE_NAME)
def update_video_render_status(
    self,
    status: str,
    task_id: Optional[str] = None,
    progress: Optional[float] = None,
    error_message: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Process video render status update and call video task status API.

    Args:
        status: New status (pending, processing, completed, failed)
        task_id: Task identifier (if available)
        progress: Progress value (0.0 - 100.0)
        error_message: Error message if render failed (optional)
        extra: Additional metadata

    Returns:
        dict: Result with success status and message
    """
    try:
        logger.info(f"Processing video render status for task_id: {task_id}, status: {status}")

        # Log error message if provided
        if error_message:
            logger.error(f"Error message: {error_message}")

        # Map status to render_status enum
        # Valid render_status values: INITIALIZED, PENDING, PROCESSING, COMPLETED, FAILED
        render_status_map = {
            "initialized": "INITIALIZED",
            "pending": "PENDING",
            "processing": "PROCESSING",
            "completed": "COMPLETED",
            "failed": "FAILED"
        }
        render_status = render_status_map.get(status.lower(), status.upper())

        # Call video task status API if task_id is provided
        api_success = False
        if task_id:
            api_success = call_video_task_status_api(
                task_id=task_id,
                status=status,
                render_status=render_status,
                progress=progress,
                message=error_message,
                extra=extra
            )

        logger.info(f"Successfully processed video render status for task_id: {task_id} (API call: {api_success})")

        return {
            "success": True,
            "message": "Video render status processed successfully",
            "task_id": task_id,
            "status": status,
            "api_called": api_success
        }

    except Exception as e:
        logger.error(f"Error processing video render status: {e!s}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="jianying_notification.process_video_render_completion", queue=config.CELERY_QUEUE_NAME)
def process_video_render_completion(
    self,
    video_id: str,
    oss_url: str,
    task_id: Optional[str] = None,
    video_name: Optional[str] = None,
    resolution: Optional[str] = None,
    framerate: Optional[str] = None,
    duration: Optional[float] = None,
    file_size: Optional[int] = None,
    thumbnail_url: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Process video render completion with OSS link.

    This task is triggered when video rendering is completed and 
    an OSS link is available. It updates the task status and creates
    a video record via API.

    Args:
        video_id: Unique identifier for the video
        oss_url: OSS link to the rendered video
        task_id: Task identifier (if available)
        video_name: Name of the video
        resolution: Video resolution
        framerate: Video framerate
        duration: Video duration in seconds
        file_size: File size in bytes
        thumbnail_url: Thumbnail URL
        extra: Additional metadata

    Returns:
        dict: Result with success status and message
    """
    logger.info(f"Processing video render completion for video_id: {video_id}")

    try:
        # Update status to completed
        result = update_video_render_status(
            status="completed",
            task_id=task_id,
            progress=100.0
        )

        # Create video record with OSS link
        if task_id:
            create_video_record(
                task_id=task_id,
                oss_url=oss_url,
                video_name=video_name,
                resolution=resolution,
                framerate=framerate,
                duration=duration,
                file_size=file_size,
                thumbnail_url=thumbnail_url
            )

        logger.info(f"Video render completed successfully for video_id: {video_id}")

        return result

    except Exception as e:
        logger.error(f"Error processing video render completion: {e!s}", exc_info=True)
        # Log failure
        if task_id:
            call_video_task_status_api(
                task_id=task_id,
                status="failed",
                render_status="FAILED",
                message=str(e)
            )
        raise self.retry(exc=e, countdown=60, max_retries=3)
