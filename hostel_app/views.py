from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from .models import Hostel, Allocation, ActivityLog
User = get_user_model()
from django.db.models import F
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import IntegrityError, OperationalError
import json
import csv


def _is_admin_user(user):
    return bool(user and (user.is_staff or user.is_superuser or getattr(user, "role", "student") == "admin"))


def _effective_role(user):
    return "admin" if _is_admin_user(user) else "student"


def _next_room_number(hostel):
    numbers = (
        Allocation.objects.filter(hostel=hostel)
        .exclude(room_number__isnull=True)
        .exclude(room_number__exact='')
        .values_list("room_number", flat=True)
    )
    max_number = 0
    for value in numbers:
        raw = str(value).strip().upper()
        if raw.startswith("R"):
            raw = raw[1:]
        if raw.isdigit():
            max_number = max(max_number, int(raw))
    return f"R{max_number + 1:03d}"


def _log_activity(user, action, details=""):
    try:
        ActivityLog.objects.create(user=user, action=action, details=details[:255])
    except Exception:
        pass


def _latest_allocation_for_student(student):
    return (
        Allocation.objects.select_related("hostel")
        .filter(student=student)
        .order_by("-allocated_on", "-id")
        .first()
    )


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
            if _is_admin_user(user):
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
    try:
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
        _log_activity(user, "register", "Registered account via frontend")
        return JsonResponse({"status": "success", "message": "Registered successfully"})
    except (IntegrityError, OperationalError):
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Registration failed unexpectedly."}, status=400)

@csrf_exempt
@require_POST
def login_api(request):
    try:
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
        _log_activity(user, "login", "Logged in via frontend")
        return JsonResponse(
            {
                "status": "success",
                "message": "Login success",
                "user": {
                    "username": user.username,
                    "name": user.first_name,
                    "role": _effective_role(user),
                    "is_admin": _is_admin_user(user),
                },
            }
        )
    except OperationalError:
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Login failed unexpectedly."}, status=400)


@csrf_exempt
@require_POST
def logout_api(request):
    try:
        current_user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        auth_logout(request)
        _log_activity(current_user, "logout", "Logged out")
        return JsonResponse({"status": "success", "message": "Logged out"})
    except Exception:
        return JsonResponse({"status": "error", "message": "Logout failed unexpectedly."}, status=400)


@ensure_csrf_cookie
@require_GET
def session_api(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated": False})

        return JsonResponse(
            {
                "authenticated": True,
                "user": {
                "id": request.user.id,
                "username": request.user.username,
                "name": request.user.first_name,
                "role": _effective_role(request.user),
                "is_admin": _is_admin_user(request.user),
            },
        }
    )
    except Exception:
        return JsonResponse({"authenticated": False})


@require_GET
def hostels_api(request):
    try:
        hostels = list(Hostel.objects.values("id", "name", "location", "total_rooms"))
        return JsonResponse({"status": "success", "hostels": hostels})
    except OperationalError:
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Failed to load hostels."}, status=400)


@require_GET
def allocation_status_api(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

        allocation = _latest_allocation_for_student(request.user)
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
    except OperationalError:
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Failed to load allocation status."}, status=400)


@csrf_exempt
@require_POST
def allocate_hostel(request):
    try:
        data = _json_body(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        student_id = data.get('student_id')
        hostel_id = data.get('hostel_id')
        room_number = data.get('room_number') or ''

        if student_id:
            if not request.user.is_authenticated or not _is_admin_user(request.user):
                return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)
            user = User.objects.filter(id=student_id).first()
            hostel = Hostel.objects.filter(id=hostel_id).first()
            if not user or not hostel:
                return JsonResponse({"status": "error", "message": "Invalid student or hostel"}, status=400)
            resolved_room = (room_number or "").strip() or _next_room_number(hostel)
            existing_allocations = Allocation.objects.filter(student=user).order_by("-allocated_on", "-id")

            if existing_allocations.exists():
                primary = existing_allocations.first()
                primary.hostel = hostel
                primary.room_number = resolved_room
                primary.save(update_fields=["hostel", "room_number"])
                removed_count = existing_allocations.exclude(id=primary.id).count()
                if removed_count:
                    existing_allocations.exclude(id=primary.id).delete()
            else:
                primary = Allocation.objects.create(student=user, hostel=hostel, room_number=resolved_room)
                removed_count = 0

            _log_activity(
                request.user,
                "allocate",
                f"Allocated {user.username} to {hostel.name} ({resolved_room}) - removed {removed_count} old allocation(s)",
            )
            return JsonResponse({"status": "success", "message": "Student allocated"})

        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Please login first"}, status=401)

        hostel = Hostel.objects.filter(id=hostel_id).first()
        if not hostel:
            return JsonResponse({"status": "error", "message": "Selected hostel is invalid"}, status=400)

        existing = _latest_allocation_for_student(request.user)
        if existing:
            return JsonResponse(
                {"status": "error", "message": "You already have a hostel assigned or application."},
                status=409,
            )

        updated = Hostel.objects.filter(id=hostel.id, total_rooms__gt=0).update(total_rooms=F('total_rooms') - 1)
        if not updated:
            return JsonResponse({"status": "error", "message": "Selected hostel has no available rooms"}, status=409)

        hostel.refresh_from_db()
        resolved_room = _next_room_number(hostel)
        Allocation.objects.create(student=request.user, hostel=hostel, room_number=resolved_room)
        _log_activity(request.user, "apply", f"Applied for {hostel.name} ({resolved_room})")
        return JsonResponse(
            {
                "status": "success",
                "message": f"Applied to {hostel.name}",
                "room_number": resolved_room,
            }
        )
    except OperationalError:
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Failed to apply hostel request."}, status=400)

@require_GET
def dashboard_api(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

        hostels = list(Hostel.objects.values("id", "name", "location", "total_rooms"))

        if _is_admin_user(request.user):
            allocations_qs = Allocation.objects.select_related("student", "hostel").order_by("-allocated_on", "-id")
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
        else:
            latest_allocation = _latest_allocation_for_student(request.user)
            allocations = (
                [
                    {
                        "id": latest_allocation.id,
                        "student": latest_allocation.student.username,
                        "hostel": latest_allocation.hostel.name,
                        "room_number": latest_allocation.room_number,
                        "allocated_on": latest_allocation.allocated_on.isoformat(),
                    }
                ]
                if latest_allocation
                else []
            )

        return JsonResponse(
            {
                "status": "success",
                "user": {
                "username": request.user.username,
                "name": request.user.first_name,
                "role": _effective_role(request.user),
                "is_admin": _is_admin_user(request.user),
            },
            "hostels": hostels,
            "allocations": allocations,
            }
        )
    except OperationalError:
        return JsonResponse({"status": "error", "message": "Database error. Hakikisha PostgreSQL ina-run."}, status=503)
    except Exception:
        return JsonResponse({"status": "error", "message": "Dashboard failed unexpectedly."}, status=400)


@require_GET
def export_allocations_csv(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

    if _is_admin_user(request.user):
        allocations_qs = Allocation.objects.select_related("student", "hostel").order_by("-allocated_on")
    else:
        allocations_qs = Allocation.objects.select_related("student", "hostel").filter(student=request.user).order_by("-allocated_on")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="allocations_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Student", "Hostel", "Room", "Allocated On"])
    for allocation in allocations_qs:
        writer.writerow(
            [
                allocation.id,
                allocation.student.username,
                allocation.hostel.name,
                allocation.room_number or "",
                allocation.allocated_on.isoformat(),
            ]
        )
    return response


@require_GET
def admin_dashboard_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
    if not _is_admin_user(request.user):
        return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)

    users = list(
        User.objects.values("id", "username", "first_name", "role", "is_staff").order_by("username")
    )
    allocations = list(
        Allocation.objects.select_related("student", "hostel")
        .values("id", "student__username", "hostel__name", "room_number", "allocated_on")
        .order_by("-allocated_on")
    )
    activities = list(
        ActivityLog.objects.select_related("user")
        .values("id", "user__username", "action", "details", "created_at")
        .order_by("-created_at")[:200]
    )

    return JsonResponse(
        {
            "status": "success",
            "summary": {
                "total_users": User.objects.count(),
                "total_students": User.objects.filter(role="student").count(),
                "total_hostels": Hostel.objects.count(),
                "total_allocations": Allocation.objects.count(),
                "total_activities": ActivityLog.objects.count(),
            },
            "users": users,
            "allocations": allocations,
            "activities": activities,
        }
    )


@csrf_exempt
@require_POST
def admin_delete_user_api(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
    if not _is_admin_user(request.user):
        return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)

    target = User.objects.filter(id=user_id).first()
    if not target:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    if target.id == request.user.id:
        return JsonResponse({"status": "error", "message": "Huwezi kujifuta mwenyewe"}, status=400)

    allocations = list(Allocation.objects.select_related("hostel").filter(student=target))
    for allocation in allocations:
        if allocation.hostel_id:
            Hostel.objects.filter(id=allocation.hostel_id).update(total_rooms=F("total_rooms") + 1)

    username = target.username
    target.delete()
    _log_activity(request.user, "allocate", f"Deleted user {username} and released {len(allocations)} room(s)")

    return JsonResponse({"status": "success", "message": f"User {username} deleted"})


@csrf_exempt
@require_POST
def admin_update_room_api(request, allocation_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
    if not _is_admin_user(request.user):
        return JsonResponse({"status": "error", "message": "Admin access required"}, status=403)

    data = _json_body(request)
    if data is None:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    room_number = (data.get("room_number") or "").strip()
    if not room_number:
        return JsonResponse({"status": "error", "message": "Room number is required"}, status=400)

    allocation = Allocation.objects.select_related("student", "hostel").filter(id=allocation_id).first()
    if not allocation:
        return JsonResponse({"status": "error", "message": "Allocation not found"}, status=404)

    old_room = allocation.room_number or "-"
    allocation.room_number = room_number
    allocation.save(update_fields=["room_number"])

    duplicate_allocations = Allocation.objects.filter(student=allocation.student).exclude(id=allocation.id)
    removed_count = duplicate_allocations.count()
    if removed_count:
        duplicate_allocations.delete()

    _log_activity(
        request.user,
        "allocate",
        f"Updated room for {allocation.student.username} in {allocation.hostel.name}: {old_room} -> {room_number} (removed {removed_count} duplicate allocation(s))",
    )

    return JsonResponse(
        {
            "status": "success",
            "message": f"Room number updated. Removed {removed_count} old allocation(s).",
            "allocation": {
                "id": allocation.id,
                "student__username": allocation.student.username,
                "hostel__name": allocation.hostel.name,
                "room_number": allocation.room_number,
                "allocated_on": allocation.allocated_on.isoformat(),
            },
        }
    )
