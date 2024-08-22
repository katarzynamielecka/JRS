from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Test, Question, Choice
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import EmployeeRegisterForm, UploadFileForm
from .models import Employee, User
import pandas as pd


# REFUGEES

def home(request):
    context = {}
    return render(request, 'refugees/home.html', context)    

def form(request):
    questions = Question.objects.all()
    return render(request, 'refugees/form.html', {'questions': questions})    


# EMPLOYEE

def employee(request):
    context = {}
    return render(request, 'admin_and_employee/e.html', context)

@csrf_protect
def login_view(request):
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
    return render(request, 'refugees/login.html')

def handle_uploaded_form(f):
    Question.objects.all().delete()
    try:
        df = pd.read_excel(f)
    except Exception as e:
        raise ValueError("Nie można odczytać pliku Excel. Upewnij się, że plik jest poprawnie sformatowany.")
    if df.shape[1] < 1:
        raise ValueError("Plik Excel musi zawierać co najmniej jedną kolumnę.")
    for index, row in df.iterrows():
        if row.isnull().all():
            continue
        question_text = row[0]
        if pd.isnull(question_text) or question_text == "":
            continue
        answer_texts = row[1:].dropna().tolist()
        if answer_texts:
            question = Question.objects.create(text=question_text, question_type='multiple_choice')
            for answer_text in answer_texts:
                Choice.objects.create(question=question, text=answer_text)
        else:
            question = Question.objects.create(text=question_text, question_type='open')

def upload_form(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                handle_uploaded_form(request.FILES['file'])
                return HttpResponseRedirect('/success/')
            except ValueError as e:
                form.add_error('file', str(e))
    else:
        form = UploadFileForm()
    return render(request, 'admin_and_employee/ae_upload_form.html', {'form': form})




# ADMIN

def systemadmin(request):
    context = {}
    return render(request, 'admin_and_employee/a.html', context)

def register(request):
    if request.method == 'POST':
        form = EmployeeRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Konto zostało utworzone')
            return redirect('/systemadmin/employee-management')
    else:
        form = EmployeeRegisterForm()
    return render(request, 'admin_and_employee/a_register.html', {'form': form})


def employee_management_section(request):
    employees = Employee.objects.all()
    return render(request, 'admin_and_employee/a_emp_man_sec.html', {'employees': employees})

def form_management_section(request):
    context = {}
    return render(request, 'admin_and_employee/a_frm_man_sec.html', context)

def courses_management_section(request):
    context = {}
    return render(request, 'admin_and_employee/a_crs_man_sec.html', context)

@login_required
def delete_employee(request, email):
    user = get_object_or_404(User, email=email)
    employee = get_object_or_404(Employee, user=user)
    employee.delete()
    user.delete()
    return redirect('/systemadmin/employee-management')
