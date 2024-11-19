from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Student
from .serializers import StudentSerializer, GetStudentSerializer

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = GetStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentProfileView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = GetStudentSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_object(self):
        return super().get_object()

class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        student = super().get_object()

        # owner or admin can
        if self.request.user != student.user and self.request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to update this record.")
        
        return student
