from django.core.cache import cache
import logging
from .models import Student
from .serializers import StudentSerializer

logger = logging.getLogger("custom")

def invalidate_student_cache(student_id):
    cache_key = f"student_profile_{student_id}"
    cache.delete(cache_key)
    logger.info(f"Cache invalidated for student profile: {student_id}")

def refresh_student_cache(student_id):
    try:
        student = Student.objects.get(id=student_id)
        serializer = StudentSerializer(student)
        cache_key = f"student_profile_{student_id}"
        cache.set(cache_key, serializer.data, timeout=3600)
        logger.info(f"Cache refreshed for student profile: {student_id}")
    except Student.DoesNotExist:
        logger.warning(f"Student with ID {student_id} does not exist.")
        cache.delete(f"student_profile_{student_id}")
