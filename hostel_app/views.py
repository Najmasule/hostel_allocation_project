from django.shortcuts import render
from .models import Student, Hostel

def home(request):
    hostels = Hostel.objects.all()
    students = Student.objects.all()
    return render(request, 'hostel_app/home.html', {
        'hostels': hostels,
        'students': students
    })
