from django import forms
from .models import Hostel, Student

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name', 'capacity', 'location']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'registration_number']
