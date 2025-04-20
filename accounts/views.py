from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import User, Profile, PasswordResetToken
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm,
    ProfileUpdateForm,
    PasswordChangeForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from projects.models import Project, Task

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, 'Logged in successfully!')
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def dashboard(request):
    active_projects = Project.objects.filter(owner=request.user, is_completed=False).order_by('-updated_at')[:5]
    recent_tasks = Task.objects.filter(created_by=request.user).order_by('-updated_at')[:10]
    
    # Task status summary
    task_status = {
        'active': Task.objects.filter(created_by=request.user, status='active').count(),
        'in_progress': Task.objects.filter(created_by=request.user, status='in_progress').count(),
        'complete': Task.objects.filter(created_by=request.user, status='complete').count(),
    }
    
    context = {
        'active_projects': active_projects,
        'recent_tasks': recent_tasks,
        'task_status': task_status,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile_settings(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_settings')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_settings.html', {'profile_form': profile_form})

@login_required
def security_settings(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('security_settings')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/security_settings.html', {'form': form})

@login_required
def toggle_2fa(request):
    user = request.user
    user.two_factor_enabled = not user.two_factor_enabled
    user.save()
    status = "enabled" if user.two_factor_enabled else "disabled"
    messages.success(request, f'Two-factor authentication {status}.')
    return redirect('security_settings')

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Create reset token
                token = PasswordResetToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + timedelta(hours=1)
                )
                # Send email
                subject = 'Password Reset Request'
                html_message = render_to_string('accounts/password_reset_email.html', {
                    'user': user,
                    'token': token.token,
                })
                plain_message = strip_tags(html_message)
                send_mail(
                    subject,
                    plain_message,
                    None,
                    [user.email],
                    html_message=html_message,
                )
                messages.success(request, 'Password reset link sent to your email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No user with that email address exists.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False, expires_at__gt=timezone.now())
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetForm(reset_token.user, request.POST)
        if form.is_valid():
            form.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Password reset successfully. You can now login with your new password.')
            return redirect('login')
    else:
        form = PasswordResetForm(reset_token.user)
    
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})