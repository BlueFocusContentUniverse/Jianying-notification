"""
Example usage of the Celery tasks

This script demonstrates how to trigger the video render tasks.
"""

from app.tasks.video_tasks import (
    update_video_render_status,
    process_video_render_completion
)


def example_update_status():
    """Example: Update video render status"""
    
    # Example 1: Mark video as processing
    task = update_video_render_status.delay(
        video_id="video_123",
        status="processing"
    )
    print(f"Task submitted: {task.id}")
    
    # Example 2: Mark video as completed with OSS link
    task = update_video_render_status.delay(
        video_id="video_456",
        status="completed",
        oss_link="https://oss.example.com/videos/video_456.mp4"
    )
    print(f"Task submitted: {task.id}")
    
    # Example 3: Mark video as failed
    task = update_video_render_status.delay(
        video_id="video_789",
        status="failed",
        error_message="Encoding error: Invalid codec"
    )
    print(f"Task submitted: {task.id}")


def example_process_completion():
    """Example: Process video render completion"""
    
    task = process_video_render_completion.delay(
        video_id="video_999",
        oss_link="https://oss.example.com/videos/video_999.mp4"
    )
    print(f"Completion task submitted: {task.id}")


if __name__ == "__main__":
    print("=== Video Render Status Update Examples ===\n")
    
    print("1. Updating video render statuses...")
    example_update_status()
    
    print("\n2. Processing video render completion...")
    example_process_completion()
    
    print("\nTasks submitted! Check Celery worker logs for processing status.")
    print("You can also monitor tasks using Flower at http://localhost:5555")
