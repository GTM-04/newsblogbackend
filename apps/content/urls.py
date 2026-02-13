from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ArticleViewSet, PodcastViewSet,
    VideoViewSet, SearchViewSet, RecommendationViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'podcasts', PodcastViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'search', SearchViewSet, basename='search')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')

urlpatterns = [
    path('', include(router.urls)),
]
