from django.db import models

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    occupied_rooms = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    room_number = models.CharField(max_length=10)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
