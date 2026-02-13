from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    """Admin for media files."""
    
    list_display = [
        'thumbnail_preview',
        'title',
        'media_type',
        'file_size_display',
        'dimensions_display',
        'uploaded_by',
        'created_at'
    ]
    
    list_filter = ['media_type', 'created_at']
    
    search_fields = ['title', 'description']
    
    readonly_fields = [
        'file_size',
        'mime_type',
        'width',
        'height',
        'uploaded_by',
        'created_at',
        'updated_at',
        'thumbnail_preview'
    ]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'media_type')
        }),
        ('File', {
            'fields': ('file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': (
                'file_size',
                'mime_type',
                'width',
                'height',
                'uploaded_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        """Display thumbnail preview."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.thumbnail.url
            )
        elif obj.media_type == 'IMAGE' and obj.file:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.file.url
            )
        return '-'
    thumbnail_preview.short_description = 'Preview'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
    file_size_display.short_description = 'Size'
    
    def dimensions_display(self, obj):
        """Display image dimensions."""
        if obj.width and obj.height:
            return f'{obj.width} × {obj.height}'
        return '-'
    dimensions_display.short_description = 'Dimensions'
    
    def save_model(self, request, obj, form, change):
        """Auto-assign uploaded_by."""
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
