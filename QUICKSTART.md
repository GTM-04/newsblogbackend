# Quick Start Guide

## Prerequisites Setup

### 1. Install PostgreSQL

**Windows:**

- Download from <https://www.postgresql.org/download/windows/>
- During installation, remember your password for the `postgres` user
- Default port: 5432

**macOS:**

```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Access PostgreSQL shell
psql -U postgres

# Create database
CREATE DATABASE pulse_passion;

# Create user (optional)
CREATE USER pulse_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pulse_passion TO pulse_user;

# Exit
\q
```

### 3. Install Redis (Optional - for Celery)

**Windows:**

- Download from <https://github.com/microsoftarchive/redis/releases>
- Install and start the service

**macOS:**

```bash
brew install redis
brew services start redis
```

**Linux:**

```bash
sudo apt install redis-server
sudo systemctl start redis
```

## Quick Setup

### Option 1: Automated Setup (Recommended)

**Windows:**

```bash
setup.bat
```

**macOS/Linux:**

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create virtual environment:**

```bash
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

1. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your settings
```

1. **Run migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

1. **Create superuser:**

```bash
python manage.py createsuperuser
```

1. **Run server:**

```bash
python manage.py runserver
```

## Test the Setup

1. **Access API:** <http://localhost:8000/api/>
2. **Access Admin:** <http://localhost:8000/admin/>
3. **Get JWT Token:**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'
```

## Sample Data (Optional)

Load sample data for testing:

```bash
python manage.py shell
```

```python
from apps.users.models import User
from apps.content.models import Category, Article
from django.utils import timezone

# Create category
cat = Category.objects.create(name='Technology', slug='technology')

# Create editor
editor = User.objects.create_user(
    email='editor@test.com',
    password='test123',
    first_name='Jane',
    last_name='Editor',
    is_editor=True
)

# Create article
article = Article.objects.create(
    title='Welcome to Pulse & Passion',
    slug='welcome-pulse-passion',
    summary='Your trusted source for news, research, and essays.',
    body='This is the full article content...',
    category=cat,
    author=editor,
    content_type='NEWS',
    status='PUBLISHED',
    is_editor_pick=True,
    published_at=timezone.now(),
    sources_count=5,
    confidence_rating='HIGH'
)

print("Sample data created!")
```

## Common Issues

### Database Connection Error

- Ensure PostgreSQL is running
- Check credentials in `.env`
- Verify database exists: `psql -U postgres -l`

### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001
```

### Migration Errors

```bash
# Reset migrations (development only!)
python manage.py migrate --fake content zero
python manage.py migrate --fake users zero
python manage.py showmigrations
```

## Development Workflow

1. **Always activate virtual environment first**
2. **Pull latest changes:** `git pull`
3. **Install new dependencies:** `pip install -r requirements.txt`
4. **Run migrations:** `python manage.py migrate`
5. **Run tests:** `pytest`
6. **Start coding!**

## API Testing with Postman/Insomnia

Import this endpoint collection:

**Base URL:** `http://localhost:8000`

**Auth Flow:**

1. POST `/api/auth/login/` with email/password
2. Get `access` token from response
3. Add header: `Authorization: Bearer {access_token}`
4. Make authenticated requests

**Sample Requests:**

- GET `/api/articles/`
- GET `/api/articles/welcome-pulse-passion/`
- GET `/api/search/?q=technology`
- GET `/api/recommendations/` (requires auth)
- POST `/api/articles/` (requires editor auth)

## Need Help?

Check the main README.md for detailed documentation.
