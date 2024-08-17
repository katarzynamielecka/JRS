from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Test, Question, Choice
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import UserRegisterForm, UploadFileForm
from .models import Profile
import pandas as pd


# REFUGEES

def home(request):
    context = {}
    return render(request, 'home.html', context)    

def form(request):
    questions = Question.objects.all()
    return render(request, 'form.html', {'questions': questions})    


# EMPLOYEE

def employee(request):
    context = {}
    return render(request, 'employee.html', context)

@csrf_protect
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            profile = Profile.objects.get(user__email=email)
            user = profile.user
            user = authenticate(request, username=user.username, password=password)
        except Profile.DoesNotExist:
            user = None
        if user is not None:
            login(request, user)
            if profile.function == 'admin':
                return redirect('/systemadmin')
            else:
                return redirect('/employee')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')

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
                return HttpResponseRedirect('/success/')  # Przekierowanie po sukcesie
            except ValueError as e:
                form.add_error('file', str(e))
    else:
        form = UploadFileForm()
    return render(request, 'upload_form.html', {'form': form})




# ADMIN

def systemadmin(request):
    context = {}
    return render(request, 'systemadmin.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            function = form.cleaned_data.get('function')
            Profile.objects.create(user=user, function=function)
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            if function == 'admin':
                return redirect('/systemadmin')
            else:
                return redirect('/employee')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def employee_managment_section(request):
    context = {}
    return render(request, 'admin_emp_man_sec.html', context)