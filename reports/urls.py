from django.urls import path
from . import views

urlpatterns = [
    path('projects/<int:pk>/', views.project_report, name='project_report'),
    path('projects/<int:pk>/export-pdf/', views.export_project_pdf, name='export_project_pdf'),
    path('projects/<int:pk>/export-csv/', views.export_project_csv, name='export_project_csv'),
    path('overall/', views.overall_report, name='overall_report'),
    path('overall/export-pdf/', views.export_overall_pdf, name='export_overall_pdf'),
    path('overall/export-csv/', views.export_overall_csv, name='export_overall_csv'),
]