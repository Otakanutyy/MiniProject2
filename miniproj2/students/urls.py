from django.urls import path
from .views import StudentUpdateView, StudentProfileView, StudentListView

urlpatterns = [
    path('profile/update/<int:pk>/', StudentUpdateView.as_view(), name='student-update'),
    path('profile/<int:pk>/', StudentProfileView.as_view(), name='student-profile'),
    path('all_profiles/', StudentListView.as_view(), name='student-list'),
]
