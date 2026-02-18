from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, F
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Article, Podcast, Video
from .serializers import (
    CategorySerializer, ArticleListSerializer, ArticleDetailSerializer,
    ArticleCreateUpdateSerializer, ArticleSchemaSerializer,
    PodcastSerializer, PodcastCreateUpdateSerializer,
    VideoSerializer, VideoCreateUpdateSerializer
)
from .filters import ArticleFilter
from .permissions import IsEditorOrReadOnly
from apps.users.models import ArticleView


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories."""
    
    queryset = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='PUBLISHED'))
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for articles with full CRUD and search."""
    
    queryset = Article.objects.select_related('category', 'author').prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ArticleFilter
    ordering_fields = ['published_at', 'view_count', 'created_at']
    ordering = ['-published_at']
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]
    
    def get_queryset(self):
        """Filter published articles for non-staff users."""
        qs = super().get_queryset()
        
        # Non-staff can only see published articles
        if not self.request.user.is_staff:
            qs = qs.filter(status='PUBLISHED')
        
        return qs
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer
    
    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve article and track view."""
        instance = self.get_object()
        
        # Increment view count
        instance.increment_view_count()
        
        # Track user view for personalization
        if request.user.is_authenticated:
            ArticleView.objects.create(
                user=request.user,
                article=instance
            )
            
            # Update last activity
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, slug=None):
        """Increment article view count without returning full article data."""
        article = self.get_object()
        
        # Increment view count atomically
        article.increment_view_count()
        
        # Refresh from database to get updated count
        article.refresh_from_db()
        
        # Track user view for personalization (if authenticated)
        # Use update_or_create to avoid duplicate key constraint violations
        if request.user.is_authenticated:
            ArticleView.objects.update_or_create(
                user=request.user,
                article=article,
                defaults={'viewed_at': timezone.now()}
            )
        
        return Response({
            'view_count': article.view_count,
            'slug': article.slug
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def schema(self, request, slug=None):
        """Return JSON-LD schema for the article."""
        article = self.get_object()
        serializer = ArticleSchemaSerializer(article)
        data = serializer.data
        
        # Build JSON-LD schema
        schema = {
            "@context": "https://schema.org",
            "@type": data['schema_type'],
            "headline": data['title'],
            "description": data['summary'],
            "datePublished": data['published_at'],
            "dateModified": data['updated_at'],
            "author": {
                "@type": "Person",
                "name": data['author_name']
            }
        }
        
        if data['hero_image']:
            schema['image'] = request.build_absolute_uri(data['hero_image'])
        
        return Response(schema)


class PodcastViewSet(viewsets.ModelViewSet):
    """ViewSet for podcasts."""
    
    queryset = Podcast.objects.select_related('author').prefetch_related('tags', 'related_articles')
    serializer_class = PodcastSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_featured', 'episode_number']
    search_fields = ['title', 'description', 'transcript']
    ordering_fields = ['published_at', 'episode_number']
    ordering = ['-published_at']
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return PodcastCreateUpdateSerializer
        return PodcastSerializer
    
    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, slug=None):
        """Increment podcast view count."""
        podcast = self.get_object()
        
        # Increment view count atomically using F expression
        Podcast.objects.filter(pk=podcast.pk).update(
            view_count=F('view_count') + 1
        )
        
        # Refresh from database to get updated count
        podcast.refresh_from_db()
        
        return Response({
            'view_count': podcast.view_count,
            'slug': podcast.slug
        }, status=status.HTTP_200_OK)


class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for videos."""
    
    queryset = Video.objects.select_related('author').prefetch_related('tags', 'related_articles')
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['published_at']
    ordering = ['-published_at']
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return VideoCreateUpdateSerializer
        return VideoSerializer
    
    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, slug=None):
        """Increment video view count."""
        video = self.get_object()
        
        # Increment view count atomically using F expression
        Video.objects.filter(pk=video.pk).update(
            view_count=F('view_count') + 1
        )
        
        # Refresh from database to get updated count
        video.refresh_from_db()
        
        return Response({
            'view_count': video.view_count,
            'slug': video.slug
        }, status=status.HTTP_200_OK)


class SearchViewSet(viewsets.ViewSet):
    """Full-text search across articles."""
    
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """Search articles by query parameter."""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'results': []})
        
        # SQLite-compatible search using Q objects and icontains
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(body__icontains=query) |
            Q(tags__name__icontains=query),
            status='PUBLISHED'
        ).distinct().select_related(
            'category', 'author'
        ).order_by('-published_at')[:20]
        
        serializer = ArticleListSerializer(results, many=True, context={'request': request})
        
        return Response({
            'query': query,
            'count': len(results),
            'results': serializer.data
        })


class RecommendationViewSet(viewsets.ViewSet):
    """Personalized recommendations based on user reading history."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get personalized article recommendations."""
        user = request.user
        
        # Check if profile should be reset
        if user.should_reset_profile():
            user.reading_profile_json = {}
            user.last_activity = timezone.now()
            user.save()
            
            return Response({
                'message': 'Your reading profile has been reset due to inactivity.',
                'recommendations': []
            })
        
        # Get user's viewed articles
        viewed_article_ids = ArticleView.objects.filter(
            user=user
        ).values_list('article_id', flat=True)
        
        if not viewed_article_ids:
            # Return editor picks for new users
            articles = Article.objects.filter(
                status='PUBLISHED',
                is_editor_pick=True
            ).select_related('category', 'author')[:10]
        else:
            # Get tags from viewed articles
            viewed_articles = Article.objects.filter(
                id__in=viewed_article_ids
            ).prefetch_related('tags')
            
            tag_names = set()
            for article in viewed_articles:
                tag_names.update(article.tags.names())
            
            # Find articles with similar tags
            if tag_names:
                articles = Article.objects.filter(
                    status='PUBLISHED',
                    tags__name__in=tag_names
                ).exclude(
                    id__in=viewed_article_ids
                ).distinct().select_related(
                    'category', 'author'
                ).annotate(
                    tag_match_count=Count('tags', filter=Q(tags__name__in=tag_names))
                ).order_by('-tag_match_count', '-published_at')[:10]
            else:
                # Fallback to recent articles
                articles = Article.objects.filter(
                    status='PUBLISHED'
                ).exclude(
                    id__in=viewed_article_ids
                ).select_related('category', 'author').order_by('-published_at')[:10]
        
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        
        return Response({
            'recommendations': serializer.data,
            'based_on': len(viewed_article_ids),
        })
