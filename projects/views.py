from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from django.db.models import Count, Q
from django.http import JsonResponse

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    tasks = project.tasks.all().order_by('-updated_at')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm()
    
    context = {
        'project': project,
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'projects/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    project_pk = task.project.pk
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('project_detail', pk=project_pk)
    return render(request, 'projects/task_confirm_delete.html', {'task': task})

@login_required
def task_list(request):
    tasks = Task.objects.filter(created_by=request.user).order_by('-updated_at')
    
    # Filters
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if category_filter:
        tasks = tasks.filter(category=category_filter)
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'projects/task_list.html', context)

@login_required
def update_task_status(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        task = get_object_or_404(Task, pk=pk, created_by=request.user)
        new_status = request.POST.get('status')
        
        if new_status in dict(Task.STATUS_CHOICES).keys():
            task.status = new_status
            task.save()
            return JsonResponse({
                'success': True,
                'status': task.get_status_display(),
                'completion_percentage': task.project.completion_percentage,
            })
    
    return JsonResponse({'success': False}, status=400)