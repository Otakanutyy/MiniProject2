from rest_framework.permissions import BasePermission

class IsInstructorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'teacher' and obj.course.instructor == request.user:
            return True
        return False

    def has_permission(self, request, view):
        return request.user.role in ['admin', 'teacher']
