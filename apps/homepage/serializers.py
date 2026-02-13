from rest_framework import serializers
from .models import HomepageSection
from apps.content.serializers import ArticleListSerializer, PodcastSerializer, VideoSerializer


class HomepageSectionSerializer(serializers.ModelSerializer):
    """Serializer for homepage sections."""
    
    articles = ArticleListSerializer(many=True, read_only=True)
    podcasts = PodcastSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    content = serializers.SerializerMethodField()
    
    class Meta:
        model = HomepageSection
        fields = [
            'id', 'section_type', 'title', 'subtitle',
            'position', 'articles', 'podcasts', 'videos',
            'content', 'manually_curated'
        ]
    
    def get_content(self, obj):
        """Get dynamic content based on section rules."""
        content = obj.get_content()
        
        return {
            'articles': ArticleListSerializer(
                content['articles'],
                many=True,
                context=self.context
            ).data,
            'podcasts': PodcastSerializer(
                content['podcasts'],
                many=True,
                context=self.context
            ).data,
            'videos': VideoSerializer(
                content['videos'],
                many=True,
                context=self.context
            ).data,
        }
