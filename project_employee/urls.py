# from django.urls import path
from timetrackapp.forms import CustomLoginForm
from timetrackapp import views
from django.contrib import admin
from timetrackapp.views import weekly_hours_view
from django.contrib.auth import views as auth_views
# urlpatterns = [

#     path('', views.signup, name='signup'),
#      path('accounts/login/', auth_views.LoginView.as_view(form_class=CustomLoginForm), name='login'),
#     path('home/', views.home, name='home'),
#     path('goal', views.goal_list, name='goal_list'),
#     path('create/', views.create_goal, name='create_goal'),
#     path('daily_update/<int:goal_id>/', views.daily_update, name='daily_update'),
#     path('weekly_hours_view/', views.weekly_hours_view, name=''), 
#    path('my-admin-page/', views.my_admin_page, name='my_admin_page'),
#     path('admin/', admin.site.urls),
#     path('start_work/<int:project_id>/', views.start_work, name='start_work'),
#     path('work_started/<int:work_hour_id>/', views.work_started, name='work_started'),
#     # path('add-weekly-goals/', views.add_weekly_goals, name='add_weekly_goals'),
#     # path('update-goal/<int:goal_id>/', views.update_goal_status, name='update_goal_status'),
#     path('switch_project/', views.switch_project, name='switch_project'),
#     path('project_switched/<int:project_id>/', views.project_switched, name='project_switched'),
#     path('stop_work/<int:work_hour_id>/', views.stop_work, name='stop_work'),
#     path('admin/', views.admin_view, name='admin_view'),
#     path('add_project/', views.add_project, name='add_project'),
#     path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
#     path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'), 
#     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
# ]
from django.urls import path
from timetrackapp import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth paths
    path('', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(form_class=CustomLoginForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Home and goal management paths
    path('home/', views.home, name='home'),
    path('goal', views.goal_list, name='goal_list'),
    path('start_work/<int:project_id>/', views.start_work, name='start_work'),  # Start work on a project
    
    # path('create/', views.create_goal, name='create_goal'),
    path('create/<int:project_id>/', views.create_goal, name='create_goal'),
   
    path('daily_update/<int:goal_id>/', views.daily_update, name='daily_update'),
    path('work_started/<int:work_hour_id>/', views.work_started, name='work_started'),
    path('add-weekly-goals/', views.add_weekly_goals, name='add_weekly_goals'),

    # Project work tracking
    # path('start_work/<int:project_id>/', views.start_work, name='start_work'),  # Start work on a project
    path('stop_work/<int:work_hour_id>/', views.stop_work, name='stop_work'),  # Stop work and log time
    path('switch_project/', views.switch_project, name='switch_project'),
    path('project_switched/<int:project_id>/', views.project_switched, name='project_switched'),

    # Admin paths
    path('admin/', admin.site.urls),
    path('add_project/', views.add_project, name='add_project'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('my-admin-page/', views.my_admin_page, name='my_admin_page'),
]
