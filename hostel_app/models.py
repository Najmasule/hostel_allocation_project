from django.db import models
from django.contrib.auth.models import AbstractUser

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    total_rooms = models.IntegerField()

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

    

class Allocation(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    allocated_on = models.DateTimeField(auto_now_add=True)
