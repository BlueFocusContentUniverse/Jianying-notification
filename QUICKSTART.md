# Quick Start Guide

Get the Jianying Notification system up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+ with Redis and PostgreSQL

## Option 1: Docker (Recommended) ⚡

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Jianying-notification
cp .env.example .env
```

### 2. Start Everything
```bash
./start.sh
```

That's it! The system is now running with:
- ✅ Celery workers processing tasks
- ✅ Redis message broker
- ✅ PostgreSQL database
- ✅ Flower monitoring dashboard at http://localhost:5555

### 3. Test the System

Run the example script to submit test tasks:
```bash
docker-compose exec celery-worker python example_usage.py
```

Watch the tasks being processed:
- View logs: `docker-compose logs -f celery-worker`
- View Flower dashboard: Open http://localhost:5555 in your browser

## Option 2: Manual Setup 🔧

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Redis and PostgreSQL settings
```

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Start Celery Worker
```bash
celery -A app.celery_app worker --loglevel=info
```

### 5. (Optional) Start Flower Dashboard
In a new terminal:
```bash
celery -A app.celery_app flower
```

### 6. Test the System
In another terminal:
```bash
python example_usage.py
```

## Basic Usage

### Submit a Task (Python)

```python
from app.tasks.video_tasks import process_video_render_completion

# Process a completed video render
task = process_video_render_completion.delay(
    video_id="video_12345",
    oss_link="https://oss.example.com/videos/video_12345.mp4"
)

print(f"Task submitted: {task.id}")
```

### Update Video Status

```python
from app.tasks.video_tasks import update_video_render_status

# Update to processing
update_video_render_status.delay(
    video_id="video_12345",
    status="processing"
)

# Update to completed with OSS link
update_video_render_status.delay(
    video_id="video_12345",
    status="completed",
    oss_link="https://oss.example.com/videos/video_12345.mp4"
)

# Mark as failed
update_video_render_status.delay(
    video_id="video_12345",
    status="failed",
    error_message="Encoding error"
)
```

## Monitoring

### Flower Dashboard
Access at http://localhost:5555 to:
- 📊 Monitor active and completed tasks
- 🔍 Inspect task details and results
- 📈 View worker statistics
- 🔄 Retry failed tasks

### Logs
```bash
# View all logs
docker-compose logs -f

# View worker logs only
docker-compose logs -f celery-worker

# View last 100 lines
docker-compose logs --tail=100 celery-worker
```

## Common Commands

### Docker Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart workers
docker-compose restart celery-worker

# Scale workers
docker-compose up -d --scale celery-worker=3

# View service status
docker-compose ps
```

### Celery Commands
```bash
# Check active tasks
celery -A app.celery_app inspect active

# Check registered tasks
celery -A app.celery_app inspect registered

# Purge all tasks
celery -A app.celery_app purge

# Check worker stats
celery -A app.celery_app inspect stats
```

## Database Operations

### View Records
```bash
# Connect to database
docker-compose exec postgres psql -U user -d jianying_notification

# Query video renders
SELECT * FROM video_renders ORDER BY created_at DESC LIMIT 10;
```

### Initialize/Reset Database
```bash
docker-compose exec celery-worker python init_db.py
```

## Troubleshooting

### Workers Not Processing Tasks
```bash
# Check if workers are running
docker-compose ps celery-worker

# Check worker logs
docker-compose logs -f celery-worker

# Restart workers
docker-compose restart celery-worker
```

### Can't Connect to Redis
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Should respond with: PONG

# Check Redis logs
docker-compose logs redis
```

### Database Issues
```bash
# Check database is running
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Reinitialize database
docker-compose exec celery-worker python init_db.py
```

## Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Overview and features
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Customize for Your Needs**
   - Modify tasks in `app/tasks/video_tasks.py`
   - Adjust configuration in `.env`
   - Add new models in `app/models/`

3. **Deploy to Production**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment guides
   - Configure monitoring and alerting
   - Set up automated backups

## Getting Help

- Check logs: `docker-compose logs -f`
- View Flower dashboard: http://localhost:5555
- Review documentation files in the repository
- Check GitHub issues for common problems

## Clean Up

To completely remove all containers and data:
```bash
docker-compose down -v
```

---

**Congratulations!** 🎉 You now have a working Celery-based video render notification system!
