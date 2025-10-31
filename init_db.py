"""
Database initialization script
Creates all tables defined in the models
"""

import logging
from app.db.session import engine, Base
from app.models import VideoRender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize database by creating all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


if __name__ == "__main__":
    init_db()
