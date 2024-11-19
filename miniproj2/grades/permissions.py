from rest_framework.permissions import BasePermission

class IsInstructorOrAdmin(BasePermission):
    """
    Allows teachers to manage grades for their courses and gives admins full access.
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        # Teachers have access to grades for their courses
        if request.user.role == 'teacher' and obj.course.instructor == request.user:
            return True
        return False

    def has_permission(self, request, view):
        # Only teachers and admins can access
        return request.user.role in ['admin', 'teacher']
