# AI-Powered Interview Management Platform

A complete, production-ready platform for managing job applications, AI-powered screening, and interview processes.

## 🚀 Features

### 👤 User Roles
- **HR/Admin**: Post jobs, manage applications, schedule interviews, upload offer letters, view analytics
- **Candidates**: Register, apply for jobs, attend AI screening, view schedules, track status

### 🔧 Tech Stack
- **Backend**: Django + Django REST Framework
- **Frontend**: React.js + Tailwind CSS + shadcn/ui
- **Database**: PostgreSQL
- **AI Chatbot**: OpenAI GPT-4 with dynamic questions
- **Notifications**: Email (SendGrid) + SMS (Twilio)
- **Video**: Google Meet integration
- **Background Tasks**: Celery + Redis
- **Authentication**: JWT with role-based access
- **Deployment**: Dockerized with docker-compose

### ✅ Core Features
- Job posting and management
- Candidate registration and profile management
- AI screening chatbot with job-specific questions
- Interview scheduling with calendar integration
- Feedback forms and status pipeline
- Offer letter management
- Analytics dashboard
- Real-time notifications

## 🏗️ Project Structure

```
interview-platform/
├── backend/                 # Django backend
│   ├── core/               # Core models and utilities
│   ├── users/              # User management
│   ├── jobs/               # Job posting and applications
│   ├── interviews/         # Interview scheduling
│   ├── chatbot/            # AI screening system
│   ├── offers/             # Offer letter management
│   ├── notifications/      # Email/SMS notifications
│   ├── analytics/          # HR analytics dashboard
│   └── config/             # Django settings
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── public/
├── docker-compose.yml      # Production deployment
└── .env.example           # Environment variables
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis

### 1. Clone and Setup
```bash
git clone <repository-url>
cd interview-platform
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker
```bash
docker-compose up -d
```

### 3. Setup Database
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py loaddata seed_data
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## 📚 API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 🔐 Environment Variables

Create a `.env` file with the following variables:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/interview_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourcompany.com

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Google Meet
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1
```

## 🧪 Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
cd frontend && npm test
```

## 📊 Analytics

The platform includes comprehensive analytics for HR:
- Application conversion rates
- Interview success rates
- Time-to-hire metrics
- Candidate pipeline status
- Department-wise hiring trends

## 🤖 AI Chatbot

The AI screening system features:
- Job-specific question generation
- Dynamic conversation flow
- Answer summarization for HR
- Skill assessment scoring
- Cultural fit evaluation

## 📱 Notifications

Automated notifications include:
- Application confirmations
- Interview reminders (email + SMS)
- Status updates
- Offer letter notifications
- Calendar invites

## 🚀 Production Deployment

1. Set up production environment variables
2. Configure SSL certificates
3. Set up monitoring and logging
4. Configure backup strategies
5. Deploy using docker-compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

Built with ❤️ for modern HR teams
