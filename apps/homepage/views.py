from rest_framework import viewsets, permissions
from .models import HomepageSection
from .serializers import HomepageSectionSerializer


class HomepageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for homepage sections."""
    
    queryset = HomepageSection.objects.filter(
        is_active=True
    ).prefetch_related(
        'articles__category',
        'articles__author',
        'articles__tags',
        'podcasts__author',
        'podcasts__tags',
        'videos__author',
        'videos__tags'
    ).order_by('position')
    
    serializer_class = HomepageSectionSerializer
    permission_classes = [permissions.AllowAny]
