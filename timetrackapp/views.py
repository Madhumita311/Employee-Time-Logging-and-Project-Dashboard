from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Project, WorkHour
from .forms import ProjectForm, WorkHourForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import CustomLoginForm
from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth import login, authenticate
from .models import Project
from django.utils.timezone import now
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

def custom_admin_page(request):
    projects = Project.objects.all()
    return render(request, 'my_admin_page.html', {'projects': projects})


def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                # Handle the next parameter for redirecting
                next_url = request.GET.get('project_list')  # Default to 'project_list' if no next parameter
                return redirect(next_url)
            else:
                messages.error(request, "Invalid login credentials")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})
# from django.contrib.auth.views import LoginView

# class CustomLoginView(LoginView):
#     def get_success_url(self):
#         next_url = self.request.GET.get('next', '/projects/')  # Default redirect if 'next' is not provided
#         return next_url

# def custom_login_view(request):
#     if request.method == 'POST':
#         form = CustomLoginForm(request=request, data=request.POST)
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             if user is not None:
#                 login(request, user)
#                 return redirect('project_list')  # Redirect to the home page or another page after login
#     else:
#         form = CustomLoginForm()

#     return render(request, 'login.html', {'form': form})
# # Home page with start button (logged in user)
@login_required
def home(request):
     # Debugging: Check if active_work_hours is Nonve Work Hours: {active_work_hours}")
    active_work_hours = WorkHour.objects.filter(user=request.user, stop_time__isnull=True).first()
    # if active_work_hours is None:
    #     print("No active work hours found.")
    # else:
    #     print(f"Active work hours ID: {active_work_hours.id}")

    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects, 'active_work_hours': active_work_hours})

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

@login_required
def start_work(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Check if there's an ongoing session for the user
    active_session = WorkHour.objects.filter(user=request.user, stop_time__isnull=True).first()
    if active_session:
        return redirect('home')  # Prevent starting a new session without stopping the current one

    if request.method == 'POST':
        work_hour = WorkHour(user=request.user, project=project, start_time=now())
        work_hour.save()
    return redirect('work_started', work_hour_id=work_hour.id)
from django.shortcuts import render, get_object_or_404
from .models import WorkHour

@login_required
def work_started(request, work_hour_id):
    work_hour = get_object_or_404(WorkHour, id=work_hour_id)
    return render(request, 'work_started.html', {
        'user': request.user,
        'project': work_hour.project,
    })

# @
@login_required
def stop_work(request, work_hour_id):
    work_hour = get_object_or_404(WorkHour, id=work_hour_id)

    if request.method == 'POST':
        stop_time = now()
        if stop_time < work_hour.start_time:
            messages.error(request, "Stop time cannot be earlier than start time.")
            return redirect('home')

        work_hour.stop_time = stop_time
        # Calculate total hours
        duration = work_hour.stop_time - work_hour.start_time
        work_hour.total_hours = duration.total_seconds() / 3600  # Convert to hours

        work_hour.save()
        messages.success(request, "Work session stopped successfully.")

    return redirect('home')
@login_required
def switch_project(request):
    # Get the list of all projects
    projects = Project.objects.all()

    if request.method == 'POST':
        # Get the selected project from the POST data
        selected_project = request.POST.get('project')
        if selected_project:
            request.session['current_project'] = selected_project  # Store the selected project in the session
            
            # Redirect to the confirmation page
            return redirect('project_switched', project_id=selected_project)
    
    return render(request, 'switch_project.html', {'projects': projects})

@login_required
def project_switched(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_switched.html', {
        'user': request.user,
        'project': project,
    })

# # Start and stop work on a project
# @login_required
# def start_work(request, project_id):
#     project = Project.objects.get(id=project_id)
#     if request.method == 'POST':
#         work_hour = WorkHour(user=request.user, project=project, start_time=datetime.now())
#         work_hour.save()
#     return redirect('home')

# @login_required
# def stop_work(request, work_hour_id):
#     work_hour = WorkHour.objects.get(id=work_hour_id)
#     if request.method == 'POST':
#         work_hour.stop_time = datetime.now()
#         work_hour.save()
#     return redirect('home')
# from django.utils.timezone import now
# from .models import WorkHour, Project

# def start_work(request, project_id):
#     project = Project.objects.get(id=project_id)
#     WorkHour.objects.create(user=request.user, project=project, start_time=now())
#     return redirect('home')

# def stop_work(request, work_hour_id):
#     work_hour = WorkHour.objects.get(id=work_hour_id)
#     work_hour.stop_time = now()
#     work_hour.calculate_total_hours()
#     return redirect('home')

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
# def edit_project(request, pk):
#     project = get_object_or_404(Project, pk=pk)  # Get the project by primary key (pk)
#     # Update the view function to accept 'project_id'
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()  # Save the updated project
            return redirect('project_list')  # Redirect after saving the changes
    else:
        form = ProjectForm(instance=project)  # Pre-populate the form with existing data

    return render(request, 'edit_project.html', {'form': form})


@login_required
def switch_project(request):
    current_project = request.session.get('current_project', None)
    projects = Project.objects.all()

    if request.method == 'POST':
        selected_project = request.POST.get('project')
        request.session['current_project'] = selected_project
        # Handle any time calculations here
        return redirect('home')  # Redirect to home or updated page

    return render(request, 'switch_project.html', {
        'current_project': current_project,
        'projects': projects,
    })
