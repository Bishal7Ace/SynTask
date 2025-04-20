from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import csv
from projects.models import Project, Task
from datetime import datetime
from django.db.models import Count


@login_required
def project_report(request, pk):
    project = Project.objects.get(pk=pk, owner=request.user)
    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'tasks': tasks,
    }
    return render(request, 'reports/project_report.html', context)

@login_required
def export_project_pdf(request, pk):
    project = Project.objects.get(pk=pk, owner=request.user)
    tasks = project.tasks.all()
    
    template_path = 'reports/project_report_pdf.html'
    context = {
        'project': project,
        'tasks': tasks,
        'date': datetime.now().strftime("%Y-%m-%d"),
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="project_{project.id}_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors generating the PDF')
    return response

@login_required
def export_project_csv(request, pk):
    project = Project.objects.get(pk=pk, owner=request.user)
    tasks = project.tasks.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="project_{project.id}_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project Report', f'Generated on {datetime.now().strftime("%Y-%m-%d")}'])
    writer.writerow([])
    writer.writerow(['Project Name', project.name])
    writer.writerow(['Description', project.description])
    writer.writerow(['Created', project.created_at.strftime("%Y-%m-%d")])
    writer.writerow(['Last Updated', project.updated_at.strftime("%Y-%m-%d")])
    writer.writerow(['Completion Status', 'Completed' if project.is_completed else 'In Progress'])
    writer.writerow(['Completion Percentage', f"{project.completion_percentage}%"])
    writer.writerow([])
    writer.writerow(['Tasks'])
    writer.writerow(['Title', 'Description', 'Status', 'Category', 'Due Date', 'Created At'])
    
    for task in tasks:
        writer.writerow([
            task.title,
            task.description,
            task.get_status_display(),
            task.get_category_display(),
            task.due_date.strftime("%Y-%m-%d") if task.due_date else '',
            task.created_at.strftime("%Y-%m-%d %H:%M"),
        ])
    
    return response

@login_required
def overall_report(request):
    projects = Project.objects.filter(owner=request.user)
    tasks = Task.objects.filter(created_by=request.user)
    
    # Project completion stats
    completed_projects = projects.filter(is_completed=True).count()
    active_projects = projects.filter(is_completed=False).count()
    
    # Task status stats
    task_status = {
        'active': tasks.filter(status='active').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'complete': tasks.filter(status='complete').count(),
    }
    
    # Task category stats
    task_categories = tasks.values('category').annotate(count=Count('category')).order_by('-count')
    
    context = {
        'projects': projects,
        'completed_projects': completed_projects,
        'active_projects': active_projects,
        'task_status': task_status,
        'task_categories': task_categories,
    }
    return render(request, 'reports/overall_report.html', context)

@login_required
def export_overall_pdf(request):
    projects = Project.objects.filter(owner=request.user)
    tasks = Task.objects.filter(created_by=request.user)
    
    completed_projects = projects.filter(is_completed=True).count()
    active_projects = projects.filter(is_completed=False).count()
    
    task_status = {
        'active': tasks.filter(status='active').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'complete': tasks.filter(status='complete').count(),
    }
    
    task_categories = tasks.values('category').annotate(count=Count('category')).order_by('-count')
    
    template_path = 'reports/overall_report_pdf.html'
    context = {
        'projects': projects,
        'completed_projects': completed_projects,
        'active_projects': active_projects,
        'task_status': task_status,
        'task_categories': task_categories,
        'date': datetime.now().strftime("%Y-%m-%d"),
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="overall_task_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors generating the PDF')
    return response

@login_required
def export_overall_csv(request):
    projects = Project.objects.filter(owner=request.user)
    tasks = Task.objects.filter(created_by=request.user)
    
    completed_projects = projects.filter(is_completed=True).count()
    active_projects = projects.filter(is_completed=False).count()
    
    task_status = {
        'active': tasks.filter(status='active').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'complete': tasks.filter(status='complete').count(),
    }
    
    task_categories = tasks.values('category').annotate(count=Count('category')).order_by('-count')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="overall_task_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Overall Task Report', f'Generated on {datetime.now().strftime("%Y-%m-%d")}'])
    writer.writerow([])
    writer.writerow(['Project Statistics'])
    writer.writerow(['Total Projects', projects.count()])
    writer.writerow(['Completed Projects', completed_projects])
    writer.writerow(['Active Projects', active_projects])
    writer.writerow([])
    writer.writerow(['Task Statistics'])
    writer.writerow(['Total Tasks', tasks.count()])
    writer.writerow(['Active Tasks', task_status['active']])
    writer.writerow(['In Progress Tasks', task_status['in_progress']])
    writer.writerow(['Completed Tasks', task_status['complete']])
    writer.writerow([])
    writer.writerow(['Tasks by Category'])
    writer.writerow(['Category', 'Count'])
    
    for category in task_categories:
        writer.writerow([
            dict(Task.CATEGORY_CHOICES)[category['category']],
            category['count']
        ])
    
    return response