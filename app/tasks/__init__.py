"""
Tasks module initialization
"""

from app.tasks.video_tasks import (
    process_video_render_completion,
    update_video_render_status,
)

__all__ = [
    "process_video_render_completion",
    "update_video_render_status"
]
