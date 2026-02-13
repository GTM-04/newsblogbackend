import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestArticleAPI:
    """Test Article API endpoints."""
    
    def test_list_articles(self, api_client, published_article):
        """Test listing published articles."""
        url = reverse('article-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == published_article.title
    
    def test_retrieve_article(self, api_client, published_article):
        """Test retrieving a single article."""
        url = reverse('article-detail', kwargs={'slug': published_article.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == published_article.title
        assert 'body_content' in response.data
    
    def test_paywall_logic_unauthenticated(self, api_client, paywalled_article):
        """Test paywall returns limited content for unauthenticated users."""
        url = reverse('article-detail', kwargs={'slug': paywalled_article.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert '...' in response.data['body_content']  # Limited content
        assert len(response.data['body_content']) < len(paywalled_article.body)
    
    def test_paywall_logic_authenticated(self, api_client, user, paywalled_article):
        """Test paywall returns full content for authenticated users."""
        api_client.force_authenticate(user=user)
        url = reverse('article-detail', kwargs={'slug': paywalled_article.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['body_content'] == paywalled_article.body
    
    def test_create_article_unauthorized(self, api_client):
        """Test creating article without authentication fails."""
        url = reverse('article-list')
        data = {
            'title': 'New Article',
            'slug': 'new-article',
            'summary': 'Summary',
            'body': 'Body',
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_article_as_editor(self, api_client, editor_user, category):
        """Test creating article as editor."""
        api_client.force_authenticate(user=editor_user)
        url = reverse('article-list')
        data = {
            'title': 'New Article',
            'slug': 'new-article',
            'summary': 'Summary',
            'body': 'Body content',
            'category': category.id,
            'content_type': 'NEWS',
            'status': 'DRAFT',
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Article'
    
    def test_filter_by_category(self, api_client, published_article):
        """Test filtering articles by category."""
        url = reverse('article-list')
        response = api_client.get(url, {'category': published_article.category.slug})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_search_articles(self, api_client, published_article):
        """Test full-text search."""
        url = reverse('search-list')
        response = api_client.get(url, {'q': 'test'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data


@pytest.mark.django_db
class TestRecommendations:
    """Test recommendation system."""
    
    def test_recommendations_require_auth(self, api_client):
        """Test recommendations require authentication."""
        url = reverse('recommendations-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_recommendations_for_new_user(self, api_client, user, published_article):
        """Test recommendations for user with no history."""
        published_article.is_editor_pick = True
        published_article.save()
        
        api_client.force_authenticate(user=user)
        url = reverse('recommendations-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'recommendations' in response.data
