"""
Custom User model for Pulse & Passion.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_editor', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as username."""
    
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(
        default=False,
        help_text='Can create and edit content'
    )
    is_admin = models.BooleanField(
        default=False,
        help_text='Has full admin access'
    )
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Personalization data
    reading_profile_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Stores user reading preferences and behavior'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name."""
        return f'{self.first_name} {self.last_name}'.strip() or self.email
    
    def get_short_name(self):
        """Return the short name."""
        return self.first_name or self.email
    
    def should_reset_profile(self):
        """Check if reading profile should be reset (30+ days inactive)."""
        if not self.last_activity:
            return False
        from datetime import timedelta
        return timezone.now() - self.last_activity > timedelta(days=30)


class ArticleView(models.Model):
    """Track article views for personalization."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='article_views'
    )
    article = models.ForeignKey(
        'content.Article',
        on_delete=models.CASCADE,
        related_name='user_views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Article View'
        verbose_name_plural = 'Article Views'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['article', '-viewed_at']),
        ]
    
    def __str__(self):
        return f'{self.user.email} viewed {self.article.title}'
