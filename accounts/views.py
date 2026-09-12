from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import User
from .forms import DynamicUserCreationForm


# --- AUTHENTICATION & SMART ROUTING ---

def smart_login_view(request):
    """Main Portal Login View (Dark Theme)"""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            if user.status != User.Status.ACTIVE:
                form.add_error(None, "This account is inactive or suspended.")
                return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

            login(request, user)
            
            # Record origin tag in session
            request.session['login_origin'] = 'main'
            request.session.modified = True

            if next_url and next_url != '/login/':
                return redirect(next_url)

            return redirect_user_by_role(user)
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

def redirect_user_by_role(user):
    """Router helper mapping role to designated workspace"""
    if user.role == User.Role.SYSTEM_ADMIN or user.is_superuser:
        return redirect('admin_dashboard')
    elif user.role == User.Role.DISTRICT_ADMIN:
        return redirect('district_dashboard')
    elif user.role == User.Role.MONITORING_OFFICER:
        return redirect('monitoring_dashboard')
    elif user.role == User.Role.INVESTIGATOR:
        return redirect('investigation_dashboard')
    return redirect('login')


def logout_view(request):
    """Dynamic logout routing based on login origin"""
    # Grab the entry point origin BEFORE calling logout()
    origin = request.session.get('login_origin', 'main')

    logout(request)

    # Route back to exact entry point page
    if origin == 'admin':
        return redirect('admin_login')
    
    return redirect('login')

def custom_403_view(request, exception=None):
    return render(request, 'accounts/403.html', status=403)


# --- SYSTEM ADMIN CONTROL PANEL ---

@login_required
def admin_dashboard(request):
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


def admin_login_view(request):
    """Admin Control Panel Login View (Amber Theme)"""
    if request.user.is_authenticated:
        if request.user.is_system_admin or request.user.is_district_admin:
            return redirect('admin_dashboard')
        raise PermissionDenied("Access restricted to Administrators.")

    next_url = request.GET.get('next', 'admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user has Administrative privileges
            if not (user.is_system_admin or user.is_district_admin):
                # Raise 403 Forbidden immediately for unauthorized roles
                raise PermissionDenied("Access Denied: You do not have Administrative privileges.")

            login(request, user)
            
            # Record origin tag in session
            request.session['login_origin'] = 'admin'
            request.session.modified = True

            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/admin_login.html', {'form': form, 'next': next_url})

@login_required(login_url='admin_login')
def admin_dashboard(request):
    user = request.user
    
    if not (user.is_system_admin or user.is_district_admin):
        raise PermissionDenied("You do not have permission to access the User Control Panel.")

    if user.is_system_admin:
        managed_users = User.objects.all().order_by('-id')
    else:
        managed_users = User.objects.filter(jurisdiction=user.jurisdiction).order_by('-id')

    return render(request, 'accounts/dashboard.html', {'users': managed_users})

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