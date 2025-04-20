from django.contrib import admin
from .models import Project, Task

class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ('title', 'status', 'category', 'due_date', 'is_overdue')
    readonly_fields = ('is_overdue',)
    show_change_link = True

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_completed', 'completion_percentage', 'updated_at')
    list_filter = ('is_completed', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__email')
    inlines = [TaskInline]

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'category', 'due_date', 'is_overdue', 'created_by')
    list_filter = ('status', 'category', 'due_date')
    search_fields = ('title', 'description', 'project__name', 'created_by__email')
    readonly_fields = ('is_overdue',)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
