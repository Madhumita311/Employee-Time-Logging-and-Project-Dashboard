from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)  # This will automatically set the time when the object is created
    # updated_at = models.DateTimeField(auto_now=True)  # This will automatically update the time when the object is updated
    
    def __str__(self):
        return self.name

class WorkHour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField()
    total_hours = models.FloatField(null=False, default=0.0)

    def save(self, *args, **kwargs):
        if self.start_time and self.stop_time:
            if self.stop_time < self.start_time:
                raise ValueError("Stop time cannot be earlier than start time.")
            self.total_hours = (self.stop_time - self.start_time).total_seconds() / 3600  # convert seconds to hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} worked on {self.project.name} for {self.total_hours} hours"
