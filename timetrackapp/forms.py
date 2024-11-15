
# timetrackapp/forms.py
from django import forms
from .models import WorkHour  # Assuming you have a model named WorkHour

class WorkHourForm(forms.ModelForm):
    class Meta:
        model = WorkHour
        fields = ['start_time', 'stop_time', 'project', 'user'] 

from django import forms
from .models import Project  # Ensure this is importing your Project model

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project  # Use the Project model here
        fields = ['name', 'description']
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    # Add custom fields or widgets if needed
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
