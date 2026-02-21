from django.contrib import admin
from .models import  CustomUser, Hostel, Allocation

admin.site.register(CustomUser)
admin.site.register(Hostel)
admin.site.register(Allocation)