from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncWeek
from django.contrib.auth.models import User
import datetime
# class Project(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()

#     def __str__(self):
#         return self.name
class Project(models.Model):
    id = models.AutoField(primary_key=True) 
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # To track if the project is running

    def __str__(self):
        return self.name
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # project = models.CharField(max_length=255)
    planned = models.TextField()
    completed = models.TextField(blank=True)
    dependencies = models.TextField(blank=True)
    pending = models.TextField(blank=True)
    title = models.CharField(max_length=200,default="Untitled") 
    is_started = models.BooleanField(default=False) 
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=datetime.date.today() + timedelta(days=30))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title  
class DailyUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField()
    completed_tasks = models.TextField()
    pending_tasks = models.TextField()
    dependencies = models.TextField()

    def __str__(self):
        return f"Update for {self.user} on {self.date}"
    
    
    # def is_locked(self):
    #     """Lock goals after Friday of the current week."""
    #     today = now().date()
    #     current_week_start = today - timedelta(days=today.weekday())  # Monday
    #     friday = current_week_start + timedelta(days=4)  # Friday of current week
    #     return today > friday

class UserProjectHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE) 
    stop_time = models.DateTimeField(null=True, blank=True) 
    @staticmethod
    def get_weekly_hours(user):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=4)  # Friday
        # Filter the entries for the user for the period Monday to Friday
        weekly_hours = UserProjectHistory.objects.filter(
            user=user,
            start_time__gte=start_of_week,
            start_time__lte=end_of_week
        ).aggregate(total_week_hours=Sum('total_hours'))
        return weekly_hours['total_week_hours'] or 0

User = get_user_model()
class WorkHour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True, blank=True)
    total_hours = models.FloatField(null=False, default=0.0)
    class Meta:
        indexes = [
            models.Index(fields=['user', 'project', 'start_time']),
        ]
    def save(self, *args, **kwargs):
        if self.start_time and self.stop_time:
            if self.stop_time < self.start_time:
                raise ValueError("Stop time cannot be earlier than start time.")
            self.total_hours = (self.stop_time - self.start_time).total_seconds() / 3600  # convert seconds to hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} worked on {self.project.name} for {self.total_hours} hours"
