from django.contrib import admin
from django.contrib import admin
from .models import Project, WorkHour

# # Registering the Project model to the admin panel
@admin.register(Project)
class Project(admin.ModelAdmin):
    list_display = ('name',)  # Customize the fields you want to display
    search_fields = ('name',)  # Search projects by name
    # list_filter = ('created_at',)  # Filter by creation date

@admin.register(WorkHour)
class WorkHour(admin.ModelAdmin):
    list_display = ('user', 'project', 'start_time', 'stop_time', 'total_hours')  # Display these fields
    search_fields = ('username', 'project')  # Allow searching by user or project name
    list_filter = ('start_time', 'stop_time')  # Filter by time range

