"""
Tasks module initialization
"""

from app.tasks.video_tasks import (
    update_video_render_status,
    process_video_render_completion
)

__all__ = [
    'update_video_render_status',
    'process_video_render_completion'
]
