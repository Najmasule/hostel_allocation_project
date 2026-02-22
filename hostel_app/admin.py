from django.contrib import admin
from .models import CustomUser, Hostel, Allocation, ActivityLog

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "role", "is_staff")
    search_fields = ("username", "first_name", "email")


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "total_rooms")
    search_fields = ("name", "location")


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ("student", "hostel", "room_number", "allocated_on")
    search_fields = ("student__username", "hostel__name", "room_number")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "details", "created_at")
    search_fields = ("user__username", "action", "details")
