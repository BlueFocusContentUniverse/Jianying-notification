#!/bin/bash
echo "Starting Jianying Notification Celery Worker..."
celery -A app.celery_app worker --loglevel=info -Q notifications
