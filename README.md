# Jianying-notification

A message queue notification Python project using Celery workers to handle video render status updates. When video rendering is completed with an OSS link, it processes the notification asynchronously.

## Features

- 🚀 Celery worker for asynchronous task processing
- 📹 Video render status tracking and updates
- 🔄 Redis as message broker and result backend
- 🐳 Docker containerization support
- 🌸 Flower monitoring dashboard
- ⚙️ Environment-based configuration

## Architecture

- **Celery Workers**: Process video render status update tasks
- **Redis**: Message broker and result backend for Celery
- **Flower**: Real-time monitoring of Celery tasks

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.14+ and Redis

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

4. **Access Flower dashboard**
   
   Open http://localhost:5555 in your browser to monitor Celery tasks.

## Manual Setup (without Docker)

1. **Install dependencies**
   ```bash
   pip install .
   ```
   
   Or for development with optional dependencies:
   ```bash
   pip install ".[dev]"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Redis credentials
   ```

3. **Start Celery worker**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

4. **Start Flower (optional)**
   ```bash
   celery -A app.celery_app flower
   ```

## Usage

### Triggering Tasks

The Celery tasks automatically call the video management APIs when video status changes. You can trigger video render status update tasks in several ways:

1. **Using Python code**:
   ```python
   from app.tasks.video_tasks import update_video_render_status, process_video_render_completion
   
   # Update status to processing
   task = update_video_render_status.delay(
       video_id="video_123",
       status="processing",
       task_id="task_456",  # Optional: task ID for API updates
       draft_id="draft_789",  # Optional: draft ID
       progress=50.0  # Optional: progress percentage
   )
   
   # Process completion with OSS link
   task = process_video_render_completion.delay(
       video_id="video_123",
       oss_url="https://oss.example.com/videos/video_123.mp4",
       task_id="task_456",  # Optional: task ID
       draft_id="draft_789",  # Optional: draft ID
       video_name="My Video",  # Optional: video metadata
       resolution="1920x1080",
       duration=120.5
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

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

- `REDIS_HOST`: Redis server hostname
- `REDIS_PORT`: Redis server port
- `REDIS_DB`: Redis database number
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `LOG_LEVEL`: Application log level
- `VIDEO_API_BASE_URL`: Base URL for video management API (e.g., http://localhost:5000)
- `VIDEO_API_TOKEN`: Bearer token for authenticating with video management API

### API Integration

When video status changes, the tasks automatically call the video management APIs:

- **Update Task Status**: `PUT /api/video-tasks/{task_id}/status` - Updates video task progress and status
- **Create Video Record**: `POST /api/videos` - Creates a video record when rendering completes

All API calls use Bearer token authentication:
```
Authorization: Bearer ${VIDEO_API_TOKEN}
```

To enable API integration:
1. Set `VIDEO_API_BASE_URL` to your video API endpoint
2. Set `VIDEO_API_TOKEN` to your authentication token
3. The tasks will automatically call the APIs when processing video status changes

## Development

### Project Structure

```
Jianying-notification/
├── app/
│   ├── __init__.py
│   ├── celery_app.py          # Celery application configuration
│   ├── config.py               # Configuration management
│   ├── api/                    # API client modules
│   │   ├── __init__.py
│   │   └── video_api_client.py # Video management API client
│   └── tasks/
│       ├── __init__.py
│       └── video_tasks.py      # Celery tasks
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── example_usage.py            # Example usage script
├── pyproject.toml              # Python dependencies and project metadata
└── README.md                   # This file
```

## Monitoring

### Flower Dashboard

Access Flower at http://localhost:5555 to:
- Monitor active tasks
- View task history
- Check worker status
- Inspect task details

## Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Ensure Redis is running
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
