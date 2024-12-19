from django.contrib import admin
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io,base64
from .forms import DailyUpdateForm
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from .models import Goal,UserProjectHistory,User, DailyUpdate,Project, WorkHour
@admin.register(Project)
class Project(admin.ModelAdmin):
    list_display = ('name',)  # Customize the fields you want to display
    search_fields = ('name',)  # Search projects by name

@admin.register(WorkHour)
class WorkHour(admin.ModelAdmin):
    list_display = ('user', 'project', 'start_time', 'stop_time', 'total_hours')  # Display these fields
    search_fields = ('username', 'project')  # Allow searching by user or project name
    list_filter = ('start_time', 'stop_time')  # Filter by time range

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user','title','planned', 'start_date', 'end_date')

@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    form=DailyUpdateForm
    list_display = ('user','goal', 'get_completed_tasks','get_pending_tasks','dependencies','date')
    fields = ['date', 'completed_tasks', 'pending_tasks', 'dependencies']  # Add editable fields
    readonly_fields = ['user','goal']
    def get_completed_tasks(self, obj):
        return obj.completed_tasks  # Adjust this if needed
    def get_pending_tasks(self, obj):
        return obj.pending_tasks 
    def save_model(self, request, obj, form, change):
        if change:  # If it is an update, not a new instance
            obj.modified_by = request.user  # Example of custom logic
        super().save_model(request, obj, form, change) 

@admin.register(UserProjectHistory)
class UserProjectHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'total_hours')

    # Define an admin action to calculate weekly hours and show a graph
    def calculate_weekly_hours(self, request, queryset):
        user = queryset.first().user  # Assuming queryset has users with the same ID
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        weekly_project_hours = (
            UserProjectHistory.objects.filter(user=user, start_time__gte=start_of_week)
            .values('project__name')
            .annotate(total_hours=Sum('total_hours'))
        )
        
        # Prepare data for plotting
        project_names = [entry['project__name'] for entry in weekly_project_hours]
        hours = [entry['total_hours'] for entry in weekly_project_hours]
        plt.figure(figsize=(6, 4))
        plt.bar(project_names, hours, color=['#4A90E2', '#7ED321', '#F5A623', '#9B59B6', '#FF6F61', '#1ABC9C'])
        plt.xlabel('Projects')
        plt.ylabel('Hours Worked')
        plt.title('Weekly Project Hours')
        plt.xticks(rotation=45, ha='right')  # Rotate project names for better visibility
        plt.tight_layout()
        # Save plot to a BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        # Embed the graph as an image in the admin response
        html = f"""
        <h2>Total weekly hours worked for {user}</h2>
        <img src="data:image/png;base64,{image_base64}" />
        <p>Total Hours Worked This Week: {sum(hours)} hours</p>
        """
        return HttpResponse(html, content_type="text/html")

    actions = [calculate_weekly_hours]

