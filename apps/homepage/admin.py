from django.contrib import admin
from .models import HomepageSection


@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    """Admin for homepage sections."""
    
    list_display = [
        'title',
        'section_type',
        'position',
        'is_active',
        'manually_curated',
        'content_count',
        'updated_at'
    ]
    
    list_filter = [
        'section_type',
        'is_active',
        'manually_curated',
        'created_at'
    ]
    
    search_fields = ['title', 'subtitle']
    
    filter_horizontal = ['articles', 'podcasts', 'videos']
    
    list_editable = ['position', 'is_active']
    
    fieldsets = (
        ('Section Info', {
            'fields': (
                'section_type',
                'title',
                'subtitle',
                'position',
                'is_active'
            )
        }),
        ('Content', {
            'fields': (
                'manually_curated',
                'articles',
                'podcasts',
                'videos'
            )
        }),
        ('Auto-Population (if not manually curated)', {
            'fields': (
                'auto_content_type',
                'auto_article_count'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def content_count(self, obj):
        """Display total content items."""
        articles = obj.articles.count()
        podcasts = obj.podcasts.count()
        videos = obj.videos.count()
        total = articles + podcasts + videos
        return f'{total} items (A:{articles} P:{podcasts} V:{videos})'
    content_count.short_description = 'Content'
    
    def get_queryset(self, request):
        """Optimize queries with prefetch."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('articles', 'podcasts', 'videos')
