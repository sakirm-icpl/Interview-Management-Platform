# 🚀 Complete Setup Guide - AI-Powered Interview Management Platform

This guide will walk you through setting up the complete AI-powered Interview Management Platform from scratch.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Node.js** (18+) and **npm** (9+) for local development
- **Python** (3.11+) and **pip** for local development
- **Git** for version control

## 🏗️ Quick Start with Docker

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repository-url>
cd interview-platform

# Create environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual configuration:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DB_NAME=interview_platform
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration (SendGrid)
SENDGRID_API_KEY=SG.your-sendgrid-api-key
FROM_EMAIL=noreply@yourcompany.com
SENDGRID_FROM_NAME=Interview Platform

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=ACyour-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Google Meet Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Build and Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d

# View logs
docker-compose logs -f
```

### 4. Initialize the Database

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create a superuser
docker-compose exec backend python manage.py createsuperuser

# Load initial data (optional)
docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/
- **Database Admin** (Adminer): http://localhost:8080

## 🛠️ Local Development Setup

For local development without Docker:

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup local database (PostgreSQL)
# Update .env with local database settings
DB_HOST=localhost

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Background Tasks (Celery)

```bash
cd backend

# Start Celery worker (new terminal)
celery -A config worker --loglevel=info

# Start Celery beat (new terminal)
celery -A config beat --loglevel=info

# Optional: Start Flower for monitoring
celery -A config flower
```

## 🔧 Configuration Details

### Required API Keys

1. **OpenAI API Key**
   - Sign up at https://platform.openai.com/
   - Create an API key in your account settings
   - Add to `OPENAI_API_KEY` in `.env`

2. **SendGrid API Key**
   - Sign up at https://sendgrid.com/
   - Create an API key with full access
   - Add to `SENDGRID_API_KEY` in `.env`

3. **Twilio Credentials**
   - Sign up at https://www.twilio.com/
   - Get Account SID, Auth Token, and phone number
   - Add to respective fields in `.env`

4. **Google Meet Integration**
   - Go to Google Cloud Console
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Add client ID and secret to `.env`

### Database Configuration

The platform uses PostgreSQL. For local development:

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
sudo -u postgres createdb interview_platform

# Create user
sudo -u postgres createuser --interactive
```

### Redis Configuration

Redis is used for Celery tasks and caching:

```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Redis
redis-server
```

## 📊 Features Overview

### 🎯 Core Features Implemented

1. **User Authentication & Authorization**
   - JWT-based authentication
   - Role-based access (Admin, HR, Candidate)
   - User registration and profile management
   - Password reset functionality

2. **Job Management**
   - Job posting with detailed requirements
   - Job categories and skill requirements
   - Application deadline management
   - Job search and filtering

3. **AI-Powered Screening**
   - OpenAI GPT-4 integration
   - Dynamic question generation
   - Candidate scoring and analysis
   - Conversation transcripts and summaries

4. **Application Management**
   - Application submission with documents
   - Status tracking pipeline
   - HR notes and feedback
   - Application analytics

5. **Email & SMS Notifications**
   - Welcome emails for new users
   - Application status updates
   - Interview reminders
   - Custom notification templates

6. **Background Tasks**
   - Celery for async processing
   - Scheduled notifications
   - Data processing tasks
   - Email queue management

### 🔮 Additional Features Ready for Development

1. **Interview Scheduling**
   - Calendar integration
   - Video meeting links
   - Automated reminders
   - Feedback collection

2. **Analytics Dashboard**
   - Application metrics
   - Conversion rates
   - Performance insights
   - Custom reports

3. **Advanced AI Features**
   - Resume parsing
   - Skill matching
   - Predictive scoring
   - Bias detection

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Create production environment file
cp .env.example .env.production

# Update with production settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### 2. Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 3. SSL/HTTPS Setup

Configure SSL certificates using Let's Encrypt:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 4. Monitoring and Logging

- Use Docker logs for monitoring: `docker-compose logs -f`
- Configure log rotation and retention
- Set up health checks and alerts
- Monitor resource usage

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Generate coverage report
npm test -- --coverage
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps db
   
   # View database logs
   docker-compose logs db
   ```

2. **Redis Connection Error**
   ```bash
   # Check Redis status
   docker-compose ps redis
   
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

3. **OpenAI API Errors**
   - Verify API key is correct
   - Check API rate limits
   - Ensure sufficient credits

4. **Email/SMS Not Working**
   - Verify API keys and credentials
   - Check service status pages
   - Review logs for error messages

### Performance Optimization

1. **Database Optimization**
   - Add database indexes
   - Optimize queries
   - Enable connection pooling

2. **Caching**
   - Implement Redis caching
   - Use CDN for static files
   - Enable browser caching

3. **Background Tasks**
   - Monitor Celery worker performance
   - Scale workers based on load
   - Optimize task execution

## 📝 API Documentation

The API is fully documented with Swagger/OpenAPI:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key API Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/jobs/` - List jobs
- `POST /api/jobs/` - Create job (HR only)
- `POST /api/jobs/{id}/apply/` - Apply for job
- `GET /api/chatbot/session/{id}/` - Chat session
- `POST /api/chatbot/message/` - Send message

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check this setup guide
2. Review the troubleshooting section
3. Check existing GitHub issues
4. Create a new issue with detailed information

## 🗺️ Next Steps

After successful setup:

1. **Customize the Platform**
   - Update branding and styling
   - Configure notification templates
   - Set up custom question templates

2. **Add Your Content**
   - Create job categories
   - Add skills to the database
   - Configure screening parameters

3. **Invite Users**
   - Create HR manager accounts
   - Set up candidate registration flow
   - Configure user roles and permissions

4. **Monitor and Optimize**
   - Set up logging and monitoring
   - Review performance metrics
   - Gather user feedback

Happy interviewing! 🎉