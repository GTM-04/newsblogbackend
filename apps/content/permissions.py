from rest_framework import permissions


class IsEditorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow editors to create/edit content.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for editors
        return request.user.is_authenticated and (
            request.user.is_editor or request.user.is_admin or request.user.is_staff
        )
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admins can edit anything
        if request.user.is_admin or request.user.is_superuser:
            return True
        
        # Editors can only edit their own drafts/content
        if request.user.is_editor:
            # Can't delete published content
            if request.method == 'DELETE' and hasattr(obj, 'status'):
                return obj.status != 'PUBLISHED'
            
            # Can edit own content
            return obj.author == request.user
        
        return False
