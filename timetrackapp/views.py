from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from .models import Project, WorkHour, UserProjectHistory,Goal,DailyUpdate
from .forms import DailyUpdateForm, GoalForm, ProjectForm, WorkHourForm, CustomLoginForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
import matplotlib.pyplot as plt
import io,base64
def create_goal(request,project_id):
    project = get_object_or_404(Project, id=project_id)
    work_hour = WorkHour.objects.first()
    if request.method == 'POST':
        form = GoalForm(request.POST)
        # form.user = request.user  # Set user when initializing the form
        if form.is_valid():
            # Set the user to the logged-in user
            goal = form.save(commit=False)
            goal.user = request.user  # Ensure the user is set
            goal.project = project 
            form.save()
            return redirect('goal_list')  # Redirect on success
        else:
            print(form.errors)  # Print form errors to debug issues
    else:
        form = GoalForm()

    return render(request, 'creategoal.html', {'form': form,'project':project,'work_hour': work_hour})

def goal_list(request):
    project = Project.objects.first()
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'goals/goal_list.html', {'project': project,'goals': goals})


def daily_update(request, goal_id):
    # goal = Goal.objects.get(id=goal_id)
    goal = get_object_or_404(Goal, id=goal_id)  # Ensure that the goal exists
    project_id = goal.project.id
    if request.method == 'POST':
        form = DailyUpdateForm(request.POST)
        if form.is_valid():
            daily_update = form.save(commit=False)
            daily_update.goal = goal
            daily_update.date = timezone.now().date()
            if not DailyUpdate.objects.filter(goal=goal, date=daily_update.date).exists():
                daily_update.save()
            return redirect('start_work', project_id=project_id)
    else:
        form = DailyUpdateForm()
    return render(request, 'goals/daily_update.html', {'form': form, 'goal': goal})

def weekly_hours_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    today = timezone.now().date()

    # Calculate the start of the week (Monday) and the end of the work week (Friday)
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=4)  # Friday (4 days after Monday)

      # Calculate total weekly hours for the user
    total_weekly_hours = WorkHour.objects.filter(
        user=request.user,
        start_time__gte=start_of_week,
        start_time__lte=end_of_week
    ).aggregate(total_week_hours=Sum('total_hours'))['total_week_hours'] or 0

     # Aggregate hours by project
    project_hours = WorkHour.objects.filter(
        user=request.user,
        start_time__gte=start_of_week,
        start_time__lte=end_of_week
    ).values('project__name').annotate(total_hours=Sum('total_hours'))
# Prepare data for the graph
    project_names = [entry['project__name'] for entry in project_hours]
    hours = [entry['total_hours'] for entry in project_hours]

    # Generate the graph using Matplotlib
    plt.figure(figsize=(4, 6))
    plt.bar(project_names, hours, color=['#4A90E2', '#7ED321', '#F5A623', '#9B59B6', '#FF6F61', '#1ABC9C'])
    plt.xlabel('Projects')
    plt.ylabel('Hours Worked')
    plt.title(f'Weekly Hours for {request.user.username}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot as a Base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Render the template with total hours and the graph
    return render(request, 'weekly_hours.html', {
        'total_hours_worked': total_weekly_hours,
        'graph': graph_base64,
    })
   
def is_staff_user(user):
    return user.is_staff

# General views
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'project_list'))
            else:
                messages.error(request, "Invalid login credentials.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')  
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html',{'form':form})

# Work hour management
@login_required
def home(request):
    active_work_hours = WorkHour.objects.filter(user=request.user, stop_time__isnull=True).first()
    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects, 'active_work_hours': active_work_hours})

@login_required
def start_work(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    active_session = WorkHour.objects.filter(user=request.user, stop_time__isnull=True).first()

    if active_session:
        messages.warning(request, "Please stop the current session before starting a new one.")
        return redirect('home')  # Return early if there's an active session
        # Check if the user has goals before starting work
    goals = Goal.objects.filter(user=request.user, project=project)
    # if not goals.exists():
    #     messages.warning(request, "Please create a goal for this project first.")
    #     return redirect('create_goal',project_id=project_id)  # Redirect to the 'create_goal' page if no goal exists

    # Now we process the form only if there's no active session
    if request.method == 'POST':
        goal_form = GoalForm(request.POST,user=request.user)
        if goal_form.is_valid():  # Call is_valid() on the form instance
            goal, created = Goal.objects.get_or_create(
                user=request.user,
                project=project,
                defaults={'is_started': True, 'planned': goal_form.cleaned_data['planned']}
            )
            if not created:  # If the goal already existed, update it
                goal.is_started = True
                goal.planned = goal_form.cleaned_data['planned']
                goal.save()

            # Now, start the work hour session
            work_hour = WorkHour.objects.create(
                user=request.user,
                project=project,
                start_time=timezone.now()  # Assuming you have start_time in your WorkHour model
            )

            messages.success(request, "Work session started and goals set.")
            return redirect('work_started', work_hour_id=work_hour.id)
        # else:
            # messages.error(request, "There was an issue with the goal form.")
            # print(goal_form.errors)

    else:
        goal_form = GoalForm(user=request.user)

    return render(request, 'start_work.html', {'goal_form': goal_form, 'project': project})

    # return redirect('home')
@login_required
def stop_work(request, work_hour_id):
    work_hour = get_object_or_404(WorkHour, id=work_hour_id, user=request.user)

    if work_hour.stop_time:
        messages.error(request, "This session is already stopped.")
        return redirect('home')

    if request.method == 'POST':
        work_hour.stop_time = now()
        work_hour.total_hours = (work_hour.stop_time - work_hour.start_time).total_seconds() / 3600
        work_hour.save()

        # Update the corresponding goal if exists
        try:
            goal = Goal.objects.get(user=request.user, project=work_hour.project, is_started=True)
            goal.completed = request.POST.get('completed', goal.completed)
            goal.dependencies = request.POST.get('dependencies', goal.dependencies)
            goal.pending = request.POST.get('pending', goal.pending)
            goal.is_started = False
            goal.is_completed = True  # Mark as completed
            goal.save()
        except Goal.DoesNotExist:
            messages.warning(request, "No goal found for this project to update.")

        UserProjectHistory.objects.create(
            user=request.user,
            project=work_hour.project,
            start_time=work_hour.start_time,
            stop_time=work_hour.stop_time,
            total_hours=work_hour.total_hours
        )
        messages.success(request, "Work session stopped successfully and goals updated.")
    return redirect('home')

@login_required
def switch_project(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        selected_project = get_object_or_404(Project, id=request.POST.get('project'))
            # Stop the current active session
        active_work_hour = WorkHour.objects.filter(user=request.user, stop_time__isnull=True).first()
        if active_work_hour:
            active_work_hour.stop_time = now()
            active_work_hour.total_hours = (active_work_hour.stop_time - active_work_hour.start_time).total_seconds() / 3600
            active_work_hour.save()

            # Record the session in UserProjectHistory
            UserProjectHistory.objects.create(
                user=request.user,
                start_time=active_work_hour.start_time,
                stop_time=active_work_hour.stop_time,
                project=selected_project,
                total_hours=active_work_hour.total_hours,
            )

        # Start a new session for the selected project
        WorkHour.objects.create(user=request.user, project=selected_project, start_time=now())
        messages.success(request, f"Switched to project: {selected_project.name}")
        return redirect('home')

    return render(request, 'switch_project.html', {'projects': projects})

@login_required
def admin_view(request):
    if not is_staff_user(request.user):
        return redirect('home')
    projects = Project.objects.all()
    return render(request, 'admin_view.html', {'projects': projects})

@login_required
def add_project(request):
    if not is_staff_user(request.user):
        return redirect('home')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect('admin_view')
    return render(request, 'add_project.html', {'form': ProjectForm()})

@login_required
def edit_project(request, project_id):
    if not is_staff_user(request.user):
        return redirect('home')

    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('admin_view')
    return render(request, 'edit_project.html', {'form': ProjectForm(instance=project)})

@login_required
def delete_project(request, project_id):
    if not is_staff_user(request.user):
        return redirect('home')

    project = get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect('admin_view')

def my_admin_page(request):
    projects = Project.objects.all()
    return render(request, 'my_admin_page.html', {'projects': projects})

@login_required
def work_started(request, work_hour_id):
    work_hour = get_object_or_404(WorkHour, id=work_hour_id)
    return render(request, 'work_started.html', {
        'user': request.user,
        'project': work_hour.project,
    })

@login_required
def project_switched(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_switched.html', {
        'user': request.user,
        'project': project,
    })

@login_required
def add_weekly_goals(request):
    """Allow users to add planned goals only on Fridays."""
    if now().weekday() != 4:  # 4 = Friday
        messages.error(request, "You can only add weekly goals on Fridays.")
        return redirect('home')

    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal, created = Goal.objects.get_or_create(
                user=request.user,
                project=request.POST.get('project'),
                defaults={
                    'planned': form.cleaned_data['planned'],
                    'is_started': False,
                    'is_completed': False
                }
            )
            if not created:
                messages.warning(request, "Goals for this project have already been set.")
            messages.success(request, "Goals added successfully.")
            return redirect('home')

    form = GoalForm()
    projects = Project.objects.all()
    return render(request, 'add_weekly_goals.html', {'form': form, 'projects': projects})
@login_required
def update_goal_status(request, goal_id):
    """Allow users to update completed, dependencies, and pending goals any day."""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)

    if request.method == 'POST':
        goal.completed = request.POST.get('completed', goal.completed)
        goal.dependencies = request.POST.get('dependencies', goal.dependencies)
        goal.pending = request.POST.get('pending', goal.pending)
        goal.save()
        messages.success(request, "Goal updated successfully.")
        return redirect('home')

    return render(request, 'update_goal_status.html', {'goal': goal})
