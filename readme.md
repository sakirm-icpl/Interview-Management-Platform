interview-platform/
├── backend/
│   ├── core/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── chatbot/
│   │   ├── views.py
│   │   ├── serializers.py
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   ├── interviews/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   ├── offers/
│   │   ├── models.py
│   │   ├── views.py
│   ├── notifications/
│   │   ├── tasks.py
│   ├── config/
│   │   ├── celery.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── ... (React files)
├── docker-compose.yml
└── .env
