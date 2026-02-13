# Pulse & Passion Backend

A professional Django backend for the **Pulse & Passion** news blog platform. Built with Django 5, Django REST Framework, and PostgreSQL.

## Features

- 📰 **Content Management**: Articles (News, Research, Essays), Podcasts, Videos
- 🏷️ **Categorization**: Hierarchical categories and taggable content
- 🔒 **Soft Paywall**: Authenticated users get full access
- 🎯 **Editorial Control**: Editor picks, trust metadata, confidence ratings
- 📊 **Homepage Curation**: BBC-style layout with multiple sections
- 🤖 **Personalization**: Basic collaborative filtering recommendations
- 🔍 **Full-Text Search**: PostgreSQL-powered search
- 🔐 **JWT Authentication**: Secure API access
- 📈 **Analytics**: View tracking and reading profiles
- 🎨 **Custom Admin**: Beautiful dashboard with statistics
- 🔧 **Media Library**: Centralized media management with thumbnails

## Tech Stack

- **Framework**: Django 5.1+ with Django REST Framework
- **Database**: PostgreSQL (with full-text search)
- **Authentication**: SimpleJWT
- **Storage**: Local or S3-compatible (configurable)
- **Tasks**: Celery + Redis (optional)
- **Image Processing**: Pillow

## Project Structure

```
pulse_backend/
├── manage.py
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   ├── admin.py           # Custom admin site
│   └── celery.py
├── apps/
│   ├── users/             # Custom user model
│   ├── content/           # Articles, podcasts, videos
│   ├── media_library/     # Media management
│   └── homepage/          # Homepage curation
├── templates/             # Custom admin templates
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis (optional, for Celery)

### Setup Steps

1. **Clone the repository**

```bash
cd pulse_backend
```

1. **Create and activate virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Set up environment variables**

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=pulse_passion
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Optional: S3 Storage
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Optional: Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

1. **Create PostgreSQL database**

```bash
# Using psql
psql -U postgres
CREATE DATABASE pulse_passion;
\q
```

1. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

1. **Create superuser**

```bash
python manage.py createsuperuser
```

1. **Run development server**

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

The admin portal will be available at `http://localhost:8000/admin/`

## API Endpoints

### Authentication

- `POST /api/auth/login/` - Obtain JWT token pair
- `POST /api/auth/refresh/` - Refresh access token

### Public Endpoints

- `GET /api/articles/` - List articles (filterable)
- `GET /api/articles/{slug}/` - Article detail
- `GET /api/articles/{slug}/schema/` - JSON-LD schema
- `GET /api/podcasts/` - List podcasts
- `GET /api/podcasts/{slug}/` - Podcast detail
- `GET /api/videos/` - List videos
- `GET /api/videos/{slug}/` - Video detail
- `GET /api/categories/` - List categories
- `GET /api/homepage/` - Homepage sections
- `GET /api/search/?q=query` - Full-text search

### Authenticated Endpoints

- `GET /api/recommendations/` - Personalized recommendations
- `GET /api/users/me/` - Current user profile
- `PATCH /api/users/update_profile/` - Update profile

### Editor Endpoints (Protected)

- `POST /api/articles/` - Create article
- `PUT/PATCH /api/articles/{slug}/` - Update article
- `DELETE /api/articles/{slug}/` - Delete article (drafts only)
- `POST /api/podcasts/` - Create podcast
- `POST /api/videos/` - Create video

## Filtering & Ordering

### Article Filters

- `?category=slug` - Filter by category
- `?tag=name` - Filter by tag
- `?content_type=NEWS|RESEARCH|ESSAY` - Filter by type
- `?status=PUBLISHED|DRAFT` - Filter by status (staff only)
- `?confidence_rating=HIGH|MEDIUM|LOW` - Filter by trust rating
- `?is_editor_pick=true` - Editor picks only
- `?is_paywalled=true` - Paywalled content

### Ordering

- `?ordering=-published_at` - Latest first
- `?ordering=view_count` - Most viewed
- `?ordering=-created_at` - Recently created

## Admin Portal

Access the customized admin portal at `/admin/`:

### Features

- **Dashboard**: Quick stats, recent articles, top viewed
- **Rich Filters**: Status, category, content type, confidence rating
- **Inline Editing**: Related articles for podcasts/videos
- **Auto-population**: Slug generation, meta fields
- **Permissions**: Editors can't delete published content
- **Search**: Full-text search across content
- **Date Hierarchy**: Navigate by publication date

### User Roles

- **Admin**: Full access, can delete published content
- **Editor**: Create/edit content, publish articles, no delete published
- **Regular User**: Read-only API access

## Personalization

The system tracks:

- Article views per user
- Tags interacted with
- Last activity timestamp

**Forget Mechanism**: Reading profiles reset after 30 days of inactivity.

**Recommendations**: Based on collaborative filtering using shared tags.

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# With coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/content/tests/
```

## Production Deployment

### Environment Setup

1. Set `DEBUG=False`
2. Configure proper `SECRET_KEY`
3. Set `ALLOWED_HOSTS` to your domain
4. Enable SSL (`SECURE_SSL_REDIRECT=True`)
5. Configure S3 storage if needed

### Static Files

```bash
python manage.py collectstatic --noinput
```

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Celery (Optional)

```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat (for scheduled tasks)
celery -A config beat -l info
```

## Security Features

- CSRF protection enabled
- CORS configurable
- Rate limiting on public API (100/hour anonymous, 1000/hour authenticated)
- File upload validation
- XSS protection
- Secure cookies in production
- HSTS headers in production

## Content Trust Metadata

Articles include transparency fields:

- `sources_count`: Number of sources cited
- `experts_interviewed`: Number of experts consulted
- `confidence_rating`: HIGH, MEDIUM, or LOW
- `what_we_dont_know`: Editorial transparency about limitations

## Database Indexes

Optimized indexes on:

- `Article.slug`, `Article.published_at`, `Article.status`
- `Category.slug`
- `User.email`
- Composite indexes for common query patterns

## API Response Example

### Article List

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Breaking: Climate Summit 2026",
      "slug": "breaking-climate-summit-2026",
      "subtitle": "World leaders gather to address climate crisis",
      "summary": "The 2026 Climate Summit brings together...",
      "hero_image": "/media/articles/heroes/2026/02/summit.jpg",
      "category": {
        "id": 2,
        "name": "Environment",
        "slug": "environment"
      },
      "tags": ["climate", "politics", "environment"],
      "author": {
        "id": 1,
        "email": "editor@pulsepassion.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "content_type": "NEWS",
      "status": "PUBLISHED",
      "is_editor_pick": true,
      "is_paywalled": false,
      "confidence_rating": "HIGH",
      "sources_count": 12,
      "experts_interviewed": 5,
      "view_count": 1523,
      "published_at": "2026-02-13T10:30:00Z",
      "created_at": "2026-02-13T08:00:00Z"
    }
  ]
}
```

## Contributing

This is a POC project. Follow Django/DRF best practices:

- Use migrations for schema changes
- Write tests for new features
- Follow PEP 8 style guide
- Document complex logic

## License

Proprietary - Pulse & Passion

## Support

For issues or questions, contact the development team.

---

Built with ❤️ using Django and Django REST Framework
