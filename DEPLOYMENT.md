# Deployment Guide

This guide provides step-by-step instructions for deploying the Jianying Notification system in various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Docker 20.10+ and Docker Compose 2.0+
- OR Python 3.11+ (for manual deployment)
- Git

### Required Services
- Redis 6.0+
- PostgreSQL 13+

## Local Development

### Option 1: Using Docker Compose (Recommended)

1. **Clone and Configure**
   ```bash
   git clone <repository-url>
   cd Jianying-notification
   cp .env.example .env
   ```

2. **Start Services**
   ```bash
   ./start.sh
   # OR
   docker-compose up -d
   ```

3. **Initialize Database**
   ```bash
   docker-compose exec celery-worker python init_db.py
   ```

4. **Verify Deployment**
   ```bash
   # Check services
   docker-compose ps
   
   # View logs
   docker-compose logs -f celery-worker
   
   # Access Flower
   open http://localhost:5555
   ```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local Redis and PostgreSQL settings
   ```

3. **Initialize Database**
   ```bash
   python init_db.py
   ```

4. **Start Celery Worker**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

5. **Start Flower (Optional)**
   ```bash
   # In a new terminal
   celery -A app.celery_app flower
   ```

## Docker Deployment

### Building the Image

```bash
# Build image
docker build -t jianying-notification:latest .

# Tag for registry
docker tag jianying-notification:latest your-registry.com/jianying-notification:latest

# Push to registry
docker push your-registry.com/jianying-notification:latest
```

### Running with Docker

```bash
# Create network
docker network create jianying-network

# Run Redis
docker run -d \
  --name jianying-redis \
  --network jianying-network \
  redis:7-alpine

# Run PostgreSQL
docker run -d \
  --name jianying-postgres \
  --network jianying-network \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=jianying_notification \
  postgres:15-alpine

# Run Celery Worker
docker run -d \
  --name jianying-worker \
  --network jianying-network \
  --env-file .env \
  -e REDIS_HOST=jianying-redis \
  -e DATABASE_URL=postgresql://user:password@jianying-postgres:5432/jianying_notification \
  jianying-notification:latest
```

## Production Deployment

### AWS ECS Deployment

1. **Create Task Definition**
   ```json
   {
     "family": "jianying-notification",
     "containerDefinitions": [
       {
         "name": "celery-worker",
         "image": "your-ecr-repo/jianying-notification:latest",
         "memory": 512,
         "cpu": 256,
         "essential": true,
         "environment": [
           {
             "name": "REDIS_HOST",
             "value": "your-elasticache-endpoint"
           },
           {
             "name": "DATABASE_URL",
             "value": "postgresql://user:pass@your-rds-endpoint/db"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/jianying-notification",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "celery"
           }
         }
       }
     ]
   }
   ```

2. **Create ECS Service**
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name jianying-notification \
     --task-definition jianying-notification \
     --desired-count 2 \
     --launch-type FARGATE
   ```

### Google Cloud Run Deployment

1. **Build and Push**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/jianying-notification
   ```

2. **Deploy**
   ```bash
   gcloud run deploy jianying-notification \
     --image gcr.io/PROJECT_ID/jianying-notification \
     --set-env-vars REDIS_HOST=your-redis-host,DATABASE_URL=your-db-url \
     --platform managed \
     --region us-central1
   ```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name jianying-notification \
  --image your-registry.azurecr.io/jianying-notification:latest \
  --environment-variables \
    REDIS_HOST=your-redis-host \
    DATABASE_URL=your-db-url \
  --cpu 1 \
  --memory 1
```

## Kubernetes Deployment

### 1. Create ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: jianying-notification-config
data:
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  LOG_LEVEL: "INFO"
```

### 2. Create Secret

```bash
kubectl create secret generic jianying-notification-secret \
  --from-literal=DATABASE_URL='postgresql://user:pass@postgres:5432/db'
```

### 3. Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jianying-notification
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jianying-notification
  template:
    metadata:
      labels:
        app: jianying-notification
    spec:
      containers:
      - name: celery-worker
        image: your-registry.com/jianying-notification:latest
        envFrom:
        - configMapRef:
            name: jianying-notification-config
        - secretRef:
            name: jianying-notification-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### 4. Deploy

```bash
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
```

### 5. Horizontal Pod Autoscaling

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jianying-notification-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jianying-notification
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_HOST` | Redis server hostname | `redis` or `my-redis.cache.amazonaws.com` |
| `REDIS_PORT` | Redis server port | `6379` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_DB` | Redis database number | `0` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `APP_NAME` | Application name | `Jianying-Notification` |

## Health Checks

### Celery Worker Health

```bash
# Check worker status
celery -A app.celery_app inspect active

# Check registered tasks
celery -A app.celery_app inspect registered
```

### Database Health

```bash
# Using psql
psql $DATABASE_URL -c "SELECT 1"

# Using Python
python -c "from app.db.session import engine; engine.connect()"
```

### Redis Health

```bash
redis-cli -h $REDIS_HOST ping
```

## Monitoring Setup

### Prometheus + Grafana

1. **Install Celery Exporter**
   ```bash
   pip install celery-exporter
   celery-exporter --broker-url=$CELERY_BROKER_URL
   ```

2. **Configure Prometheus**
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'celery'
       static_configs:
         - targets: ['celery-exporter:9540']
   ```

### AWS CloudWatch

Add to task definition:
```json
"logConfiguration": {
  "logDriver": "awslogs",
  "options": {
    "awslogs-group": "/ecs/jianying-notification",
    "awslogs-region": "us-east-1",
    "awslogs-stream-prefix": "celery"
  }
}
```

## Backup and Disaster Recovery

### Database Backup

```bash
# Automated daily backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240101.sql
```

### Redis Backup

```bash
# Enable AOF persistence in redis.conf
appendonly yes

# Or use RDB snapshots
save 900 1
save 300 10
save 60 10000
```

## Troubleshooting

### Worker Not Processing Tasks

1. Check worker is running:
   ```bash
   docker-compose ps celery-worker
   ```

2. Check worker logs:
   ```bash
   docker-compose logs -f celery-worker
   ```

3. Check Redis connection:
   ```bash
   redis-cli -h $REDIS_HOST ping
   ```

### Database Connection Issues

1. Verify connection string:
   ```bash
   echo $DATABASE_URL
   ```

2. Test connection:
   ```bash
   psql $DATABASE_URL -c "SELECT version()"
   ```

3. Check network:
   ```bash
   docker network inspect jianying-network
   ```

### High Memory Usage

1. Adjust worker concurrency:
   ```bash
   celery -A app.celery_app worker --concurrency=2
   ```

2. Enable max-tasks-per-child:
   ```bash
   celery -A app.celery_app worker --max-tasks-per-child=100
   ```

## Rollback Procedure

1. **Identify last good version**:
   ```bash
   docker images | grep jianying-notification
   ```

2. **Rollback deployment**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Verify**:
   ```bash
   docker-compose logs -f
   ```

## Security Checklist

- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable SSL/TLS for Redis and PostgreSQL
- [ ] Run containers as non-root user
- [ ] Use network policies in Kubernetes
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Use VPC/private networks

## Performance Tuning

### Worker Optimization

```python
# In celery_app.py
celery_app.conf.update(
    worker_prefetch_multiplier=1,  # Disable prefetching
    worker_max_tasks_per_child=1000,  # Restart after 1000 tasks
    task_acks_late=True,  # Acknowledge after task completion
)
```

### Database Connection Pool

```python
# In db/session.py
engine = create_engine(
    config.DATABASE_URL,
    pool_size=20,  # Increase pool size
    max_overflow=40,  # Allow more overflow connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600  # Recycle connections every hour
)
```

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See README.md and ARCHITECTURE.md
