from django.urls import path
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, {'user_role': 'refugee'}, name="home"),
    path('form/', views.form, {'user_role': 'refugee'}, name="form"),
    path('employee/', views.employee, {'user_role': 'employee'}, name="employee"),
    path('systemadmin/', views.systemadmin, {'user_role': 'admin'}, name="systemadmin"), 
    path('login/', views.login_view, {'user_role': 'refugee'}, name="login"),
    path('register/', views.register, {'user_role': 'admin'}, name="register"),
    path('systemadmin/employee-management', views.employee_management_section, {'user_role': 'admin'}, name='emp_man_sec'),
    path('systemadmin/courses-management', views.courses_management_section, {'user_role': 'admin'}, name='crs_man_sec'),
    path('systemadmin/form-management', views.form_management_section, {'user_role': 'admin'}, name='frm_man_sec'),
    path('systemadmin/refugees', views.refugees_list_view, {'user_role': 'admin'}, name='refugee_list'),
    path('delete_employee/<str:email>/', views.delete_employee, {'user_role': 'admin'}, name='delete_employee'),
    path('systemadmin/delete_test/<int:id>/', views.delete_test, {'user_role': 'admin'}, name='delete_test'),
    path('systemadmin/edit_test/<int:id>/', views.edit_test, {'user_role': 'admin'}, name='edit_test'),
    path('systemadmin/create-test/', views.create_test_view, {'user_role': 'admin'}, name='create_test'),
    path('employee/form-management', views.form_management_section, {'user_role': 'employee'}, name='frm_man_sec_employee'),
    path('employee/edit_test/<int:id>/', views.edit_test, {'user_role': 'employee'}, name='edit_test_employee'),
    path('employee/create-test/', views.create_test_view, {'user_role': 'employee'}, name='create_test_employee'),
    path('logout/', views.logout_view, name='logout')
]
