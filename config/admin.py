from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.content.models import Article, Podcast, Video
from apps.users.models import User


class PulsePassionAdminSite(admin.AdminSite):
    """Custom admin site with dashboard."""
    
    site_header = 'Pulse & Passion Admin'
    site_title = 'Pulse & Passion Admin Portal'
    index_title = 'Content Management Dashboard'
    
    def index(self, request, extra_context=None):
        """Custom admin index with statistics."""
        extra_context = extra_context or {}
        
        # Get today's date range
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        
        # Content statistics
        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(status='PUBLISHED').count()
        draft_articles = Article.objects.filter(status='DRAFT').count()
        review_articles = Article.objects.filter(status='REVIEW').count()
        published_today = Article.objects.filter(
            published_at__gte=today_start
        ).count()
        
        # Media statistics
        total_podcasts = Podcast.objects.count()
        total_videos = Video.objects.count()
        
        # User statistics
        total_editors = User.objects.filter(is_editor=True).count()
        
        # Recent articles
        recent_articles = Article.objects.select_related(
            'category', 'author'
        ).order_by('-created_at')[:5]
        
        # Top viewed articles (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        top_articles = Article.objects.filter(
            published_at__gte=week_ago,
            status='PUBLISHED'
        ).order_by('-view_count')[:5]
        
        extra_context.update({
            'stats': {
                'total_articles': total_articles,
                'published_articles': published_articles,
                'draft_articles': draft_articles,
                'review_articles': review_articles,
                'published_today': published_today,
                'total_podcasts': total_podcasts,
                'total_videos': total_videos,
                'total_editors': total_editors,
            },
            'recent_articles': recent_articles,
            'top_articles': top_articles,
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = PulsePassionAdminSite(name='pulse_admin')
