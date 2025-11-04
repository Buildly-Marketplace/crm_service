# ForgeCRM Setup Guide

## Quick Start

ForgeCRM is a Django-based CRM microservice with PostgreSQL backend. Get it running in under 5 minutes.

## Prerequisites

- **Docker & Docker Compose** (recommended)
- **OR** Python 3.11+ with PostgreSQL 13+ (manual setup)

## Docker Setup (Recommended)

### 1. Clone and Start

```bash
git clone https://github.com/buildly-marketplace/crm_service.git
cd crm_service
docker-compose up -d
```

### 2. Verify Installation

```bash
# Check service health
curl http://localhost:8003/health/

# Check API (requires auth token - see below)
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8003/accounts/
```

### 3. Get Authentication Token

```bash
# Create admin user and get token
docker-compose exec crm_service python manage.py shell -c "
from django.contrib.auth.models import User; 
from rest_framework.authtoken.models import Token; 
user = User.objects.get(username='admin'); 
token, created = Token.objects.get_or_create(user=user); 
print('Token:', token.key)"
```

### 4. Load Sample Data (Optional)

```bash
docker-compose exec crm_service python manage.py loadinitialdata
```

## Manual Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb crm_service
```

### 2. Environment Configuration

Create `.env` file:

```env
# Database Configuration
DATABASE_ENGINE=postgresql
DATABASE_NAME=crm_service
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django Configuration
DJANGO_SETTINGS_MODULE=crm_service.settings.development
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: JWT Configuration
JWT_AUTH_DISABLED=True
JWT_ALLOWED_ISSUER=buildly
```

### 3. Database Setup

```bash
# Create database extensions
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost', port='5432',
    user='your_db_user', password='your_db_password',
    database='crm_service'
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE EXTENSION IF NOT EXISTS hstore;')
cursor.close()
conn.close()
"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8080
```

## Environment Variables

### Required

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL host | `postgres_crm_service` |
| `DATABASE_NAME` | Database name | `crm_service` |
| `DATABASE_USER` | Database user | `root` |
| `DATABASE_PASSWORD` | Database password | `root` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PORT` | Database port | `5432` |
| `DEBUG` | Django debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `JWT_AUTH_DISABLED` | Disable JWT auth | `True` |

## API Authentication

ForgeCRM supports two authentication methods:

### 1. Token Authentication (Recommended)

```bash
# Get token via API
curl -X POST http://localhost:8003/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8003/accounts/
```

### 2. Session Authentication

```bash
# Login via admin interface
http://localhost:8003/admin/

# API calls will use session cookies
```

## Health Check

ForgeCRM provides a health endpoint for monitoring:

```bash
curl http://localhost:8003/health/
# Returns: {"status": "healthy", "database": "connected", "version": "1.0.0"}
```

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8004:8080"  # Change 8003 to 8004
```

**Database Connection Error:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres_crm_service

# Check logs
docker-compose logs postgres_crm_service
```

**Migration Issues:**
```bash
# Reset migrations (development only)
docker-compose exec crm_service python manage.py migrate crm zero
docker-compose exec crm_service python manage.py makemigrations crm
docker-compose exec crm_service python manage.py migrate
```

### Getting Help

- Check `devdocs/OPERATIONS.md` for deployment issues
- Review logs: `docker-compose logs crm_service`
- See `SUPPORT.md` for professional support options

## Next Steps

- Review API endpoints in `devdocs/REFERENCE.md`
- Deploy to production using `devdocs/OPERATIONS.md`
- Explore the admin interface at `http://localhost:8003/admin/`