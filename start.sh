#!/bin/bash

# Startup script for Jianying Notification system

set -e

echo "Starting Jianying Notification System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Start services with docker-compose
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Initialize database
echo "Initializing database..."
docker-compose exec -T celery-worker python init_db.py

echo ""
echo "============================================"
echo "✅ Jianying Notification System is running!"
echo "============================================"
echo ""
echo "Services:"
echo "  - Celery Worker: Running"
echo "  - Redis: Running on port 6379"
echo "  - PostgreSQL: Running on port 5432"
echo "  - Flower Dashboard: http://localhost:5555"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
