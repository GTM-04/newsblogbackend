"""
Media library models for centralized media management.
"""
from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class MediaFile(models.Model):
    """Centralized media file storage."""
    
    MEDIA_TYPE_CHOICES = [
        ('IMAGE', 'Image'),
        ('AUDIO', 'Audio'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    file = models.FileField(upload_to='media_library/%Y/%m/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    
    file_size = models.PositiveBigIntegerField(
        help_text='File size in bytes'
    )
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Image-specific fields
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to='media_library/thumbnails/%Y/%m/',
        null=True,
        blank=True
    )
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_media'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Generate thumbnail for images."""
        if self.file:
            self.file_size = self.file.size
            
            # Generate thumbnail for images
            if self.media_type == 'IMAGE' and self.file:
                try:
                    img = Image.open(self.file)
                    self.width, self.height = img.size
                    
                    # Create thumbnail
                    if not self.thumbnail:
                        thumb = img.copy()
                        thumb.thumbnail((300, 300), Image.LANCZOS)
                        
                        thumb_io = BytesIO()
                        thumb.save(thumb_io, format='JPEG', quality=85)
                        thumb_io.seek(0)
                        
                        self.thumbnail = InMemoryUploadedFile(
                            thumb_io,
                            None,
                            f'thumb_{self.file.name}',
                            'image/jpeg',
                            sys.getsizeof(thumb_io),
                            None
                        )
                except Exception:
                    pass  # Skip thumbnail generation if error
        
        super().save(*args, **kwargs)
