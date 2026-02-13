from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category, Article, Podcast, Video


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for categories."""
    
    list_display = ['name', 'slug', 'parent', 'article_count', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


class RelatedArticleInline(admin.TabularInline):
    """Inline for related articles."""
    model = Article.related_podcasts.through
    extra = 1
    verbose_name = 'Related Article'
    verbose_name_plural = 'Related Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Customized admin for articles."""
    
    list_display = [
        'title', 
        'content_type', 
        'status', 
        'category',
        'author',
        'is_editor_pick',
        'is_paywalled',
        'confidence_rating',
        'view_count',
        'published_at'
    ]
    
    list_filter = [
        'status',
        'content_type',
        'category',
        'confidence_rating',
        'is_editor_pick',
        'is_paywalled',
        'published_at',
        'created_at'
    ]
    
    search_fields = ['title', 'subtitle', 'summary', 'body', 'author__email']
    
    prepopulated_fields = {'slug': ('title',)}
    
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'published_at']
    
    date_hierarchy = 'published_at'
    
    list_per_page = 50
    
    fieldsets = (
        ('Content', {
            'fields': (
                'title', 
                'slug', 
                'subtitle', 
                'summary', 
                'body', 
                'hero_image'
            )
        }),
        ('Classification', {
            'fields': (
                'content_type',
                'category',
                'tags',
                'author'
            )
        }),
        ('Publishing', {
            'fields': (
                'status',
                'is_editor_pick',
                'is_paywalled',
            )
        }),
        ('Trust & Transparency', {
            'fields': (
                'sources_count',
                'experts_interviewed',
                'confidence_rating',
                'what_we_dont_know'
            ),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
                'schema_type'
            ),
            'classes': ('collapse',)
        }),
        ('Analytics & Timestamps', {
            'fields': (
                'view_count',
                'published_at',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-assign author if not set."""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('category', 'author')
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete published articles."""
        if obj and obj.status == 'PUBLISHED' and not request.user.is_admin:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    """Admin for podcasts."""
    
    list_display = [
        'title',
        'episode_number',
        'author',
        'duration_display',
        'is_featured',
        'published_at'
    ]
    
    list_filter = ['is_featured', 'published_at', 'created_at']
    
    search_fields = ['title', 'description', 'transcript', 'author__email']
    
    prepopulated_fields = {'slug': ('title',)}
    
    readonly_fields = ['created_at', 'updated_at']
    
    date_hierarchy = 'published_at'
    
    filter_horizontal = ['related_articles']
    
    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title',
                'slug',
                'description',
                'episode_number',
                'author'
            )
        }),
        ('Media', {
            'fields': (
                'audio_file',
                'thumbnail',
                'duration_seconds',
            )
        }),
        ('Content', {
            'fields': (
                'transcript',
                'tags',
                'related_articles',
            )
        }),
        ('Publishing', {
            'fields': (
                'is_featured',
                'published_at',
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display duration in MM:SS format."""
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f'{minutes}:{seconds:02d}'
    duration_display.short_description = 'Duration'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign author if not set."""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin for videos."""
    
    list_display = [
        'title',
        'author',
        'duration_display',
        'video_type',
        'is_featured',
        'published_at'
    ]
    
    list_filter = ['is_featured', 'published_at', 'created_at']
    
    search_fields = ['title', 'description', 'author__email']
    
    prepopulated_fields = {'slug': ('title',)}
    
    readonly_fields = ['created_at', 'updated_at']
    
    date_hierarchy = 'published_at'
    
    filter_horizontal = ['related_articles']
    
    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title',
                'slug',
                'description',
                'author'
            )
        }),
        ('Media', {
            'fields': (
                'video_file',
                'external_url',
                'thumbnail',
                'duration_seconds',
            )
        }),
        ('Content', {
            'fields': (
                'tags',
                'related_articles',
            )
        }),
        ('Publishing', {
            'fields': (
                'is_featured',
                'published_at',
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display duration in MM:SS format."""
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f'{minutes}:{seconds:02d}'
    duration_display.short_description = 'Duration'
    
    def video_type(self, obj):
        """Display whether video is uploaded or external."""
        if obj.video_file:
            return format_html('<span style="color: green;">Uploaded</span>')
        return format_html('<span style="color: blue;">External</span>')
    video_type.short_description = 'Type'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign author if not set."""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)
