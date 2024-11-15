from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class WorkHour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True, blank=True)
    total_hours = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.stop_time:
            self.total_hours = (self.stop_time - self.start_time).total_seconds() / 3600  # convert seconds to hours
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} worked on {self.project.name} for {self.total_hours} hours"
