# 🎯 AI-Powered Interview Management Platform

A comprehensive, production-ready interview management system with AI-powered candidate screening, automated scheduling, and analytics.

## 🚀 Features

### 👤 User Roles
- **HR/Admin**: Job posting, application management, interview scheduling, offer letters, analytics
- **Candidates**: Registration, job applications, AI screening, interview tracking, status updates

### 🛠️ Tech Stack
- **Backend**: Django + Django REST Framework
- **Frontend**: React.js + Tailwind CSS + shadcn/ui
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4 for screening chatbot
- **Notifications**: Email (SendGrid) + SMS (Twilio)
- **Video**: Google Meet/Zoom API integration
- **Background Tasks**: Celery + Redis
- **Authentication**: JWT with role-based access
- **Deployment**: Docker + docker-compose

### ✨ Core Features
- 📝 Job posting and management
- 👥 Candidate registration and profile management
- 🤖 AI-powered screening chatbot with dynamic questions
- 📅 Interview scheduling with automated reminders
- 📊 Interviewer feedback and status pipeline
- 📄 Offer letter management
- 📈 Analytics dashboard

## 🏗️ Project Structure

```
interview-platform/
├── backend/                    # Django backend
│   ├── apps/                  # Django applications
│   │   ├── authentication/   # User management & JWT
│   │   ├── jobs/             # Job management
│   │   ├── candidates/       # Candidate profiles
│   │   ├── interviews/       # Interview scheduling
│   │   ├── chatbot/          # AI screening chatbot
│   │   ├── notifications/    # Email/SMS notifications
│   │   └── analytics/        # Dashboard analytics
│   ├── config/               # Django settings
│   ├── requirements.txt      # Python dependencies
│   └── manage.py
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   └── utils/           # Utilities
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml         # Docker orchestration
├── .env.example              # Environment template
└── docs/                     # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Docker and docker-compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd interview-platform
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/

### 4. Default Admin User
- Email: admin@example.com
- Password: admin123

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Background Tasks (Celery)
```bash
cd backend
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

## 🔐 Environment Variables

Create a `.env` file with the following variables:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=interview_platform
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourcompany.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Google Meet/Zoom
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
ZOOM_API_KEY=your-zoom-api-key
ZOOM_API_SECRET=your-zoom-api-secret
```

## 📚 API Documentation

The API is fully documented with Swagger/OpenAPI. Access it at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🤖 AI Chatbot Features

- **Dynamic Questions**: Questions adapt based on job requirements
- **Context Awareness**: Maintains conversation context
- **Summary Generation**: Automatically generates candidate summaries for HR
- **Admin Configuration**: HR can customize question sets per job
- **Multi-language Support**: Supports multiple languages

## 📊 Analytics Dashboard

- Application conversion rates
- Interview completion rates
- Time-to-hire metrics
- Source tracking
- Candidate pipeline visualization
- Custom reporting

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Input validation and sanitization
- Rate limiting
- CORS protection
- SQL injection prevention
- XSS protection

## 🚢 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### Environment-specific Configurations
- `docker-compose.yml`: Development
- `docker-compose.prod.yml`: Production
- `docker-compose.test.yml`: Testing

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@yourcompany.com or create an issue in the repository.

## 🗺️ Roadmap

- [ ] Mobile app development
- [ ] Advanced AI features (resume parsing, skill matching)
- [ ] Integration with more video platforms
- [ ] Advanced analytics and reporting
- [ ] Multi-tenant support
- [ ] API rate limiting and caching
- [ ] Real-time notifications via WebSocket