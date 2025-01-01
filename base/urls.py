from django.urls import path
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

handler404 = views.custom_404_view 

urlpatterns = [
    path("", views.home, {"user_role": "refugee"}, name="home"),
    path("no_registration/", views.no_registration_view, {"user_role": "refugee"}, name="no_registration"),
    path(
        "form/", views.refugee_registration_view, {"user_role": "refugee"}, name="form"
    ),
    path(
        "language_test/",
        views.language_test_view,
        {"user_role": "refugee"},
        name="language_test",
    ),
    path("success/", views.success_view, {"user_role": "refugee"}, name="success_view"),
    path("employee/", views.employee, {"user_role": "employee"}, name="employee"),
    path("systemadmin/", views.systemadmin, {"user_role": "admin"}, name="systemadmin"),
    path("login/", views.login_view, {"user_role": "refugee"}, name="login"),
    path("register/", views.register, {"user_role": "admin"}, name="register"),
    path(
        "systemadmin/employee-management",
        views.employee_management_section,
        {"user_role": "admin"},
        name="emp_man_sec",
    ),
    path(
        "systemadmin/courses-management",
        views.courses_management_section,
        {"user_role": "admin"},
        name="crs_man_sec",
    ),
    path(
        "systemadmin/form-management",
        views.form_management_section,
        {"user_role": "admin"},
        name="frm_man_sec",
    ),
    path(
        "systemadmin/refugees",
        views.refugees_list_view,
        {"user_role": "admin"},
        name="refugee_list",
    ),
    path(
        "refugee/delete/<int:refugee_id>/",
        views.delete_refugee_view,
        {"user_role": "admin"},
        name="delete_refugee",
    ),
    path(
        "delete_employee/<str:email>/",
        views.delete_employee,
        {"user_role": "admin"},
        name="delete_employee",
    ),
    path(
        "systemadmin/delete_test/<int:id>/",
        views.delete_test,
        {"user_role": "admin"},
        name="delete_test",
    ),
    path(
        "systemadmin/edit_test/<int:id>/",
        views.edit_test,
        {"user_role": "admin"},
        name="edit_test",
    ),
    path(
        "systemadmin/create-test/",
        views.create_test_view,
        {"user_role": "admin"},
        name="create_test",
    ),
    path(
        "systemadmin/test-check/<int:test_id>/",
        views.test_check_view,
        {"user_role": "admin"},
        name="test_check",
    ),
    path(
        "systemadmin/save_points/",
        views.save_points,
        {"user_role": "admin"},
        name="save_points",
    ),
    path( "systemadmin/assignment_to_courses/<int:test_id>/<str:recruitment_name>/", views.assignment_to_courses, {"user_role": "admin"}, name="assignment_to_courses"),
    path( "systemadmin/recruitment_management", views.recruitment_management, {"user_role": "admin"}, name="recruitment_management"),
    path(
        "systemadmin/timetable/",
        views.timetable_view,
        {"user_role": "admin"},
        name="timetable",
    ),
    path(
        "employee/form-management",
        views.form_management_section,
        {"user_role": "employee"},
        name="frm_man_sec_employee",
    ),
    path(
        "employee/test-check/<int:test_id>/",
        views.test_check_view,
        {"user_role": "employee"},
        name="test_check_employee",
    ),
    path(
        "employee/edit_test/<int:id>/",
        views.edit_test,
        {"user_role": "employee"},
        name="edit_test_employee",
    ),
    path(
        "employee/create-test/",
        views.create_test_view,
        {"user_role": "employee"},
        name="create_test_employee",
    ),
    path(
        "employee/courses-management",
        views.courses_management_section,
        {"user_role": "employee"},
        name="crs_man_sec_employee",
    ),
    path('systemadmin/generate-timetable/',  views.generate_timetable, {"user_role": "admin"}, name='generate_timetable'),
    path("logout/", views.logout_view, name="logout"),
]
