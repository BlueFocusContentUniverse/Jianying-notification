"""
Video API client for calling video management endpoints.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = os.getenv("VIDEO_API_BASE_URL", "http://localhost:5000")
API_TOKEN = os.getenv("VIDEO_API_TOKEN", "")


def call_video_task_status_api(
    task_id: str,
    status: Optional[str] = None,
    render_status: Optional[str] = None,
    progress: Optional[float] = None,
    message: Optional[str] = None,
    video_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Call the video task status API to update task status.

    Args:
        task_id: Task identifier
        render_status: Render status enum value (e.g., "PROCESSING", "COMPLETED", "FAILED")
        progress: Progress value (0.0 - 100.0)
        message: Status message
        video_id: Video ID to link to the task
        extra: Additional metadata

    Returns:
        bool: True if API call succeeded, False otherwise
    """
    if not API_TOKEN:
        logger.warning("VIDEO_API_TOKEN not configured, skipping API call")
        return False

    try:
        url = f"{API_BASE_URL}/api/video-tasks/{task_id}/status"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {}
        if status is not None:
            payload["status"] = status
        if render_status is not None:
            payload["render_status"] = render_status
        if progress is not None:
            payload["progress"] = progress
        if message is not None:
            payload["message"] = message
        if video_id is not None:
            payload["video_id"] = video_id
        if extra is not None:
            payload["extra"] = extra

        logger.info(f"Calling video task status API: {url} with payload: {payload}")

        response = requests.put(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get("success"):
            logger.info(f"Successfully updated task status via API for task_id: {task_id}")
            return True
        else:
            logger.error(f"API returned success=False: {result.get('error')}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to call video task status API: {e!s}", exc_info=True)
        return False


def create_video_record(
    task_id: str,
    oss_url: str,
    video_name: Optional[str] = None,
    resolution: Optional[str] = None,
    framerate: Optional[str] = None,
    duration: Optional[float] = None,
    file_size: Optional[int] = None,
    thumbnail_url: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Call the video creation API to create a new video record.

    Args:
        task_id: Task identifier
        oss_url: OSS URL of the video
        video_name: Name of the video
        resolution: Video resolution
        framerate: Video framerate
        duration: Video duration in seconds
        file_size: File size in bytes
        thumbnail_url: Thumbnail URL
        extra: Additional metadata

    Returns:
        bool: True if API call succeeded, False otherwise
    """
    if not API_TOKEN:
        logger.warning("VIDEO_API_TOKEN not configured, skipping API call")
        return False

    try:
        url = f"{API_BASE_URL}/api/videos/create"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "task_id": task_id,
            "oss_url": oss_url
        }

        if video_name is not None:
            payload["video_name"] = video_name
        if resolution is not None:
            payload["resolution"] = resolution
        if framerate is not None:
            payload["framerate"] = framerate
        if duration is not None:
            payload["duration"] = duration
        if file_size is not None:
            payload["file_size"] = file_size
        if thumbnail_url is not None:
            payload["thumbnail_url"] = thumbnail_url
        if extra is not None:
            payload["extra"] = extra

        logger.info(f"Creating video record via API: {url}")

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get("success"):
            logger.info(f"Successfully created video record via API for task_id: {task_id}")
            return True
        else:
            logger.error(f"API returned success=False: {result.get('error')}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to call video creation API: {e!s}", exc_info=True)
        return False
