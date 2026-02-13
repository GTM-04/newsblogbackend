"""
Content models for Pulse & Passion.
Includes Articles, Podcasts, Videos, and Categories.
"""
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from taggit.managers import TaggableManager


class Category(models.Model):
    """Content category with hierarchical support."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f'{self.parent.name} > {self.name}'
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Core article model for news, research, and essays."""
    
    CONTENT_TYPE_CHOICES = [
        ('NEWS', 'News'),
        ('RESEARCH', 'Research'),
        ('ESSAY', 'Essay'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('REVIEW', 'In Review'),
        ('PUBLISHED', 'Published'),
    ]
    
    CONFIDENCE_RATING_CHOICES = [
        ('HIGH', 'High Confidence'),
        ('MEDIUM', 'Medium Confidence'),
        ('LOW', 'Low Confidence'),
    ]
    
    SCHEMA_TYPE_CHOICES = [
        ('Article', 'Article'),
        ('NewsArticle', 'News Article'),
        ('FAQ', 'FAQ'),
        ('HowTo', 'How-To'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, db_index=True)
    subtitle = models.CharField(max_length=400, blank=True)
    summary = models.TextField(
        max_length=500,
        help_text='Brief summary for listing pages and SEO'
    )
    body = models.TextField(help_text='Main article content')
    
    # Media
    hero_image = models.ImageField(
        upload_to='articles/heroes/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles'
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='articles'
    )
    
    # Content type and status
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='NEWS',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True
    )
    
    # Editorial features
    is_editor_pick = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Featured on homepage'
    )
    is_paywalled = models.BooleanField(
        default=False,
        help_text='Requires authentication to read full content'
    )
    
    # Trust and transparency
    sources_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of sources cited'
    )
    experts_interviewed = models.PositiveIntegerField(
        default=0,
        help_text='Number of experts interviewed'
    )
    confidence_rating = models.CharField(
        max_length=20,
        choices=CONFIDENCE_RATING_CHOICES,
        default='MEDIUM'
    )
    what_we_dont_know = models.TextField(
        blank=True,
        help_text='Transparency about unknowns and limitations'
    )
    
    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    schema_type = models.CharField(
        max_length=20,
        choices=SCHEMA_TYPE_CHOICES,
        default='Article'
    )
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at', 'status']),
            models.Index(fields=['content_type', 'status']),
            models.Index(fields=['is_editor_pick', '-published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set published_at when status changes to PUBLISHED
        if self.status == 'PUBLISHED' and not self.published_at:
            self.published_at = timezone.now()
        
        # Auto-populate meta fields if empty
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description:
            self.meta_description = self.summary[:160]
        
        super().save(*args, **kwargs)
    
    def get_limited_body(self):
        """Return 30% of body for paywalled content."""
        if not self.is_paywalled:
            return self.body
        
        words = self.body.split()
        limit = int(len(words) * 0.3)
        return ' '.join(words[:limit]) + '...'
    
    def increment_view_count(self):
        """Increment view count atomically."""
        Article.objects.filter(pk=self.pk).update(
            view_count=models.F('view_count') + 1
        )


class Podcast(models.Model):
    """Podcast episode model."""
    
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, db_index=True)
    description = models.TextField()
    
    audio_file = models.FileField(
        upload_to='podcasts/%Y/%m/',
        help_text='MP3 or other audio format'
    )
    thumbnail = models.ImageField(
        upload_to='podcasts/thumbnails/%Y/%m/',
        null=True,
        blank=True
    )
    
    episode_number = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(
        help_text='Duration in seconds'
    )
    
    transcript = models.TextField(
        blank=True,
        help_text='Full transcript of the podcast'
    )
    
    # Relationships
    related_articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='related_podcasts'
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='podcasts'
    )
    
    is_featured = models.BooleanField(default=False, db_index=True)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Podcast'
        verbose_name_plural = 'Podcasts'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'is_featured']),
        ]
    
    def __str__(self):
        if self.episode_number:
            return f'Episode {self.episode_number}: {self.title}'
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description:
            self.meta_description = self.description[:160]
        super().save(*args, **kwargs)


class Video(models.Model):
    """Video content model."""
    
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, db_index=True)
    description = models.TextField()
    
    # Video can be uploaded or linked externally
    video_file = models.FileField(
        upload_to='videos/%Y/%m/',
        null=True,
        blank=True,
        help_text='Upload video file (MP4 recommended)'
    )
    external_url = models.URLField(
        blank=True,
        help_text='YouTube or Vimeo URL'
    )
    
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/%Y/%m/',
        null=True,
        blank=True
    )
    
    duration_seconds = models.PositiveIntegerField(
        help_text='Duration in seconds'
    )
    
    # Relationships
    related_articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name='related_videos'
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='videos'
    )
    
    is_featured = models.BooleanField(default=False, db_index=True)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'is_featured']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description:
            self.meta_description = self.description[:160]
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate that either video_file or external_url is provided."""
        from django.core.exceptions import ValidationError
        if not self.video_file and not self.external_url:
            raise ValidationError(
                'Either upload a video file or provide an external URL'
            )
