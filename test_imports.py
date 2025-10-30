"""
Test script to verify all imports and module structure
This should run successfully when dependencies are installed
"""

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    # Test config
    try:
        from app.config import config
        print("✓ Config module imported")
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'DATABASE_URL')
        print(f"  App name: {config.APP_NAME}")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    # Test models
    try:
        from app.models.video_render import VideoRender, RenderStatus
        print("✓ VideoRender model imported")
        assert hasattr(VideoRender, '__tablename__')
        assert VideoRender.__tablename__ == 'video_renders'
        statuses = [s.value for s in RenderStatus]
        print(f"  Available statuses: {statuses}")
        assert 'completed' in statuses
    except Exception as e:
        print(f"✗ Model import failed: {e}")
        return False
    
    # Test database session
    try:
        from app.db.session import SessionLocal, engine, Base
        print("✓ Database session module imported")
    except Exception as e:
        print(f"✗ Database session import failed: {e}")
        return False
    
    # Test Celery app
    try:
        from app.celery_app import celery_app
        print("✓ Celery app imported")
        assert celery_app.conf.task_serializer == 'json'
        print(f"  Task serializer: {celery_app.conf.task_serializer}")
    except Exception as e:
        print(f"✗ Celery app import failed: {e}")
        return False
    
    # Test tasks
    try:
        from app.tasks.video_tasks import (
            update_video_render_status,
            process_video_render_completion
        )
        print("✓ Video tasks imported")
        assert hasattr(update_video_render_status, 'delay')
        assert hasattr(process_video_render_completion, 'delay')
    except Exception as e:
        print(f"✗ Tasks import failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


if __name__ == "__main__":
    import sys
    success = test_imports()
    sys.exit(0 if success else 1)
