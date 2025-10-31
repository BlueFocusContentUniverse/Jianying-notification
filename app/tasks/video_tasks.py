"""
Celery tasks for video render status updates
"""

import logging
from typing import Optional
from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.video_render import VideoRender, RenderStatus

# Configure logging
logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='app.tasks.update_video_render_status')
def update_video_render_status(
    self,
    video_id: str,
    status: str,
    oss_link: Optional[str] = None,
    error_message: Optional[str] = None
):
    """
    Update video render status in the database.
    
    Args:
        video_id: Unique identifier for the video
        status: New status (pending, processing, completed, failed)
        oss_link: OSS link to the rendered video (optional)
        error_message: Error message if render failed (optional)
    
    Returns:
        dict: Result with success status and message
    """
    db = SessionLocal()
    try:
        logger.info(f"Updating video render status for video_id: {video_id}, status: {status}")
        
        # Find the video render record
        video_render = db.query(VideoRender).filter(
            VideoRender.video_id == video_id
        ).first()
        
        if not video_render:
            # Create new record if it doesn't exist
            logger.info(f"Creating new video render record for video_id: {video_id}")
            video_render = VideoRender(
                video_id=video_id,
                status=RenderStatus(status)
            )
            db.add(video_render)
        else:
            # Update existing record
            logger.info(f"Updating existing video render record for video_id: {video_id}")
            video_render.status = RenderStatus(status)
        
        # Update OSS link if provided
        if oss_link:
            video_render.oss_link = oss_link
            logger.info(f"OSS link updated: {oss_link}")
        
        # Update error message if provided
        if error_message:
            video_render.error_message = error_message
            logger.error(f"Error message: {error_message}")
        
        # Commit changes
        db.commit()
        db.refresh(video_render)
        
        logger.info(f"Successfully updated video render status for video_id: {video_id}")
        
        return {
            'success': True,
            'message': f'Video render status updated successfully',
            'video_id': video_id,
            'status': status,
            'oss_link': oss_link
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating video render status: {str(e)}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)
        
    finally:
        db.close()


@celery_app.task(bind=True, name='app.tasks.process_video_render_completion')
def process_video_render_completion(
    self,
    video_id: str,
    oss_link: str
):
    """
    Process video render completion and update database with OSS link.
    
    This task is triggered when video rendering is completed and 
    an OSS link is available.
    
    Args:
        video_id: Unique identifier for the video
        oss_link: OSS link to the rendered video
    
    Returns:
        dict: Result with success status and message
    """
    logger.info(f"Processing video render completion for video_id: {video_id}")
    
    try:
        # Update status to completed with OSS link
        result = update_video_render_status(
            video_id=video_id,
            status='completed',
            oss_link=oss_link
        )
        
        logger.info(f"Video render completed successfully for video_id: {video_id}")
        
        # Here you can add additional processing logic like:
        # - Sending notifications
        # - Triggering downstream processes
        # - Updating caches
        # - etc.
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing video render completion: {str(e)}", exc_info=True)
        # Update status to failed
        update_video_render_status(
            video_id=video_id,
            status='failed',
            error_message=str(e)
        )
        raise self.retry(exc=e, countdown=60, max_retries=3)
