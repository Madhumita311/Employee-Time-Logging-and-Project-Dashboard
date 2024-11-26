from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Project, WorkHour
from .forms import ProjectForm, WorkHourForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import CustomLoginForm
# from django.contrib.auth import login, authenticate

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page or another page after login
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})
# Home page with start button (logged in user)
@login_required
def home(request):
    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects})

# User signup view

# def signup(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()  # Save the new user to the database
#             return redirect("login")  # Redirect to login page after successful signup
#     else:
#         form = UserCreationForm()  # Empty form for GET request
#     return render(request, "registration/signup.html", {"form": form})
from django.contrib.auth import login
from django.contrib import messages

# User signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user and log them in
            user = form.save()
            login(request, user)  # Log in the user after successful signup
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')  # Redirect to the home page or any other page
        else:
            # If the form is not valid, show errors
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html',{'form':form})

# Start and stop work on a project
@login_required
def start_work(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        work_hour = WorkHour(user=request.user, project=project, start_time=datetime.now())
        work_hour.save()
    return redirect('home')

@login_required
def stop_work(request, work_hour_id):
    work_hour = WorkHour.objects.get(id=work_hour_id)
    if request.method == 'POST':
        work_hour.stop_time = datetime.now()
        work_hour.save()
    return redirect('home')

# Admin page for managing projects (add, edit, delete)
@login_required
def admin_view(request):
    if not request.user.is_staff:
        return redirect('home')
    
    projects = Project.objects.all()
    return render(request, 'admin_view.html', {'projects': projects})

# Admin can add a project
@login_required
def add_project(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_view')
    return render(request, 'add_project.html', {'form': ProjectForm()})

# Admin can edit a project
@login_required
def edit_project(request, project_id):
    if not request.user.is_staff:
        return redirect('home')

    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('admin_view')
    return render(request, 'edit_project.html', {'form': ProjectForm(instance=project)})

# Admin can delete a project
@login_required
def delete_project(request, project_id):
    if not request.user.is_staff:
        return redirect('home')

    project = Project.objects.get(id=project_id)
    project.delete()
    return redirect('admin_view')
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm
from .models import Project

# View for adding a new project
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new project
            return redirect('project_list')  # Redirect to a page (like a project list)
    else:
        form = ProjectForm()  # Empty form for GET request

    return render(request, 'add_project.html', {'form': form})

# View for editing an existing project
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)  # Get the project by primary key (pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()  # Save the updated project
            return redirect('project_list')  # Redirect after saving the changes
    else:
        form = ProjectForm(instance=project)  # Pre-populate the form with existing data

    return render(request, 'edit_project.html', {'form': form})
