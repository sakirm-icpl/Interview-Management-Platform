# Production Deployment Guide

## Overview

This guide covers deploying the AI-Powered Interview Management Platform to production environments. The platform is designed to be deployed using Docker and can run on various cloud providers.

## Prerequisites

- Docker and Docker Compose installed
- Domain name and SSL certificate
- Cloud provider account (AWS, GCP, Azure, etc.)
- Database (PostgreSQL)
- Redis instance
- Email service (SendGrid, AWS SES, etc.)
- SMS service (Twilio, AWS SNS, etc.)
- OpenAI API key
- Google Calendar API credentials (optional)

## Environment Configuration

### 1. Production Environment Variables

Create a `.env.prod` file with production settings:

```env
# Django Configuration
SECRET_KEY=your-super-secure-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://username:password@your-db-host:5432/interview_platform

# Redis Configuration
REDIS_URL=redis://your-redis-host:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Email Configuration
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Interview Platform

# SMS Configuration
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Google Calendar Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1

# Security Configuration
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Production Configuration
PRODUCTION=True
ENVIRONMENT=production
```

### 2. SSL Certificate

Obtain an SSL certificate for your domain:
- Let's Encrypt (free)
- Cloud provider SSL certificates
- Third-party certificates

## Cloud Provider Deployment

### AWS Deployment

#### 1. EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Minimum specs: 2 vCPU, 4GB RAM, 20GB storage

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
```

#### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/your-repo/interview-platform.git
cd interview-platform

# Copy production environment file
cp .env.prod .env

# Build and start containers
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load seed data
docker-compose exec backend python manage.py loaddata seed_data.json
```

#### 3. RDS Database Setup

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
    --db-instance-identifier interview-platform-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password your-password \
    --allocated-storage 20
```

#### 4. ElastiCache Redis Setup

```bash
# Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id interview-platform-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

### Google Cloud Platform (GCP) Deployment

#### 1. Compute Engine Setup

```bash
# Create VM instance
gcloud compute instances create interview-platform \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
```

#### 2. Cloud SQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create interview-platform-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1
```

#### 3. Cloud Run Deployment (Alternative)

```bash
# Build and push Docker images
docker build -t gcr.io/your-project/interview-backend ./backend
docker build -t gcr.io/your-project/interview-frontend ./frontend

docker push gcr.io/your-project/interview-backend
docker push gcr.io/your-project/interview-frontend

# Deploy to Cloud Run
gcloud run deploy interview-backend \
    --image gcr.io/your-project/interview-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated

gcloud run deploy interview-frontend \
    --image gcr.io/your-project/interview-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Azure Deployment

#### 1. Azure Container Instances

```bash
# Create resource group
az group create --name interview-platform --location eastus

# Create container registry
az acr create --resource-group interview-platform \
    --name interviewplatform --sku Basic

# Build and push images
az acr build --registry interviewplatform --image backend .
az acr build --registry interviewplatform --image frontend .

# Deploy containers
az container create \
    --resource-group interview-platform \
    --name interview-backend \
    --image interviewplatform.azurecr.io/backend \
    --ports 8000 \
    --environment-variables DATABASE_URL=your-db-url
```

## Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_files:/var/www/static
      - media_files:/var/www/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    volumes:
      - media_files:/app/media
      - static_files:/app/static
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped
    command: celery -A config worker --loglevel=info

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped
    command: celery -A config beat --loglevel=info

volumes:
  static_files:
  media_files:
```

## Production Nginx Configuration

Create `nginx/nginx.prod.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Login with stricter rate limiting
        location /api/auth/login/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Admin panel
        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Media files
        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }
        
        # Health check
        location /health/ {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
```

## Production Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
```

## Monitoring and Logging

### 1. Application Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
    restart: unless-stopped

volumes:
  grafana_data:
```

### 2. Log Aggregation

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.0
    volumes:
      - ./logs:/var/log/app
      - ./monitoring/filebeat.yml:/usr/share/filebeat/filebeat.yml

volumes:
  elasticsearch_data:
```

## Backup Strategy

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
docker-compose exec -T postgres pg_dump -U interview_user interview_platform > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C /app/media .

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql s3://your-backup-bucket/
aws s3 cp $BACKUP_DIR/media_backup_$DATE.tar.gz s3://your-backup-bucket/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 2. Automated Backup Cron Job

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

## Security Considerations

### 1. Firewall Configuration

```bash
# UFW firewall setup
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Regular Security Updates

```bash
# Automated security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Database Security

```sql
-- Create read-only user for analytics
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE interview_platform TO analytics_user;
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_job_applications_status ON jobs_jobapplication(status);
CREATE INDEX idx_job_applications_created ON jobs_jobapplication(created_at);
CREATE INDEX idx_interviews_scheduled ON interviews_interview(scheduled_at);
```

### 2. Caching Strategy

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache frequently accessed data
CACHE_TTL = 60 * 15  # 15 minutes
```

### 3. CDN Configuration

```nginx
# nginx.conf
location /static/ {
    proxy_pass http://your-cdn-url;
    proxy_set_header Host $host;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Scaling Considerations

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}

  celery_worker:
    deploy:
      replicas: 2
```

### 2. Load Balancer

```nginx
# nginx load balancer
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker-compose exec backend python manage.py dbshell
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

3. **Static Files Not Loading**
   ```bash
   # Recollect static files
   docker-compose exec backend python manage.py collectstatic --noinput
   ```

4. **Celery Tasks Not Running**
   ```bash
   # Check Celery status
   docker-compose exec backend celery -A config inspect active
   ```

### Log Analysis

```bash
# View application logs
docker-compose logs -f backend

# View nginx logs
docker-compose logs -f nginx

# View database logs
docker-compose logs -f postgres
```

## Maintenance

### 1. Regular Maintenance Tasks

```bash
#!/bin/bash
# maintenance.sh

# Update dependencies
docker-compose pull
docker-compose build --no-cache

# Run migrations
docker-compose exec backend python manage.py migrate

# Clear old sessions
docker-compose exec backend python manage.py clearsessions

# Update search index
docker-compose exec backend python manage.py update_index

# Restart services
docker-compose restart
```

### 2. Health Checks

```python
# health_check.py
import requests
import sys

def check_health():
    try:
        response = requests.get('https://yourdomain.com/health/')
        if response.status_code == 200:
            print("✅ Application is healthy")
            return True
        else:
            print("❌ Application health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
```

## Support and Maintenance

### 1. Monitoring Alerts

Set up alerts for:
- High CPU/Memory usage
- Database connection errors
- Application errors (5xx responses)
- Disk space usage
- SSL certificate expiration

### 2. Incident Response

1. **Immediate Response**
   - Check application logs
   - Verify database connectivity
   - Check external service status

2. **Escalation**
   - Contact on-call engineer
   - Notify stakeholders
   - Document incident

3. **Resolution**
   - Implement fix
   - Test thoroughly
   - Deploy to production

4. **Post-Incident**
   - Conduct post-mortem
   - Update runbooks
   - Implement preventive measures

This deployment guide provides a comprehensive approach to deploying the Interview Management Platform in production. Follow the security best practices and monitor the application closely after deployment.