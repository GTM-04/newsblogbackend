from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Category, Article, Podcast, Video
from apps.users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category."""
    
    article_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'article_count']


class ArticleListSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for article list view."""
    
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'subtitle', 'summary',
            'hero_image', 'category', 'tags', 'author',
            'content_type', 'status', 'is_editor_pick',
            'is_paywalled', 'confidence_rating',
            'sources_count', 'experts_interviewed',
            'view_count', 'published_at', 'created_at'
        ]
        read_only_fields = ['view_count', 'published_at', 'created_at']


class ArticleDetailSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for article detail view with paywall logic."""
    
    category = CategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    body_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'subtitle', 'summary',
            'body_content', 'hero_image', 'category', 'tags',
            'author', 'content_type', 'status',
            'is_editor_pick', 'is_paywalled',
            'sources_count', 'experts_interviewed',
            'confidence_rating', 'what_we_dont_know',
            'meta_title', 'meta_description', 'schema_type',
            'view_count', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['view_count', 'published_at', 'created_at', 'updated_at']
    
    def get_body_content(self, obj):
        """Return full or limited body based on paywall status."""
        request = self.context.get('request')
        
        # If not paywalled, return full body
        if not obj.is_paywalled:
            return obj.body
        
        # If authenticated, return full body
        if request and request.user.is_authenticated:
            return obj.body
        
        # Otherwise return limited content
        return obj.get_limited_body()


class ArticleCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for creating/updating articles (editors only)."""
    
    tags = TagListSerializerField()
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'subtitle', 'summary', 'body',
            'hero_image', 'category', 'tags', 'content_type',
            'status', 'is_editor_pick', 'is_paywalled',
            'sources_count', 'experts_interviewed',
            'confidence_rating', 'what_we_dont_know',
            'meta_title', 'meta_description', 'schema_type'
        ]
    
    def validate_status(self, value):
        """Validate status changes."""
        request = self.context.get('request')
        instance = self.instance
        
        # Only admins can publish
        if value == 'PUBLISHED' and not request.user.is_admin:
            if not request.user.is_editor:
                raise serializers.ValidationError(
                    'Only editors and admins can publish articles.'
                )
        
        return value


class ArticleSchemaSerializer(serializers.ModelSerializer):
    """Serializer for JSON-LD schema generation."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'title', 'summary', 'published_at', 'updated_at',
            'hero_image', 'author_name', 'schema_type'
        ]


class PodcastSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for Podcast."""
    
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    related_articles = ArticleListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Podcast
        fields = [
            'id', 'title', 'slug', 'description',
            'audio_file', 'thumbnail', 'episode_number',
            'duration_seconds', 'transcript', 'tags',
            'related_articles', 'author', 'is_featured',
            'meta_title', 'meta_description',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['published_at', 'created_at', 'updated_at']


class PodcastCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for creating/updating podcasts."""
    
    tags = TagListSerializerField()
    
    class Meta:
        model = Podcast
        fields = [
            'title', 'slug', 'description', 'audio_file',
            'thumbnail', 'episode_number', 'duration_seconds',
            'transcript', 'tags', 'related_articles',
            'is_featured', 'meta_title', 'meta_description'
        ]


class VideoSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for Video."""
    
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    related_articles = ArticleListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description',
            'video_file', 'external_url', 'thumbnail',
            'duration_seconds', 'tags', 'related_articles',
            'author', 'is_featured', 'meta_title',
            'meta_description', 'published_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['published_at', 'created_at', 'updated_at']


class VideoCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer for creating/updating videos."""
    
    tags = TagListSerializerField()
    
    class Meta:
        model = Video
        fields = [
            'title', 'slug', 'description', 'video_file',
            'external_url', 'thumbnail', 'duration_seconds',
            'tags', 'related_articles', 'is_featured',
            'meta_title', 'meta_description'
        ]
    
    def validate(self, data):
        """Validate that either video_file or external_url is provided."""
        if not data.get('video_file') and not data.get('external_url'):
            raise serializers.ValidationError(
                'Either video_file or external_url must be provided.'
            )
        return data
