from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.utils import formats
from django.contrib import messages
from django.contrib.auth import logout
from datetime import datetime
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import QuestionForm, ChoiceFormSet
from .forms import (
    EmployeeRegisterForm,
    LanguageCourseForm,
    RefugeeRegistrationForm,
    LanguageTestForm,
    LanguageForm
)
from .models import Employee, User, Refugee, LanguageTest, Question, Choice, UserAnswer, LanguageCourse, Language
from .decorators import admin_required, employee_required, admin_or_employee_required
import pandas as pd
from django.shortcuts import get_object_or_404, redirect
from .models import LanguageTest, Refugee, Question, Choice, UserAnswer
from datetime import datetime


# REFUGEES
def home(request, user_role):
    courses = LanguageCourse.objects.all()
    context = {
        "user_role": user_role,
        "courses": courses, 
    }
    return render(request, "refugees/home.html", context)


def refugee_registration_view(request, user_role):
    if request.method == "POST":
        form = RefugeeRegistrationForm(request.POST)
        if form.is_valid():
            refugee_data = form.cleaned_data
            refugee_data["dob"] = refugee_data["dob"].strftime("%Y-%m-%d")
            refugee_data["language_id"] = refugee_data["language"].id
            del refugee_data["language"]

            request.session["refugee_data"] = refugee_data
            return redirect("language_test")
    else:
        form = RefugeeRegistrationForm()

    context = {
        "form": form,
        "user_role": user_role,
    }
    return render(request, "refugees/form.html", context)




def language_test_view(request, user_role):
    refugee_data = request.session.get("refugee_data")
    if not refugee_data:
        return redirect("refugee_registration")
    language_id = refugee_data.get("language_id")
    language = get_object_or_404(Language, id=language_id)
    test = get_object_or_404(LanguageTest, language=language, is_current=True)
    questions = test.questions.all()
    if request.method == "POST":
        answers = {}
        for question in questions:
            if question.question_type == "choice":
                selected_choice_id = request.POST.get(f"question_{question.id}")
                answers[question.id] = selected_choice_id
            elif question.question_type == "open":
                open_answer = request.POST.get(f"question_{question.id}")
                answers[question.id] = open_answer
        request.session["test_answers"] = answers
        if refugee_data:
            refugee_data["dob"] = datetime.strptime(refugee_data["dob"], "%Y-%m-%d").date()
            refugee = Refugee.objects.create(**refugee_data)
            for question_id, answer in answers.items():
                question = Question.objects.get(id=question_id)
                if question.question_type == "choice":
                    selected_choice = Choice.objects.get(id=answer)
                    awarded_points = question.max_points if selected_choice.is_correct else 0
                    UserAnswer.objects.create(
                        refugee=refugee,
                        question=question,
                        choice=selected_choice,
                        awarded_points=awarded_points
                    )
                else:
                    UserAnswer.objects.create(
                        refugee=refugee,
                        question=question,
                        text_answer=answer
                    )

            request.session.pop("refugee_data", None)
            request.session.pop("test_answers", None)

            return redirect("success_view")

    context = {
        "questions": questions,
        "user_role": user_role,
    }
    return render(request, "refugees/language_test.html", context)




def success_view(request, user_role):
    context = {
        "user_role": user_role,
    }
    return render(request, "refugees/success.html", context)


@csrf_protect
def login_view(request, user_role):
    context = {
        "user_role": user_role,
    }
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            try:
                employee = Employee.objects.get(user=user)
                if employee.is_admin:
                    return redirect("/systemadmin")
                else:
                    return redirect("/employee")
            except Employee.DoesNotExist:
                messages.error(request, "User does not have an associated profile.")
                return redirect("/login")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "refugees/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")


# EMPLOYEE AND ADMIN
@login_required
@admin_or_employee_required
def form_management_section(request, user_role):
    if request.method == "POST":
        selected_test_id = request.POST.get("current_test")
        if selected_test_id:
            test = LanguageTest.objects.get(pk=selected_test_id)
            LanguageTest.objects.filter(language=test.language).update(is_current=False)
            test.is_current = True
            test.save()
    languages = Language.objects.prefetch_related('languagetest_set').all()
    context = {
        "user_role": user_role,
        "languages": languages,
    }
    return render(request, "admin_and_employee/ae_frm_man_sec.html", context)


@login_required
@admin_or_employee_required
def set_current_test(request, test_id, user_role):
    try:
        LanguageTest.objects.update(is_current=False)
        test = LanguageTest.objects.get(pk=test_id)
        test.is_current = True
        test.save()
        messages.success(
            request, f"Test '{test.title}' został ustawiony jako aktualny."
        )
    except LanguageTest.DoesNotExist:
        messages.error(request, "Wybrany test nie istnieje.")
    return redirect("frm_man_sec")


@login_required
@admin_or_employee_required
def test_check_view(request, test_id, user_role):
    test = LanguageTest.objects.get(pk=test_id)
    refugees = Refugee.objects.filter(useranswer__question__test=test).distinct()
    refugee_data = []
    total_max_points = Question.objects.filter(test=test).aggregate(total_max=Sum('max_points'))['total_max'] or 0
    total_questions = test.questions.count()
    for refugee in refugees:
        total_points = UserAnswer.objects.filter(
            refugee=refugee, 
            question__test=test
        ).aggregate(total_awarded_points=Sum('awarded_points'))['total_awarded_points'] or 0
        checked_tasks = UserAnswer.objects.filter(
            refugee=refugee, 
            question__test=test,
            awarded_points__isnull=False
        ).count()
        answers = UserAnswer.objects.filter(refugee=refugee, question__test=test).select_related('question')
        refugee_data.append({
            'refugee': refugee,
            'total_points': total_points,
            'checked_tasks': checked_tasks,
            'total_tasks': total_questions,
            'answers': answers 
        })
    context = {
        "user_role": user_role,
        "test": test,
        "refugee_data": refugee_data,
        "total_max_points": total_max_points,
    }
    return render(request, "admin_and_employee/ae_filled_tests.html", context)

@login_required
@admin_or_employee_required
def save_points(request, user_role):
    if request.method == 'POST':
        test_id = request.POST.get('test_id') 
        for key, value in request.POST.items():
            if key.startswith('points_'):
                try:
                    answer_id = key.split('_')[1]
                    points = float(value)
                    user_answer = UserAnswer.objects.get(pk=answer_id)
                    user_answer.awarded_points = points
                    user_answer.save()
                except (ValueError, UserAnswer.DoesNotExist):
                    pass
        return redirect('test_check', test_id=test_id, user_role=user_role)



@login_required
@admin_or_employee_required
def create_test_view(request, user_role):
    if request.method == "POST":
        form = LanguageTestForm(request.POST)
        if form.is_valid():
            test = form.save()
            return redirect("frm_man_sec")
    else:
        form = LanguageTestForm()
    context = {"user_role": user_role, "form": form}
    return render(request, "admin_and_employee/ae_create_test.html", context)


@login_required
@admin_or_employee_required
def delete_test(request, user_role, id):
    test = get_object_or_404(LanguageTest, id=id)
    test.delete()
    return redirect("/systemadmin/form-management")


@login_required
@admin_or_employee_required
def edit_test(request, user_role, id):
    test = get_object_or_404(LanguageTest, id=id)
    if request.method == "POST":
        if "add_open_question" in request.POST:
            text = request.POST.get("open_question_text")
            if text:
                Question.objects.create(test=test, text=text, question_type="open")
                return redirect("edit_test", id=id)
        elif "add_choice_question" in request.POST:
            text = request.POST.get("choice_question_text")
            answers = request.POST.getlist("answer_text")
            correct_answers = request.POST.getlist("is_correct")
            if text and answers:
                question = Question.objects.create(
                    test=test, text=text, question_type="choice"
                )
                for idx, answer_text in enumerate(answers):
                    if str(idx) in correct_answers:
                        is_correct = True
                    else:
                        is_correct = False
                    Choice.objects.create(
                        question=question, text=answer_text, is_correct=is_correct
                    )
                return redirect("edit_test", id=id)
        elif "update_question" in request.POST:
            question_id = request.POST.get("question_id")
            question = get_object_or_404(Question, id=question_id)
            question.text = request.POST.get("updated_question_text")
            question.save()
            return redirect("edit_test", id=id)
        elif "delete_question" in request.POST:
            question_id = request.POST.get("question_id")
            question = get_object_or_404(Question, id=question_id)
            question.delete()
            return redirect("edit_test", id=id)
        elif "question_id" in request.POST and "max_points" in request.POST:
            question_id = request.POST.get("question_id")
            max_points = request.POST.get("max_points")
            question = get_object_or_404(Question, id=question_id)
            question.max_points = max_points
            question.save()
            return redirect("edit_test", id=id)
    questions = test.questions.prefetch_related("choices").all()
    context = {"user_role": user_role, "test": test, "questions": questions}
    return render(request, "admin_and_employee/ae_edit_test.html", context)


# EMPLOYEE
@login_required
@employee_required
def employee(request, user_role):
    context = {
        "user_role": user_role,
    }
    return render(request, "admin_and_employee/e.html", context)


# ADMIN
@login_required
@admin_required
def systemadmin(request, user_role):
    context = {
        'user_role': user_role,
        }
    return render(request, 'admin_and_employee/a.html', context)


@login_required
@admin_required
def register(request, user_role):
    if request.method == "POST":
        form = EmployeeRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Konto zostało utworzone")
            return redirect("/systemadmin/employee-management")
    else:
        form = EmployeeRegisterForm()
    context = {
        "navbar_title": "JRS Admin",
        "form": form,
        "user_role": user_role,
    }
    return render(request, "admin_and_employee/a_register.html", context)


@login_required
@admin_required
def employee_management_section(request, user_role):
    employees = Employee.objects.all()
    context = {
        "employees": employees,
        "user_role": user_role,
    }
    return render(request, "admin_and_employee/a_emp_man_sec.html", context)


@login_required
@admin_required
def courses_management_section(request, user_role):
    course_id = request.POST.get('course_id')
    if course_id:
        course = get_object_or_404(LanguageCourse, id=course_id)
        form = LanguageCourseForm(request.POST, instance=course)
    else:
        form = LanguageCourseForm(request.POST or None)
    language_form = LanguageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('crs_man_sec')
    if request.method == "POST" and language_form.is_valid():
        language_form.save()
        return redirect('crs_man_sec')
    if request.GET.get('edit'):
        course = get_object_or_404(LanguageCourse, id=request.GET.get('edit'))
        form = LanguageCourseForm(instance=course)
    if request.GET.get('delete'):
        course_to_delete = get_object_or_404(LanguageCourse, id=request.GET.get('delete'))
        course_to_delete.delete()
        return redirect('crs_man_sec')
    if request.GET.get('delete_language'):
        language_to_delete = get_object_or_404(Language, id=request.GET.get('delete_language'))
        language_to_delete.delete()
        return redirect('crs_man_sec')
    courses = LanguageCourse.objects.all()
    languages = Language.objects.all()
    context = {
        "user_role": user_role,
        "form": form,
        "language_form": language_form, 
        "courses": courses,
        "languages": languages,
    }
    return render(request, "admin_and_employee/a_crs_man_sec.html", context)

@login_required
@admin_required
def delete_employee(request, email):
    user = get_object_or_404(User, email=email)
    employee = get_object_or_404(Employee, user=user)
    employee.delete()
    user.delete()
    return redirect("/systemadmin/employee-management")

@login_required
@admin_required
def delete_refugee_view(request, refugee_id, user_role):
    refugee = get_object_or_404(Refugee, id=refugee_id)
    refugee.delete()
    context = {"user_role": user_role}
    return redirect(refugees_list_view)


@login_required
@admin_required
def refugees_list_view(request, user_role):
    refugees = Refugee.objects.all()
    context = {"user_role": user_role, "refugees": refugees}
    return render(request, "admin_and_employee/a_refugees_list.html", context)
