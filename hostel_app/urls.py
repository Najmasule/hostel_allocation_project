from django.urls import path
from . import views

urlpatterns = [
    path('api/session/', views.session_api, name='session_api'),
    path('api/register/', views.register_api, name='register_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
    path('api/hostels/', views.hostels_api, name='hostels_api'),
    path('api/status/', views.allocation_status_api, name='allocation_status_api'),
    path('api/allocate/', views.allocate_hostel, name='allocate_api'),
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('api/admin/dashboard/', views.admin_dashboard_api, name='admin_dashboard_api'),
    path('api/export/allocations.csv', views.export_allocations_csv, name='export_allocations_csv'),
    path('', views.spa_page, name='spa_root'),
    path('register/', views.spa_page, name='register_page'),
    path('dashboard/', views.spa_page, name='dashboard_page'),
    path('home/', views.spa_page, name='home'),
    path('hostels/', views.spa_page, name='view_hostel'),
    path('apply/', views.spa_page, name='apply_hostel'),
    path('status/', views.spa_page, name='allocation_status'),
    path('settings/', views.spa_page, name='settings_page'),
    path('logout/', views.spa_page, name='logout'),
]

