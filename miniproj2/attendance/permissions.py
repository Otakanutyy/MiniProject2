from rest_framework.permissions import BasePermission

class CanManageAttendance(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'teacher']

    def has_object_permission(self, request, view, obj):
        # Admin
        if request.user.role == 'admin':
            return True
        # Teacher is instructor
        if request.user.role == 'teacher' and obj.course.instructor == request.user:
            return True
        return False
