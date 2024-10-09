from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils import formats
from django.contrib import messages
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import QuestionForm, ChoiceFormSet
from .forms import EmployeeRegisterForm, UploadFileForm, RefugeeRegistrationForm, LanguageTestForm
from .models import Employee, User, Refugee, LanguageTest, Question, Choice
from .decorators import admin_required, employee_required
import pandas as pd


# REFUGEES

def home(request):
    context = {
        'navbar_title': 'JRS Registration for Language Courses',
        'role':'r'
    }
    return render(request, 'refugees/home.html', context)    

def form(request):
    test = get_object_or_404(LanguageTest, title="cur_test")
    questions = test.questions.all()  
    if request.method == 'POST':
        form = RefugeeRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RefugeeRegistrationForm()
    context = {
        'form': form,
        'questions': questions,
    }
    return render(request, 'refugees/form.html', context)

# EMPLOYEE
@login_required
@employee_required
def employee(request):
    context = {
        'navbar_title': 'JRS Employee',
        'role': 'e'
        }
    return render(request, 'admin_and_employee/e.html', context)

@csrf_protect
def login_view(request):
    context = {
        'navbar_title': 'JRS Registration for Language Courses',
        'role': 'a'
        }
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            try:
                employee = Employee.objects.get(user=user)
                if employee.is_admin:
                    return redirect('/systemadmin')
                else:
                    return redirect('/employee')
            except Employee.DoesNotExist:
                messages.error(request, 'User does not have an associated profile.')
                return redirect('/login')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'refugees/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')



# ADMIN
@admin_required
@login_required
def create_test_view(request):
    if request.method == 'POST':
        form = LanguageTestForm(request.POST)
        if form.is_valid():
            test = form.save()
            return redirect('frm_man_sec')
    else:
        form = LanguageTestForm()
    context = {
    'navbar_title': 'JRS Admin',
    'role': 'a',
    'form': form
    }
    return render(request, 'admin_and_employee/a_create_test.html', context)

@login_required
@admin_required
def delete_test(request, id):
    test = get_object_or_404(LanguageTest, id=id)
    test.delete()
    return redirect('/systemadmin/form-management')

@login_required
@admin_required
def edit_test(request, id):
    test = get_object_or_404(LanguageTest, id=id)
    if request.method == 'POST':
        if 'add_open_question' in request.POST:
            text = request.POST.get('open_question_text')
            if text:
                Question.objects.create(test=test, text=text, question_type='open')
                return redirect('edit_test', id=id)
        elif 'add_choice_question' in request.POST:
            text = request.POST.get('choice_question_text')
            if text:
                Question.objects.create(test=test, text=text, question_type='choice')
                return redirect('edit_test', id=id)
        elif 'add_choice_answer' in request.POST:
            question_id = request.POST.get('question_id')
            answer_text = request.POST.get('answer_text')
            is_correct = 'is_correct' in request.POST
            if question_id and answer_text:
                question = get_object_or_404(Question, id=question_id)
                Choice.objects.create(question=question, text=answer_text, is_correct=is_correct)
                return redirect('edit_test', id=id)
        elif 'delete_question' in request.POST:
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, id=question_id)
            question.delete()
            return redirect('edit_test', id=id)
    questions = test.questions.prefetch_related('choices').all()
    context = {
        'navbar_title': 'JRS Admin',
        'role': 'a',
        'test': test, 
        'questions': questions
    }
    return render(request, 'admin_and_employee/a_edit_test.html', context)

@login_required
@admin_required
def systemadmin(request):
    context = {
        'navbar_title': 'JRS Admin',
        'role': 'a'
        }
    return render(request, 'admin_and_employee/a.html', context)

@login_required
@admin_required
def register(request):
    if request.method == 'POST':
        form = EmployeeRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konto zostało utworzone')
            return redirect('/systemadmin/employee-management')
    else:
        form = EmployeeRegisterForm()
    context = {
    'navbar_title': 'JRS Admin',
    'form': form,
    'role': 'a'
    }
    return render(request, 'admin_and_employee/a_register.html', context)

@login_required
@admin_required
def employee_management_section(request):
    employees = Employee.objects.all()
    context = {
        'navbar_title': 'JRS Admin',
        'employees': employees,
        'role': 'a',
    }
    return render(request, 'admin_and_employee/a_emp_man_sec.html', context)

@login_required
@admin_required
def form_management_section(request):
    tests = LanguageTest.objects.all()
    context = {
        'navbar_title': 'JRS Admin',
        'role': 'a',
        'tests': tests,
        }
    return render(request, 'admin_and_employee/a_frm_man_sec.html', context)

@login_required
@admin_required
def courses_management_section(request):
    context = {
        'navbar_title': 'JRS Admin',
        'role': 'a'
        }
    return render(request, 'admin_and_employee/a_crs_man_sec.html', context)

@login_required
@admin_required
def delete_employee(request, email):
    user = get_object_or_404(User, email=email)
    employee = get_object_or_404(Employee, user=user)
    employee.delete()
    user.delete()
    return redirect('/systemadmin/employee-management')

@login_required
@admin_required
def refugees_list_view(request):
    refugees = Refugee.objects.all() 
    context = {
        'navbar_title': 'JRS Admin',
        'role': 'a',
        'refugees': refugees
        }
    return render(request, 'admin_and_employee/a_refugees_list.html', context)
