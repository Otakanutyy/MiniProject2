from rest_framework.permissions import BasePermission

class CanManageEnrollments(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        # Teachers have access to enrollments for their courses
        if request.user.role == 'teacher' and obj.course.instructor == request.user:
            return True
        return False

from rest_framework.permissions import BasePermission

class CanManageCourses(BasePermission):
    def has_permission(self, request, view):
        # teache or admin
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        # Admins
        if request.user.role == 'admin':
            return True
        # Teacher is instructor
        if request.user.role == 'teacher' and obj.instructor == request.user:
            return True
        return False
