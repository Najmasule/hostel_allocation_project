from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from .models import Hostel, Allocation
User = get_user_model()
from django.db.models import F
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json

# ==== PAGES ====
def register_page(request):
    # Handles both showing the registration page and form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username') or request.POST.get('email')    
        password = request.POST.get('password')
        password2 = request.POST.get('password2') or request.POST.get('confirm_password')
        role = request.POST.get('role', 'student')
        adress = request.POST.get('adress', '')
        phone_number = request.POST.get('phone_number', '')
        if not (name and username and password):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'hostel_app/register.html')
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'hostel_app/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already registered')
            return render(request, 'hostel_app/register.html')
        user = User.objects.create_user(username=username, email=username, password=password, first_name=name, role=role, adress=adress, phone_number=phone_number)
        auth_login(request, user)
        return redirect('dashboard_page')
    return render(request, 'hostel_app/register.html')

def login_page(request):
    # Handles both showing the login page and form submission
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not (username and password):
            messages.error(request, 'Please provide username and password')
            return render(request, 'hostel_app/login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # If the user is staff/superuser, send them to the Django admin
            if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
                return redirect('admin:index')
            return redirect('dashboard_page')
        messages.error(request, 'Invalid credentials')
        return render(request, 'hostel_app/login.html')
    return render(request, 'hostel_app/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login_page')

def dashboard_page(request):
    students = User.objects.filter(role='student')
    hostels = Hostel.objects.all()
    return render(request, 'hostel_app/dashboard.html', {"students": students, "hostels": hostels})


def home_page(request):
    return render(request, 'hostel_app/home.html')


def view_hostel_page(request):
    hostels = Hostel.objects.all()
    return render(request, 'hostel_app/view_hostel.html', {"hostels": hostels})


def apply_page(request):
    hostels = Hostel.objects.all()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login_page')
        hostel_id = request.POST.get('hostel_id')
        try:
            hostel = Hostel.objects.get(id=hostel_id)
        except (Hostel.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Selected hostel is invalid')
            return render(request, 'hostel_app/apply.html', {"hostels": hostels})

        # prevent re-applying if user already has an allocation
        existing = Allocation.objects.filter(student=request.user).first()
        if existing:
            messages.error(request, 'You already have a hostel assigned or an existing application.')
            return render(request, 'hostel_app/apply.html', {"hostels": hostels})

        # ensure hostel has available rooms
        if hostel.total_rooms is None or hostel.total_rooms <= 0:
            messages.error(request, 'Selected hostel has no available rooms.')
            return render(request, 'hostel_app/apply.html', {"hostels": hostels})

        # decrement total_rooms atomically to avoid race conditions
        updated = Hostel.objects.filter(id=hostel.id, total_rooms__gt=0).update(total_rooms=F('total_rooms') - 1)
        if not updated:
            messages.error(request, 'Failed to reserve a room — it may have just filled up.')
            return render(request, 'hostel_app/apply.html', {"hostels": hostels})

        # refresh hostel instance to reflect new count
        hostel.refresh_from_db()

        # create an allocation record for this user
        Allocation.objects.create(student=request.user, hostel=hostel, room_number='')
        messages.success(request, f'Applied to {hostel.name}.')
        return redirect('allocation_status')

    return render(request, 'hostel_app/apply.html', {"hostels": hostels})


def allocation_status_page(request):
    allocation = None
    if request.user.is_authenticated:
        allocation = Allocation.objects.filter(student=request.user).first()
    return render(request, 'hostel_app/status.html', {"allocation": allocation})


def settings_page(request):
    return render(request, 'hostel_app/settings.html')

@ensure_csrf_cookie
def spa_page(request):
    return render(request, 'index.html')


def _json_body(request):
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return None

# ==== API ====
@csrf_exempt
@require_POST
def register_api(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    name = data.get('name', '').strip()
    username = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password')
    password2 = data.get('password2')
    role = data.get('role', 'student')
    adress = data.get('adress', '').strip()
    phone_number = data.get('phone_number', '').strip()

    if not (name and username and password):
        return JsonResponse({"status": "error", "message": "Please fill all required fields"}, status=400)
    if password2 is not None and password != password2:
        return JsonResponse({"status": "error", "message": "Passwords do not match"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"status": "error", "message": "Username already registered"}, status=409)

    user = User.objects.create_user(
        username=username,
        email=username,
        password=password,
        first_name=name,
        role=role,
        adress=adress,
        phone_number=phone_number,
    )
    auth_login(request, user)
    return JsonResponse({"status": "success", "message": "Registered successfully"})

@csrf_exempt
@require_POST
def login_api(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    username = (data.get('username') or '').strip()
    password = data.get('password')
    if not (username and password):
        return JsonResponse({"status": "error", "message": "Username and password are required"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)

    auth_login(request, user)
    return JsonResponse(
        {
            "status": "success",
            "message": "Login success",
            "user": {"username": user.username, "name": user.first_name, "role": user.role},
        }
    )


@csrf_exempt
@require_POST
def logout_api(request):
    auth_logout(request)
    return JsonResponse({"status": "success", "message": "Logged out"})


@ensure_csrf_cookie
@require_GET
def session_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False})

    return JsonResponse(
        {
            "authenticated": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "name": request.user.first_name,
                "role": getattr(request.user, "role", "student"),
            },
        }
    )


@require_GET
def hostels_api(request):
    hostels = list(Hostel.objects.values("id", "name", "location", "total_rooms"))
    return JsonResponse({"status": "success", "hostels": hostels})


@require_GET
def allocation_status_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

    allocation = Allocation.objects.select_related("hostel").filter(student=request.user).first()
    if not allocation:
        return JsonResponse({"status": "success", "allocation": None})

    return JsonResponse(
        {
            "status": "success",
            "allocation": {
                "hostel_name": allocation.hostel.name,
                "room_number": allocation.room_number,
                "allocated_on": allocation.allocated_on.isoformat(),
            },
        }
    )


@csrf_exempt
@require_POST
def allocate_hostel(request):
    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    student_id = data.get('student_id')
    hostel_id = data.get('hostel_id')
    room_number = data.get('room_number') or ''

    if student_id:
        # Admin/staff can allocate any student from dashboard-like UI.
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)
        user = User.objects.filter(id=student_id).first()
        hostel = Hostel.objects.filter(id=hostel_id).first()
        if not user or not hostel:
            return JsonResponse({"status": "error", "message": "Invalid student or hostel"}, status=400)
        Allocation.objects.update_or_create(
            student=user,
            defaults={"hostel": hostel, "room_number": room_number},
        )
        return JsonResponse({"status": "success", "message": "Student allocated"})

    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Please login first"}, status=401)

    hostel = Hostel.objects.filter(id=hostel_id).first()
    if not hostel:
        return JsonResponse({"status": "error", "message": "Selected hostel is invalid"}, status=400)

    existing = Allocation.objects.filter(student=request.user).first()
    if existing:
        return JsonResponse(
            {"status": "error", "message": "You already have a hostel assigned or application."},
            status=409,
        )

    updated = Hostel.objects.filter(id=hostel.id, total_rooms__gt=0).update(total_rooms=F('total_rooms') - 1)
    if not updated:
        return JsonResponse({"status": "error", "message": "Selected hostel has no available rooms"}, status=409)

    hostel.refresh_from_db()
    Allocation.objects.create(student=request.user, hostel=hostel, room_number='')
    return JsonResponse({"status": "success", "message": f"Applied to {hostel.name}"})

@require_GET
def dashboard_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

    hostels = list(Hostel.objects.values("id", "name", "location", "total_rooms"))

    if request.user.is_staff or request.user.is_superuser or getattr(request.user, "role", "student") == "admin":
        allocations_qs = Allocation.objects.select_related("student", "hostel").order_by("-allocated_on")
    else:
        allocations_qs = Allocation.objects.select_related("student", "hostel").filter(student=request.user).order_by("-allocated_on")

    allocations = [
        {
            "id": allocation.id,
            "student": allocation.student.username,
            "hostel": allocation.hostel.name,
            "room_number": allocation.room_number,
            "allocated_on": allocation.allocated_on.isoformat(),
        }
        for allocation in allocations_qs
    ]

    return JsonResponse(
        {
            "status": "success",
            "user": {
                "username": request.user.username,
                "name": request.user.first_name,
                "role": getattr(request.user, "role", "student"),
            },
            "hostels": hostels,
            "allocations": allocations,
        }
    )
