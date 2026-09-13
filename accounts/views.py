from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import User
from .forms import DynamicUserCreationForm
from projects.models import Project
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count
from django.views.decorators.http import require_POST
from .forms import DynamicUserCreationForm
from projects.models import Project
from jurisdictions.models import Jurisdiction


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
    origin = request.session.get('login_origin', 'main')

    logout(request)

    if origin == 'admin':
        return redirect('admin_login')
    
    return redirect('login')

def custom_403_view(request, exception=None):
    return render(request, 'accounts/403.html', status=403)


# --- SYSTEM ADMIN CONTROL PANEL ---

@login_required(login_url='admin_login')
def admin_dashboard(request):
    """Executive Dashboard with Metrics, Interactive Drawer Data, and Visual Charts"""
    user = request.user
    if not (user.is_system_admin or user.is_district_admin or user.is_superuser):
        raise PermissionDenied("Access Denied.")

    # Projects Aggregation
    all_projects = Project.objects.all()
    total_projects = all_projects.count()
    total_sanctioned = all_projects.aggregate(Sum('sanctioned_amount'))['sanctioned_amount__sum'] or 0
    total_released = all_projects.aggregate(Sum('funds_released'))['funds_released__sum'] or 0

    completed_count = all_projects.filter(status=Project.Status.COMPLETED).count()
    in_progress_count = all_projects.filter(status=Project.Status.IN_PROGRESS).count()
    proposed_count = all_projects.filter(status=Project.Status.PROPOSED).count()

    # User Role Breakdown
    system_admins = User.objects.filter(role=User.Role.SYSTEM_ADMIN).order_by('-id')
    officials = User.objects.exclude(role=User.Role.SYSTEM_ADMIN).order_by('-id')

    # Chart Data: Category Breakdown
    cat_data = list(all_projects.values('category').annotate(count=Count('id')))
    chart_labels = [item['category'] for item in cat_data]
    chart_counts = [item['count'] for item in cat_data]

    context = {
        'total_projects': total_projects,
        'total_sanctioned': f"₹{total_sanctioned:,.2f}",
        'total_released': f"₹{total_released:,.2f}",
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'proposed_count': proposed_count,
        'system_admins': system_admins,
        'system_admins_count': system_admins.count(),
        'officials': officials,
        'officials_count': officials.count(),
        'chart_labels': chart_labels,
        'chart_counts': chart_counts,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='admin_login')
def manage_users_view(request):
    """Dedicated Page for Viewing & Managing Users"""
    user = request.user
    if not (user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Access Restricted.")

    users = User.objects.all().order_by('-id')
    return render(request, 'accounts/manage_users.html', {'users': users})

@login_required(login_url='admin_login')
def edit_user(request, user_id):
    """View to Edit User Details (Username, Name, Role, Jurisdiction)"""
    user = request.user
    if not (user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Access Restricted.")

    target_user = get_object_or_404(User, id=user_id)
    is_self = (target_user == user)

    if request.method == 'POST':
        target_user.username = request.POST.get('username')
        target_user.first_name = request.POST.get('first_name')
        target_user.last_name = request.POST.get('last_name')

        # Prevent changing own role or jurisdiction
        if not is_self:
            target_user.role = request.POST.get('role')
            jurisdiction_id = request.POST.get('jurisdiction')
            if jurisdiction_id:
                target_user.jurisdiction = get_object_or_404(Jurisdiction, id=jurisdiction_id)
            else:
                target_user.jurisdiction = None

        target_user.save()
        return redirect('manage_users')

    context = {
        'target_user': target_user,
        'is_self': is_self,
        'roles': User.Role.choices,
        'jurisdictions': Jurisdiction.objects.all(),
    }
    return render(request, 'accounts/edit_user.html', context)

@login_required(login_url='admin_login')
def project_directory_view(request):
    """Dedicated Page for System-Wide Projects Explorer"""
    user = request.user
    if not (user.is_system_admin or user.is_district_admin or user.is_superuser):
        raise PermissionDenied("Access Restricted.")

    projects = Project.objects.all().order_by('project_id')
    return render(request, 'accounts/project_directory.html', {'projects': projects})

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
            
            if not (user.is_system_admin or user.is_district_admin):
                raise PermissionDenied("Access Denied: You do not have Administrative privileges.")

            login(request, user)
            
            request.session['login_origin'] = 'admin'
            request.session.modified = True

            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/admin_login.html', {'form': form, 'next': next_url})


# --- OPERATIONAL WORKSPACE DASHBOARDS ---

@login_required(login_url='login')
def district_dashboard(request):
    """District Administrator Workspace — Scoped to User Jurisdiction"""
    user = request.user
    
    if not (user.is_district_admin or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Access restricted to District Administrators.")
    
    if user.jurisdiction:
        district_projects = Project.objects.filter(jurisdiction=user.jurisdiction).order_by('-id')
        jurisdiction_name = user.jurisdiction.name
    else:
        district_projects = Project.objects.all().order_by('-id')
        jurisdiction_name = "Global / All Districts"

    total_projects = district_projects.count()
    total_sanctioned = district_projects.aggregate(Sum('sanctioned_amount'))['sanctioned_amount__sum'] or 0
    total_released = district_projects.aggregate(Sum('funds_released'))['funds_released__sum'] or 0

    completed_count = district_projects.filter(status=Project.Status.COMPLETED).count()
    in_progress_count = district_projects.filter(status=Project.Status.IN_PROGRESS).count()
    proposed_count = district_projects.filter(status=Project.Status.PROPOSED).count()

    cat_data = list(district_projects.values('category').annotate(count=Count('id')))
    chart_labels = [item['category'] for item in cat_data]
    chart_counts = [item['count'] for item in cat_data]

    context = {
        'jurisdiction_name': jurisdiction_name,
        'projects': district_projects,
        'total_projects': total_projects,
        'total_sanctioned': f"₹{total_sanctioned:,.2f}",
        'total_released': f"₹{total_released:,.2f}",
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'proposed_count': proposed_count,
        'chart_labels': chart_labels,
        'chart_counts': chart_counts,
        'can_access_admin': (user.is_system_admin or user.is_district_admin or user.is_superuser),
    }

    return render(request, 'dashboards/district_admin.html', context)

# In accounts/views.py

@login_required(login_url='login')
def monitoring_dashboard(request):
    """Monitoring Officer Workspace — Scoped Inspection & Status Control Panel"""
    user = request.user
    
    if not (user.role == User.Role.MONITORING_OFFICER or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Access restricted to Monitoring Officers.")
    
    # Scoped Queryset by Jurisdiction
    if user.jurisdiction:
        projects = Project.objects.filter(jurisdiction=user.jurisdiction).order_by('-id')
        jurisdiction_name = user.jurisdiction.name
    else:
        projects = Project.objects.all().order_by('-id')
        jurisdiction_name = "Global / All Districts"

    # Aggregates for field status tracking
    total_projects = projects.count()
    completed_count = projects.filter(status=Project.Status.COMPLETED).count()
    in_progress_count = projects.filter(status=Project.Status.IN_PROGRESS).count()
    proposed_count = projects.filter(status=Project.Status.PROPOSED).count()

    # Calculate overall progress completion %
    completion_rate = round((completed_count / total_projects * 100), 1) if total_projects > 0 else 0

    context = {
        'jurisdiction_name': jurisdiction_name,
        'projects': projects,
        'total_projects': total_projects,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'proposed_count': proposed_count,
        'completion_rate': completion_rate,
        'status_choices': Project.Status.choices,
    }

    return render(request, 'dashboards/monitoring_officer.html', context)


@require_POST
@login_required(login_url='login')
def update_project_status(request, project_id):
    """View to update a project's operational status directly from the workspace"""
    user = request.user
    if not (user.role == User.Role.MONITORING_OFFICER or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Unauthorized action.")

    project = get_object_or_404(Project, id=project_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Project.Status.choices):
        project.status = new_status
        project.save()

    return redirect('monitoring_dashboard')

@require_POST
@login_required(login_url='login')
def update_project_status(request, project_id):
    """View to update a project's operational status directly from the workspace"""
    user = request.user
    if not (user.role == User.Role.MONITORING_OFFICER or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Unauthorized action.")

    project = get_object_or_404(Project, id=project_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Project.Status.choices):
        project.status = new_status
        project.save()

    return redirect('monitoring_dashboard')

@login_required(login_url='login')
def investigation_dashboard(request):
    """Investigator Officer Workspace — Displays Flagged Audits & Field Investigations"""
    user = request.user
    
    if not (user.role == User.Role.INVESTIGATOR or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Access restricted to Investigator Officers.")

    # Filter projects flagged for investigation within user's jurisdiction
    if user.jurisdiction:
        flagged_projects = Project.objects.filter(
            jurisdiction=user.jurisdiction,
            is_under_investigation=True
        ).select_related('flagged_by', 'jurisdiction').order_by('-id')
        jurisdiction_name = user.jurisdiction.name
    else:
        flagged_projects = Project.objects.filter(
            is_under_investigation=True
        ).select_related('flagged_by', 'jurisdiction').order_by('-id')
        jurisdiction_name = "Global / All Districts"

    context = {
        'jurisdiction_name': jurisdiction_name,
        'flagged_projects': flagged_projects,
        'total_audits': flagged_projects.count(),
    }

    return render(request, 'dashboards/investigator.html', context)
from django.views.decorators.http import require_POST

@require_POST
@login_required(login_url='admin_login')
def delete_user(request, user_id):
    """Deletes a user account ensuring administrators cannot delete themselves."""
    current_user = request.user

    # Permission check
    if not (current_user.is_system_admin or current_user.is_district_admin or current_user.is_superuser):
        raise PermissionDenied("You do not have administrative privileges.")

    target_user = get_object_or_404(User, id=user_id)

    # Self-deletion safeguard
    if target_user == current_user:
        # Prevent self-deletion directly
        return redirect('admin_dashboard')

    # District Admin scope constraint
    if current_user.is_district_admin and target_user.jurisdiction != current_user.jurisdiction:
        raise PermissionDenied("You can only delete users within your assigned jurisdiction.")

    target_user.delete()
    return redirect('admin_dashboard')

# In accounts/views.py

@require_POST
@login_required(login_url='login')
def flag_project_for_investigation(request, project_id):
    """View for Monitoring Officers to flag a project for investigation"""
    user = request.user
    
    if not (user.role == User.Role.MONITORING_OFFICER or user.is_system_admin or user.is_superuser):
        raise PermissionDenied("Only Monitoring Officers can flag projects for investigation.")

    project = get_object_or_404(Project, id=project_id)
    reason = request.POST.get('reason', '').strip()

    project.is_under_investigation = True
    project.flagged_by = user
    if reason:
        project.investigation_reason = reason
    project.save()

    return redirect('monitoring_dashboard')