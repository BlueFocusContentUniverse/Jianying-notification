"""
Video Render model for tracking video rendering status
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.db.session import Base
import enum


class RenderStatus(enum.Enum):
    """Enum for video render status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoRender(Base):
    """
    VideoRender model to store video rendering information
    """
    __tablename__ = "video_renders"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(RenderStatus), default=RenderStatus.PENDING, nullable=False)
    oss_link = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VideoRender(id={self.id}, video_id={self.video_id}, status={self.status.value})>"
