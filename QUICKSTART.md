# Quick Start Guide - Task Manager PRO API

## Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Development Server

```bash
uvicorn task_manager_pro.api.main:app --reload
```

Server running at: http://localhost:8000

### 3. Access API Documentation

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## Common Tasks

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password_123"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

Save the `access_token` for authenticated requests.

### Create a Task

```bash
TOKEN="your_access_token_here"
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "due_date": "2025-12-31",
    "priority": "high"
  }'
```

### List Your Tasks

```bash
TOKEN="your_access_token_here"
curl -X GET "http://localhost:8000/api/tasks?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Get a Specific Task

```bash
TOKEN="your_access_token_here"
TASK_ID="task_id_here"
curl -X GET http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Mark Task as Completed

```bash
TOKEN="your_access_token_here"
TASK_ID="task_id_here"
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

### Delete a Task

```bash
TOKEN="your_access_token_here"
TASK_ID="task_id_here"
curl -X DELETE http://localhost:8000/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Get User Profile

```bash
TOKEN="your_access_token_here"
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Toggle Email Reminders

```bash
TOKEN="your_access_token_here"
curl -X POST http://localhost:8000/api/users/me/toggle-reminders \
  -H "Authorization: Bearer $TOKEN"
```

---

## Running Tests

### All Tests

```bash
pytest tests/
```

### Specific Test File

```bash
pytest tests/test_api.py
```

### Specific Test

```bash
pytest tests/test_api.py::test_create_task_authenticated
```

### With Coverage Report

```bash
pytest tests/ --cov=task_manager_pro
```

### Verbose Output

```bash
pytest tests/ -v -s
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite:///./tasks.db
# DATABASE_URL=postgresql://user:password@localhost/taskdb

# Security
SECRET_KEY=your-secret-key-change-in-production

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=0.5  # 30 minutes

# API
API_TITLE=Task Manager PRO
API_VERSION=0.3.0
DEBUG=False
```

---

## Docker Deployment

### Build Image

```bash
docker build -t task-manager-pro:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./tasks.db" \
  -e SECRET_KEY="your-secret-key" \
  task-manager-pro:latest
```

### With PostgreSQL

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@postgres:5432/taskdb" \
  -e SECRET_KEY="your-secret-key" \
  task-manager-pro:latest
```

---

## Troubleshooting

### "Address already in use" Error

```bash
# Change port
uvicorn task_manager_pro.api.main:app --reload --port 8001
```

### Database Connection Error

```bash
# Verify DATABASE_URL environment variable
echo $DATABASE_URL

# Reset database
rm -f tasks.db
python -c "from task_manager_pro.storage.database import init_db; init_db()"
```

### JWT Token Expired

```bash
# Get new token via login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_password"}'
```

### Tests Failing

```bash
# Ensure clean database
rm -f tasks.db

# Run with verbose output
pytest tests/ -v -s

# Check for errors
python -m pytest tests/ -x  # Stop on first failure
```

---

## Project Structure

```
task_manager_pro/
├── api/                 # REST API routes
├── storage/            # Database layer
├── schemas/            # Pydantic validation
├── models/             # Core domain models
├── services/           # Business logic
└── utils/              # Utilities (security, etc)

tests/                  # Test suite
docs/                   # Documentation
```

---

## Next Steps

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Review Documentation:** See `IMPLEMENTATION_SUMMARY.md`
3. **Run Tests:** Execute `pytest tests/`
4. **Create Features:** Follow Phase 5-6 roadmap

---

## Support

- **Full Documentation:** See `IMPLEMENTATION_SUMMARY.md`
- **API Details:** See `docs/PHASE3_REST_API.md`
- **Database Design:** See `docs/PHASE2_DATABASE_SECURITY.md`
- **Testing Guide:** See `docs/PHASE4_TESTING_CI_CD.md`

---

**Happy Task Managing! 🚀**
