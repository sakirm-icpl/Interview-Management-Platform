# API Documentation

## Overview

The Interview Management Platform API provides comprehensive endpoints for managing job applications, interviews, AI screening, and user management. The API follows RESTful principles and uses JWT authentication.

**Base URL**: `http://localhost:8000/api`

**Authentication**: Bearer Token (JWT)

## Authentication

### Login
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "candidate",
    "is_verified": true
  }
}
```

### Register
```http
POST /v1/users/users/register/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "password123",
  "password_confirm": "password123",
  "phone_number": "+1234567890",
  "role": "candidate"
}
```

### Refresh Token
```http
POST /auth/token/refresh/
Content-Type: application/json

{
  "refresh": "refresh_token_here"
}
```

## User Management

### Get Current User
```http
GET /v1/users/users/me/
Authorization: Bearer <access_token>
```

### Update User Profile
```http
PATCH /v1/users/users/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "phone_number": "+1234567890",
  "bio": "Updated bio"
}
```

### Change Password
```http
POST /v1/users/users/change_password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "current_password",
  "new_password": "new_password",
  "new_password_confirm": "new_password"
}
```

### Request Password Reset
```http
POST /v1/users/users/request_password_reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Reset Password
```http
POST /v1/users/users/reset_password/
Content-Type: application/json

{
  "token": "reset_token",
  "new_password": "new_password",
  "new_password_confirm": "new_password"
}
```

### Verify Email
```http
POST /v1/users/users/verify_email/
Content-Type: application/json

{
  "token": "verification_token"
}
```

## Job Management

### List Jobs
```http
GET /v1/jobs/jobs/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `q`: Search query
- `department`: Department filter
- `employment_type`: Employment type filter
- `experience_level`: Experience level filter
- `work_model`: Work model filter
- `location`: Location filter
- `min_salary`: Minimum salary
- `max_salary`: Maximum salary
- `skills`: Skills filter (comma-separated)
- `is_active`: Active jobs only

**Response**:
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/jobs/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Senior Software Engineer",
      "department_name": "Engineering",
      "employment_type": "full_time",
      "experience_level": "senior",
      "work_model": "hybrid",
      "location": "San Francisco, CA",
      "salary_min": 120000.00,
      "salary_max": 180000.00,
      "salary_currency": "USD",
      "is_open_for_applications": true,
      "posted_by_name": "HR Manager",
      "created_at": "2024-01-01T00:00:00Z",
      "views_count": 150,
      "applications_count": 25
    }
  ]
}
```

### Get Job Details
```http
GET /v1/jobs/jobs/{job_id}/
Authorization: Bearer <access_token>
```

### Create Job (HR Only)
```http
POST /v1/jobs/jobs/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "New Job Position",
  "department": "uuid",
  "description": "Job description",
  "requirements": "Job requirements",
  "responsibilities": "Job responsibilities",
  "employment_type": "full_time",
  "experience_level": "mid",
  "work_model": "remote",
  "location": "Remote",
  "salary_min": 80000.00,
  "salary_max": 120000.00,
  "salary_currency": "USD",
  "min_experience_years": 3,
  "education_required": "Bachelor's degree",
  "application_deadline": "2024-12-31T23:59:59Z",
  "required_skills": ["Python", "React"],
  "preferred_skills": ["AWS", "Docker"]
}
```

### Update Job (HR Only)
```http
PATCH /v1/jobs/jobs/{job_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Job Title",
  "status": "published"
}
```

## Job Applications

### Apply for Job
```http
POST /v1/jobs/applications/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "job": "job_uuid",
  "cover_letter": "Cover letter text",
  "resume": <file>,
  "portfolio_url": "https://github.com/username"
}
```

### List Applications (HR/Candidate)
```http
GET /v1/jobs/applications/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `job`: Job ID filter
- `status`: Application status filter
- `candidate`: Candidate ID filter

### Get Application Details
```http
GET /v1/jobs/applications/{application_id}/
Authorization: Bearer <access_token>
```

### Update Application Status (HR Only)
```http
PATCH /v1/jobs/applications/{application_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "interview_scheduled",
  "internal_notes": "Strong candidate, schedule interview",
  "interview_feedback": "Excellent technical skills",
  "technical_score": 85.5,
  "cultural_fit_score": 90.0
}
```

## AI Chatbot Screening

### Start Chatbot Session
```http
POST /v1/chatbot/sessions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "application_id": "application_uuid"
}
```

### Send Message
```http
POST /v1/chatbot/sessions/{session_id}/messages/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "User response to question"
}
```

### Get Session History
```http
GET /v1/chatbot/sessions/{session_id}/messages/
Authorization: Bearer <access_token>
```

### Complete Screening
```http
POST /v1/chatbot/sessions/{session_id}/complete/
Authorization: Bearer <access_token>
```

## Interview Management

### Schedule Interview
```http
POST /v1/interviews/interviews/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "application_id": "application_uuid",
  "interviewer_id": "interviewer_uuid",
  "scheduled_at": "2024-01-15T14:00:00Z",
  "duration_minutes": 60,
  "interview_type": "technical",
  "meeting_link": "https://meet.google.com/abc-defg-hij",
  "notes": "Technical interview focusing on Python and React"
}
```

### List Interviews
```http
GET /v1/interviews/interviews/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `application`: Application ID filter
- `interviewer`: Interviewer ID filter
- `status`: Interview status filter
- `date_from`: Start date filter
- `date_to`: End date filter

### Update Interview
```http
PATCH /v1/interviews/interviews/{interview_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "completed",
  "feedback": "Excellent candidate, recommend hiring",
  "technical_score": 88.0,
  "cultural_fit_score": 92.0
}
```

## Offer Management

### Create Offer
```http
POST /v1/offers/offers/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "application_id": "application_uuid",
  "salary": 120000.00,
  "currency": "USD",
  "start_date": "2024-02-01",
  "offer_letter": <file>,
  "notes": "Welcome to the team!"
}
```

### List Offers
```http
GET /v1/offers/offers/
Authorization: Bearer <access_token>
```

### Accept/Reject Offer
```http
PATCH /v1/offers/offers/{offer_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "accepted",
  "response_notes": "Excited to join the team!"
}
```

## Analytics

### Dashboard Analytics (HR Only)
```http
GET /v1/analytics/dashboard/
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "total_applications": 150,
  "applications_this_month": 25,
  "interviews_scheduled": 45,
  "offers_sent": 12,
  "hires": 8,
  "conversion_rate": 5.33,
  "average_time_to_hire": 15.5,
  "department_stats": [
    {
      "department": "Engineering",
      "applications": 80,
      "hires": 5
    }
  ],
  "monthly_trends": [
    {
      "month": "2024-01",
      "applications": 25,
      "interviews": 15,
      "hires": 3
    }
  ]
}
```

### Application Analytics
```http
GET /v1/analytics/applications/
Authorization: Bearer <access_token>
```

### Interview Analytics
```http
GET /v1/analytics/interviews/
Authorization: Bearer <access_token>
```

## Notifications

### List Notifications
```http
GET /v1/notifications/notifications/
Authorization: Bearer <access_token>
```

### Mark as Read
```http
PATCH /v1/notifications/notifications/{notification_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_read": true
}
```

## Error Responses

### Validation Error
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### Authentication Error
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Error
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found Error
```json
{
  "detail": "Not found."
}
```

## Rate Limiting

The API implements rate limiting:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number
- `page_size`: Items per page (default: 20, max: 100)

Response includes:
- `count`: Total number of items
- `next`: URL for next page
- `previous`: URL for previous page
- `results`: Array of items

## File Upload

File uploads are supported for:
- Resumes (PDF, DOC, DOCX)
- Profile pictures (JPG, PNG)
- Offer letters (PDF)
- Application answers (various formats)

Maximum file size: 10MB

## Webhooks

The platform supports webhooks for real-time notifications:

### Configure Webhook
```http
POST /v1/webhooks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["application.created", "interview.scheduled"],
  "secret": "webhook_secret"
}
```

### Webhook Events
- `application.created`: New job application
- `application.status_changed`: Application status updated
- `interview.scheduled`: Interview scheduled
- `interview.completed`: Interview completed
- `offer.sent`: Offer letter sent
- `offer.accepted`: Offer accepted
- `offer.rejected`: Offer rejected

## SDKs and Libraries

### Python SDK
```python
from interview_platform import InterviewPlatform

client = InterviewPlatform(
    api_key="your_api_key",
    base_url="http://localhost:8000/api"
)

# Create job application
application = client.applications.create(
    job_id="job_uuid",
    cover_letter="Cover letter",
    resume="path/to/resume.pdf"
)
```

### JavaScript SDK
```javascript
import { InterviewPlatform } from '@interview-platform/sdk';

const client = new InterviewPlatform({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000/api'
});

// Create job application
const application = await client.applications.create({
  jobId: 'job_uuid',
  coverLetter: 'Cover letter',
  resume: file
});
```

## Testing

### Test Credentials
```
Admin: admin@company.com / admin123
HR: hr@company.com / hr123
Interviewer: interviewer@company.com / interviewer123
Candidate: candidate@example.com / candidate123
```

### Postman Collection
Download the complete Postman collection: [Interview Platform API.postman_collection.json](https://github.com/your-repo/postman-collection)

## Support

For API support:
- Email: api-support@company.com
- Documentation: http://localhost:8000/api/docs/
- Issues: https://github.com/your-repo/issues