from django.urls import path
from .views import CourseListCreateView, CourseDetailUpdateView, EnrollmentListCreateView

urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course_list_create'),
    path('<int:pk>/', CourseDetailUpdateView.as_view(), name='course_detail_update'),

    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment_list_create'),    
]
