import pytest
from django.contrib.auth import get_user_model
from apps.content.models import Category, Article
from rest_framework.test import APIClient
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def api_client():
    """Return API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create regular user."""
    return User.objects.create_user(
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def editor_user():
    """Create editor user."""
    return User.objects.create_user(
        email='editor@test.com',
        password='testpass123',
        is_editor=True
    )


@pytest.fixture
def admin_user():
    """Create admin user."""
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        is_admin=True,
        is_staff=True
    )


@pytest.fixture
def category():
    """Create test category."""
    return Category.objects.create(
        name='Technology',
        slug='technology'
    )


@pytest.fixture
def published_article(editor_user, category):
    """Create published article."""
    return Article.objects.create(
        title='Test Article',
        slug='test-article',
        summary='Test summary',
        body='Test body content',
        category=category,
        author=editor_user,
        content_type='NEWS',
        status='PUBLISHED',
        published_at=timezone.now()
    )


@pytest.fixture
def paywalled_article(editor_user, category):
    """Create paywalled article."""
    return Article.objects.create(
        title='Premium Article',
        slug='premium-article',
        summary='Premium summary',
        body='This is premium content that requires authentication.',
        category=category,
        author=editor_user,
        content_type='RESEARCH',
        status='PUBLISHED',
        is_paywalled=True,
        published_at=timezone.now()
    )
