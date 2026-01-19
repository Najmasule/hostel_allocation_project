from django.contrib import admin
from .models import Student, Hostel

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'room_number', 'hostel')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('hostel',)

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'capacity', 'occupied_rooms')
    search_fields = ('name',)
