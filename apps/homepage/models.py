"""
Homepage curation models for BBC-style layout.
"""
from django.db import models
from apps.content.models import Article, Podcast, Video


class HomepageSection(models.Model):
    """Homepage section for curated content layout."""
    
    SECTION_TYPE_CHOICES = [
        ('HERO', 'Hero Section (Top 3)'),
        ('COLLAGE', 'Image Collage'),
        ('RESEARCH_STRIP', 'Research Strip'),
        ('REFLECTIONS', 'Reflections/Essays'),
        ('QNA', 'Q&A Section'),
        ('FEATURED_MEDIA', 'Featured Podcasts/Videos'),
    ]
    
    section_type = models.CharField(
        max_length=30,
        choices=SECTION_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(
        max_length=200,
        help_text='Section heading (e.g., "Editor\'s Picks", "Deep Dive")'
    )
    subtitle = models.CharField(max_length=300, blank=True)
    
    position = models.PositiveIntegerField(
        default=0,
        help_text='Order on homepage (lower = higher)'
    )
    
    # Content relationships
    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='homepage_sections'
    )
    podcasts = models.ManyToManyField(
        Podcast,
        blank=True,
        related_name='homepage_sections'
    )
    videos = models.ManyToManyField(
        Video,
        blank=True,
        related_name='homepage_sections'
    )
    
    manually_curated = models.BooleanField(
        default=True,
        help_text='If False, content will be auto-populated based on rules'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Show this section on homepage'
    )
    
    # Auto-population rules (if not manually curated)
    auto_content_type = models.CharField(
        max_length=20,
        choices=[
            ('RECENT', 'Most Recent'),
            ('POPULAR', 'Most Viewed'),
            ('EDITOR_PICKS', 'Editor Picks'),
        ],
        blank=True
    )
    auto_article_count = models.PositiveIntegerField(
        default=5,
        help_text='Number of articles to auto-populate'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Homepage Section'
        verbose_name_plural = 'Homepage Sections'
        ordering = ['position']
        indexes = [
            models.Index(fields=['position', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.get_section_type_display()} - {self.title}'
    
    def get_content(self):
        """Get all content for this section."""
        content = {
            'articles': list(self.articles.filter(status='PUBLISHED').select_related('category', 'author')),
            'podcasts': list(self.podcasts.all()),
            'videos': list(self.videos.all()),
        }
        
        # Auto-populate if not manually curated
        if not self.manually_curated and self.auto_content_type:
            if self.auto_content_type == 'RECENT':
                content['articles'] = list(
                    Article.objects.filter(status='PUBLISHED')
                    .select_related('category', 'author')
                    .order_by('-published_at')[:self.auto_article_count]
                )
            elif self.auto_content_type == 'POPULAR':
                content['articles'] = list(
                    Article.objects.filter(status='PUBLISHED')
                    .select_related('category', 'author')
                    .order_by('-view_count')[:self.auto_article_count]
                )
            elif self.auto_content_type == 'EDITOR_PICKS':
                content['articles'] = list(
                    Article.objects.filter(status='PUBLISHED', is_editor_pick=True)
                    .select_related('category', 'author')
                    .order_by('-published_at')[:self.auto_article_count]
                )
        
        return content
