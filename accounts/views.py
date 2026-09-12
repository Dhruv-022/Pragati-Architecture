from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import User
from .forms import DynamicUserCreationForm


# --- AUTHENTICATION & SMART ROUTING ---

def smart_login_view(request):
    """Central entry point routing each user to their primary operational workspace"""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            if user.status != User.Status.ACTIVE:
                form.add_error(None, "This account is inactive or suspended. Contact your Administrator.")
                return render(request, 'accounts/login.html', {'form': form})

            login(request, user)
            return redirect_user_by_role(user)
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def redirect_user_by_role(user):
    """Router helper: Sends System Admin to Control Center, all other roles to Work Dashboards"""
    if user.role == User.Role.SYSTEM_ADMIN or user.is_superuser:
        return redirect('admin_dashboard') # Control Center
    elif user.role == User.Role.DISTRICT_ADMIN:
        return redirect('district_dashboard') # District Operations Dashboard!
    elif user.role == User.Role.MONITORING_OFFICER:
        return redirect('monitoring_dashboard') # Monitoring Field Workspace
    elif user.role == User.Role.INVESTIGATOR:
        return redirect('investigation_dashboard') # Case Management Workspace
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('login')


def custom_403_view(request, exception=None):
    return render(request, 'accounts/403.html', status=403)


# --- USER MANAGEMENT CONTROL PANEL ---

@login_required
def admin_dashboard(request):
    """Control Panel for provisioning accounts (Accessible by System Admin & District Admin)"""
    user = request.user
    
    if not (user.is_system_admin or user.is_district_admin):
        raise PermissionDenied("You do not have permission to access the User Control Panel.")

    if user.is_system_admin:
        managed_users = User.objects.all().order_by('-id')
    else:
        managed_users = User.objects.filter(jurisdiction=user.jurisdiction).order_by('-id')

    return render(request, 'accounts/dashboard.html', {'users': managed_users})


@login_required
def create_user(request):
    user = request.user

    if not (user.is_system_admin or user.is_district_admin):
        raise PermissionDenied("You do not have permission to create users.")

    if request.method == 'POST':
        form = DynamicUserCreationForm(request.POST, logged_in_user=user)
        if form.is_valid():
            new_user = form.save(commit=False)
            
            if user.is_district_admin:
                new_user.jurisdiction = user.jurisdiction
            
            if new_user.role in [User.Role.SYSTEM_ADMIN, User.Role.DISTRICT_ADMIN]:
                new_user.is_staff = True

            new_user.save()
            return redirect('admin_dashboard')
    else:
        form = DynamicUserCreationForm(logged_in_user=user)

    return render(request, 'accounts/create_user.html', {'form': form})


# --- OPERATIONAL WORKSPACE DASHBOARDS ---

@login_required
def district_dashboard(request):
    return render(request, 'dashboards/district_admin.html')


@login_required
def monitoring_dashboard(request):
    return render(request, 'dashboards/monitoring_officer.html')


@login_required
def investigation_dashboard(request):
    return render(request, 'dashboards/investigator.html')