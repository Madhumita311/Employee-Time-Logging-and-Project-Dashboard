
# timetrackapp/forms.py
from django import forms
from .models import WorkHour  # Assuming you have a model named WorkHour
from django import forms
from django.contrib.admin.widgets import AdminTextInputWidget
from .models import Goal, DailyUpdate


# class GoalForm(forms.ModelForm):
#     class Meta:
#         model = Goal
#         fields = ['title', 'description', 'start_date', 'end_date', 'completed', 'dependencies', 'planned']

#     def save(self, commit=True):
#         goal = super().save(commit=False)
#         if commit:
#             goal.user = self.user  # Assuming you're passing user when initializing the form
#             goal.save()
#         return goal
#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)  # Get the user from the keyword arguments
#         super().__init__(*args, **kwargs)

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'planned']  # Adjust fields as necessary

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get user from keyword arguments
        super().__init__(*args, **kwargs)
        
        # Optional: set placeholder for 'planned'
        self.fields['planned'].widget.attrs['placeholder'] = "Enter your weekly planned goals"

    def save(self, commit=True):
        goal = super().save(commit=False)
        if self.user:
            goal.user = self.user  # Set user if provided
        if commit:
            goal.save()
        return goal

class DailyUpdateForm(forms.ModelForm):
    class Meta:
        model = DailyUpdate
        fields = ['date','completed_tasks', 'pending_tasks', 'dependencies']
class MyForm(forms.Form):
    name = forms.CharField(widget=AdminTextInputWidget())
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'vTextField'}))


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
    # email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}
# timetrackapp/forms.py

# from django import forms
# from .models import Goal

# class GoalForm(forms.ModelForm):
#     class Meta:
#         model = Goal
#         fields = ['planned']  # Only allow users to enter planned goals

# def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['planned'].widget.attrs['placeholder'] = "Enter your weekly planned goals"

# class GoalUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Goal
#         fields = ['completed', 'dependencies', 'pending']