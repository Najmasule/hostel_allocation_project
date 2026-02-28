from django.db import models
from django.contrib.auth.models import AbstractUser

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    total_rooms = models.IntegerField()

    def __str__(self):
        return self.name

# class Student(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True)
#     room_number = models.CharField(max_length=10)

class CustomUser(AbstractUser):
    role_choices = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=role_choices, default='student')
    adress = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

    

class Allocation(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    allocated_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Keep exactly one allocation per student by removing older rows first.
        if self.student_id:
            Allocation.objects.filter(student_id=self.student_id).exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        room = self.room_number or "N/A"
        return f"{self.student.username} - {self.hostel.name} - {room}"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("register", "Register"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("apply", "Apply Hostel"),
        ("allocate", "Allocate Hostel"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "unknown"
        return f"{username} - {self.action} - {self.created_at:%Y-%m-%d %H:%M}"
