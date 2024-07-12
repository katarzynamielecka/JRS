from django.urls import path
from . import views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('employee/', views.employee, name="employee"),
    path('systemadmin/', views.systemadmin, name="systemadmin"), 
    path('login/', views.login_view, name="login"),
    path('register/', views.register, name="register"),
    path('upload/', views.upload_form, name='upload_file'),
    path('success/', lambda request: render(request, 'success.html'), name='success'),
]