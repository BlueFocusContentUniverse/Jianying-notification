# Architecture Documentation

## System Overview

The Jianying Notification system is designed to handle video render status updates asynchronously using Celery workers. When a video rendering process completes, it triggers a task that updates the database with the render status and OSS link.

## Components

### 1. Celery Workers
- **Purpose**: Process asynchronous tasks for video render status updates
- **Location**: `app/celery_app.py`
- **Configuration**: 
  - Task serialization: JSON
  - Timezone: UTC
  - Time limits: 30 minutes hard, 25 minutes soft
  - Automatic retry on failure with exponential backoff

### 2. Redis
- **Purpose**: Message broker and result backend
- **Usage**:
  - Stores task queues
  - Caches task results
  - Enables task distribution across multiple workers

### 3. PostgreSQL Database
- **Purpose**: Persistent storage for video render records
- **Schema**: Single table `video_renders` with fields:
  - `id`: Primary key
  - `video_id`: Unique video identifier
  - `status`: Current render status (pending/processing/completed/failed)
  - `oss_link`: OSS URL to rendered video
  - `error_message`: Error details if failed
  - `created_at`, `updated_at`: Timestamps

### 4. Flower Dashboard
- **Purpose**: Real-time monitoring and management
- **Features**:
  - View active tasks
  - Monitor worker health
  - Inspect task history
  - Restart failed tasks

## Data Flow

```
Video Render System
       |
       | (triggers task)
       v
Celery Task Queue (Redis)
       |
       | (worker picks up task)
       v
Celery Worker
       |
       | (processes task)
       v
Update Database (PostgreSQL)
       |
       v
Return Result
```

## Task Processing Flow

### 1. Update Video Render Status
```
Client
  |
  | update_video_render_status.delay(video_id, status, oss_link)
  v
Task Queue
  |
  v
Celery Worker
  |
  |- Query database for existing record
  |- Create or update record
  |- Set status and OSS link
  |- Commit to database
  |
  v
Result (success/failure)
```

### 2. Process Video Render Completion
```
Video Render Complete Event
  |
  | process_video_render_completion.delay(video_id, oss_link)
  v
Task Queue
  |
  v
Celery Worker
  |
  |- Call update_video_render_status
  |- Set status to 'completed'
  |- Store OSS link
  |- Additional processing (notifications, etc.)
  |
  v
Database Updated
```

## Error Handling

### Automatic Retry
- Failed tasks are automatically retried up to 3 times
- Exponential backoff: 60 seconds between retries
- On final failure, status is set to 'failed' with error message

### Database Transactions
- All database operations are wrapped in transactions
- Automatic rollback on error
- Connection pooling prevents resource exhaustion

### Logging
- All operations are logged with appropriate levels
- Errors include stack traces for debugging
- Task IDs tracked throughout processing

## Scalability

### Horizontal Scaling
```bash
# Scale workers to handle more load
docker-compose up -d --scale celery-worker=5
```

### Worker Concurrency
```bash
# Adjust worker concurrency
celery -A app.celery_app worker --concurrency=8
```

### Queue Prioritization
Tasks can be routed to different queues based on priority:
```python
@celery_app.task(queue='high_priority')
def urgent_task():
    pass
```

## Security Considerations

1. **Non-root User**: Docker container runs as non-root user `celeryuser`
2. **Environment Variables**: Sensitive credentials stored in `.env` file (not committed)
3. **Database Connection**: Uses connection pooling with health checks
4. **Input Validation**: Task parameters validated before processing

## Monitoring

### Health Checks
- Redis: `redis-cli ping`
- PostgreSQL: `pg_isready`
- Celery Worker: Flower dashboard

### Metrics to Track
- Task success/failure rate
- Task processing time
- Queue length
- Worker utilization
- Database connection pool usage

## Deployment

### Docker Deployment
1. Configure `.env` file
2. Run `docker-compose up -d`
3. Initialize database with `init_db.py`
4. Monitor via Flower at http://localhost:5555

### Production Considerations
- Use managed Redis (e.g., AWS ElastiCache)
- Use managed PostgreSQL (e.g., AWS RDS)
- Set up log aggregation (e.g., ELK stack)
- Configure alerts for task failures
- Implement rate limiting for task submission
- Set up backup strategies for database

## Development Workflow

1. **Local Development**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Start services
   docker-compose up -d redis postgres
   
   # Run worker locally
   celery -A app.celery_app worker --loglevel=debug
   ```

2. **Testing**:
   ```bash
   # Submit test tasks
   python example_usage.py
   
   # Monitor via Flower
   celery -A app.celery_app flower
   ```

3. **Debugging**:
   - Check worker logs: `docker-compose logs -f celery-worker`
   - Use Flower to inspect failed tasks
   - Query database directly for state verification

## Future Enhancements

1. **Task Scheduling**: Implement periodic tasks with Celery Beat
2. **Webhooks**: Add webhook notifications on completion
3. **API Layer**: Create REST API for task submission
4. **Batch Processing**: Support bulk status updates
5. **Metrics Export**: Export metrics to Prometheus
6. **Dead Letter Queue**: Implement DLQ for permanently failed tasks
