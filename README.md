# Jianying-notification

A message queue notification Python project using Celery workers to handle video render status updates. When video rendering is completed with an OSS link, it updates the database record automatically.

## Features

- 🚀 Celery worker for asynchronous task processing
- 📹 Video render status tracking and updates
- 🗄️ PostgreSQL database integration with SQLAlchemy
- 🔄 Redis as message broker and result backend
- 🐳 Docker containerization support
- 🌸 Flower monitoring dashboard
- ⚙️ Environment-based configuration

## Architecture

- **Celery Workers**: Process video render status update tasks
- **Redis**: Message broker and result backend for Celery
- **PostgreSQL**: Database for storing video render records
- **Flower**: Real-time monitoring of Celery tasks

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+, Redis, and PostgreSQL

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Jianying-notification
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration if needed.

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec celery-worker python init_db.py
   ```

5. **Access Flower dashboard**
   
   Open http://localhost:5555 in your browser to monitor Celery tasks.

## Manual Setup (without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Redis and PostgreSQL credentials
   ```

3. **Initialize database**
   ```bash
   python init_db.py
   ```

4. **Start Celery worker**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

5. **Start Flower (optional)**
   ```bash
   celery -A app.celery_app flower
   ```

## Usage

### Triggering Tasks

You can trigger video render status update tasks in several ways:

1. **Using Python code**:
   ```python
   from app.tasks.video_tasks import update_video_render_status, process_video_render_completion
   
   # Update status to processing
   task = update_video_render_status.delay(
       video_id="video_123",
       status="processing"
   )
   
   # Process completion with OSS link
   task = process_video_render_completion.delay(
       video_id="video_123",
       oss_link="https://oss.example.com/videos/video_123.mp4"
   )
   ```

2. **Run example script**:
   ```bash
   python example_usage.py
   ```

3. **Using Celery CLI**:
   ```bash
   celery -A app.celery_app call app.tasks.update_video_render_status \
     --args='["video_123", "completed"]' \
     --kwargs='{"oss_link": "https://oss.example.com/video.mp4"}'
   ```

### Video Render Statuses

The system supports the following statuses:
- `pending`: Video is queued for rendering
- `processing`: Video is currently being rendered
- `completed`: Video rendering completed successfully
- `failed`: Video rendering failed

## Database Schema

### VideoRender Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| video_id | String | Unique video identifier |
| status | Enum | Current render status |
| oss_link | String | OSS link to rendered video |
| error_message | String | Error message if failed |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

- `REDIS_HOST`: Redis server hostname
- `REDIS_PORT`: Redis server port
- `REDIS_DB`: Redis database number
- `DATABASE_URL`: PostgreSQL connection string
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `LOG_LEVEL`: Application log level

## Development

### Project Structure

```
Jianying-notification/
├── app/
│   ├── __init__.py
│   ├── celery_app.py          # Celery application configuration
│   ├── config.py               # Configuration management
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py          # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── video_render.py     # VideoRender model
│   └── tasks/
│       ├── __init__.py
│       └── video_tasks.py      # Celery tasks
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── example_usage.py            # Example usage script
├── init_db.py                  # Database initialization script
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

### Running Tests

```bash
# Add tests as needed
pytest
```

## Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f celery-worker

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Scale workers
docker-compose up -d --scale celery-worker=3
```

## Monitoring

### Flower Dashboard

Access Flower at http://localhost:5555 to:
- Monitor active tasks
- View task history
- Check worker status
- Inspect task details

### Logs

```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# View all logs
docker-compose logs -f
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Ensure Redis and PostgreSQL are running
2. Check `.env` file for correct credentials
3. Verify network connectivity between services

### Task Not Processing

1. Check Celery worker is running
2. Verify Redis connection
3. Check Flower dashboard for task status
4. Review worker logs for errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license here]
