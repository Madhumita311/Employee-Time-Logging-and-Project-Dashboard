from django.urls import path
from timetrackapp.forms import CustomLoginForm
from timetrackapp import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(form_class=CustomLoginForm), name='login'),
    path('home/', views.home, name='home'),

    # path('accounts/login/', auth_views.LoginView.as_view(form_class=CustomLoginForm, redirect_authenticated_user=True), name='login'),
# path('accounts/login/', auth_views.LoginView.as_view(form_class=CustomLoginForm, redirect_authenticated_user=True), name='login'),
    # path('accounts/login/home/', views.home, name='home'), 
    path('admin/', admin.site.urls),
    # path('signup/', views.signup, name='signup'),
    path('start_work/<int:project_id>/', views.start_work, name='start_work'),
    path('work_started/<int:work_hour_id>/', views.work_started, name='work_started'),
     path('project_switched/<int:project_id>/', views.project_switched, name='project_switched'),
    path('stop_work/<int:work_hour_id>/', views.stop_work, name='stop_work'),
    path('admin/', views.admin_view, name='admin_view'),
    path('add_project/', views.add_project, name='add_project'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'), 
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('switch_project/', views.switch_project, name='switch_project'),

    # path('signup/', views.signup, name='signup'),
   
]
