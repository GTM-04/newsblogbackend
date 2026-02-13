from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ArticleView


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin."""
    
    list_display = ['email', 'first_name', 'last_name', 'is_editor', 'is_admin', 'is_staff', 'date_joined']
    list_filter = ['is_editor', 'is_admin', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_editor', 'is_admin', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_activity')}),
        ('Personalization', {'fields': ('reading_profile_json',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_editor', 'is_admin'),
        }),
    )


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    """Admin for article views."""
    
    list_display = ['user', 'article', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__email', 'article__title']
    date_hierarchy = 'viewed_at'
    readonly_fields = ['user', 'article', 'viewed_at']
    
    def has_add_permission(self, request):
        return False
