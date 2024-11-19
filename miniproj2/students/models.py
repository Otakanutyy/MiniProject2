from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        Student.objects.create(
            user=instance,
            name=instance.username,  
            email=instance.email
        )
