from django.urls import path
from .views import AttendanceViewSet, AttendanceWindowCreateView, AttendanceMarkView

urlpatterns = [
    # URL patterns for AttendanceViewSet
    path('', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance_list_create'),
    path('<int:pk>/', AttendanceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='attendance_detail'),

    # URL pattern for creating attendance window
    path('create_att_window/', AttendanceWindowCreateView.as_view(), name='attendance_window_create'),

    # URL pattern for marking attendance
    path('mark-attendance/', AttendanceMarkView.as_view(), name='attendance_mark'),
]
