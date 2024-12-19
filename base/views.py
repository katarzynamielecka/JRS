from django.shortcuts import render, redirect, get_object_or_404
import random
from django.contrib.auth import authenticate, login
from django.utils import formats
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import logout
from datetime import datetime
from collections import defaultdict
from django.db.models import Sum, Q
from datetime import time
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .utils import genetic_algorithm_schedule
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from .forms import QuestionForm, ChoiceFormSet
from .forms import (
    EmployeeRegisterForm,
    LanguageCourseForm,
    RefugeeRegistrationForm,
    LanguageTestForm,
    LanguageForm,
)
from .models import (
    Employee,
    User,
    Refugee,
    LanguageTest,
    Question,
    Choice,
    UserAnswer,
    LanguageCourse,
    Language,
    TimeInterval,
    Classroom,
    Availability,
    ClassSchedule,
    Semester,
)
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
    questions = test.questions.filter(
        Q(question_type="open") | Q(question_type="choice", choices__isnull=False)
    ).distinct()

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
            refugee_data["dob"] = datetime.strptime(
                refugee_data["dob"], "%Y-%m-%d"
            ).date()
            refugee = Refugee.objects.create(**refugee_data)
            for question_id, answer in answers.items():
                question = Question.objects.get(id=question_id)
                if question.question_type == "choice":
                    selected_choice = Choice.objects.get(id=answer)
                    awarded_points = (
                        question.max_points if selected_choice.is_correct else 0
                    )
                    UserAnswer.objects.create(
                        refugee=refugee,
                        question=question,
                        choice=selected_choice,
                        awarded_points=awarded_points,
                    )
                else:
                    UserAnswer.objects.create(
                        refugee=refugee, question=question, text_answer=answer
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
                messages.error(request, "Nie ma takiego użytkownika.")
                return redirect("/login")
        else:
            messages.error(request, "Niepoprawny email lub hasło.")
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
    languages = Language.objects.prefetch_related("languagetest_set").all()
    context = {
        "user_role": user_role,
        "languages": languages,
    }
    return render(request, "admin_and_employee/ae_frm_man_sec.html", context)


@login_required
@admin_required
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
    total_max_points = (
        Question.objects.filter(test=test).aggregate(total_max=Sum("max_points"))[
            "total_max"
        ]
        or 0
    )
    total_questions = test.questions.count()
    for refugee in refugees:
        total_points = (
            UserAnswer.objects.filter(refugee=refugee, question__test=test).aggregate(
                total_awarded_points=Sum("awarded_points")
            )["total_awarded_points"]
            or 0
        )
        checked_tasks = UserAnswer.objects.filter(
            refugee=refugee, question__test=test, awarded_points__isnull=False
        ).count()
        answers = UserAnswer.objects.filter(
            refugee=refugee, question__test=test
        ).select_related("question")
        refugee_data.append(
            {
                "refugee": refugee,
                "total_points": total_points,
                "checked_tasks": checked_tasks,
                "total_tasks": total_questions,
                "answers": answers,
            }
        )
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
    if request.method == "POST":
        test_id = request.POST.get("test_id")
        for key, value in request.POST.items():
            if key.startswith("points_"):
                try:
                    answer_id = key.split("_")[1]
                    points = float(value)
                    user_answer = UserAnswer.objects.get(pk=answer_id)
                    user_answer.awarded_points = points
                    user_answer.save()
                except (ValueError, UserAnswer.DoesNotExist):
                    pass
        return redirect("test_check", test_id=test_id, user_role=user_role)


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
@admin_required
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
        if "add_choice_question" in request.POST:
            text = request.POST.get("choice_question_text")
            answers = request.POST.getlist("answer_text")
            correct_answers = request.POST.getlist("is_correct")
            if text and answers:
                question = Question.objects.create(
                    test=test, text=text, question_type="choice"
                )
                for idx, answer_text in enumerate(answers):
                    is_correct = str(idx) in correct_answers
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
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    intervals = list(TimeInterval.objects.all())
    lessons = ClassSchedule.objects.select_related(
        "time_interval", "classroom", "teacher", "course"
    )
    timetable = []
    for interval in intervals:
        interval_data = {"interval": interval, "days": []}
        for day in days:
            day_lessons = lessons.filter(
                day=day, 
                time_interval=interval
            ).values(
                "course__name", 
                "teacher__user__last_name", 
                "classroom__name", 
                "time_interval__start_time", 
                "time_interval__end_time",
            )
            interval_data["days"].append({"day": day, "lessons": list(day_lessons)})
        timetable.append(interval_data)
    context = {
        "user_role": user_role,
        "timetable": timetable,
    }
    return render(request, "admin_and_employee/a.html", context)


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


# courses management
def handle_course_form(request):
    course_id = request.POST.get("course_id")
    if course_id:
        course = get_object_or_404(LanguageCourse, id=course_id)
        form = LanguageCourseForm(request.POST, instance=course)
    else:
        form = LanguageCourseForm(request.POST or None)

    if form.is_valid():
        form.save()
        return form, None
    else:
        return form, form.errors

def handle_language_form(request):
    language_form = LanguageForm(request.POST or None)
    if language_form.is_valid():
        language_form.save()
        return True
    return language_form

def handle_course_deletion(request):
    course_id = request.GET.get("delete")
    if course_id:
        course_to_delete = get_object_or_404(LanguageCourse, id=course_id)
        course_to_delete.delete()
        return True
    return False

def handle_language_deletion(request):
    language_id = request.GET.get("delete_language")
    if language_id:
        language_to_delete = get_object_or_404(Language, id=language_id)
        language_to_delete.delete()
        return True
    return False

def handle_teacher_assignment(request):
    course_id = request.POST.get("course_id")
    if "teachers" in request.POST and course_id:
        course = get_object_or_404(LanguageCourse, id=course_id)
        teacher_ids = request.POST.getlist("teachers")
        employees = Employee.objects.filter(id__in=teacher_ids)
        for employee in Employee.objects.all():
            if employee in employees:
                employee.courses.add(course)
            else:
                employee.courses.remove(course)
        return True
    return False

def handle_weekly_classes_update(request):
    course_id = request.POST.get("course_id")
    weekly_classes = request.POST.get("weekly_classes")
    if course_id and weekly_classes and weekly_classes.isdigit():
        course = get_object_or_404(LanguageCourse, id=course_id)
        course.weekly_classes = int(weekly_classes)
        course.save()
        return True
    return False

def handle_semester_deletion(request):
    semester_id = request.POST.get("semester_id")
    if request.POST.get("delete_semester") and semester_id:
        semester = get_object_or_404(Semester, id=semester_id)
        semester.delete()
        return True
    return False

def handle_semester_update(request):
    semester_id = request.POST.get("semester_id")
    name = request.POST.get("semester_name")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    if semester_id and name and start_date and end_date:
        semester = get_object_or_404(Semester, id=semester_id)
        semester.name = name
        semester.start_date = start_date
        semester.end_date = end_date
        semester.save()
        return True
    return False

def handle_new_semester_creation(request):
    name = request.POST.get("semester_name")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    if name and start_date and end_date:
        Semester.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        return True
    return False

@login_required
def courses_management_section(request, user_role):
    if request.method == "POST":
        if request.POST.get("form_type") == "course_form":
            form, errors = handle_course_form(request)
            if not errors:
                return redirect("crs_man_sec")
        elif request.POST.get("form_type") == "language_form":
            language_form, errors = handle_language_form(request)
            if not errors:
                return redirect("crs_man_sec")
        elif handle_teacher_assignment(request):
            return redirect("crs_man_sec")
        elif handle_weekly_classes_update(request):
            return redirect("crs_man_sec")
        elif handle_semester_deletion(request):
            return redirect("crs_man_sec")
        elif handle_semester_update(request):
            return redirect("crs_man_sec")
        elif handle_new_semester_creation(request):
            return redirect("crs_man_sec")

    elif request.method == "GET":
        if handle_course_deletion(request):
            return redirect("crs_man_sec")
        elif handle_language_deletion(request):
            return redirect("crs_man_sec")

    form = LanguageCourseForm()
    language_form = LanguageForm()
    if request.GET.get("edit"):
        course = get_object_or_404(LanguageCourse, id=request.GET.get("edit"))
        form = LanguageCourseForm(instance=course)


    context = {
        "user_role": user_role,
        "form": form,
        "language_form": language_form,
        "courses": LanguageCourse.objects.all().order_by('name'),
        "languages": Language.objects.all(),
        "employees": Employee.objects.all(),
        "semesters": Semester.objects.all(),
        "cur_semesters": Semester.get_current_semesters(),
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


@login_required
@admin_required
def timetable_view(request, user_role,):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    availability = Availability.objects.prefetch_related("classrooms", "employees").all()
    intervals = list(TimeInterval.objects.all())
    classrooms = Classroom.objects.all()
    employees = Employee.objects.filter(courses__isnull=False).distinct()
    while len(intervals) < 12:
        intervals.append(None)
    availability_list = [
        {
            "day": a.day,
            "time_interval_id": a.time_interval_id,
            "classroom_id": classroom_id,
            "type": "classroom",
        }
        for a in availability
        for classroom_id in a.classrooms.values_list("id", flat=True)
    ] + [
        {
            "day": a.day,
            "time_interval_id": a.time_interval_id,
            "employee_id": employee_id,
            "type": "employee",
        }
        for a in availability
        for employee_id in a.employees.values_list("id", flat=True)
    ]
    lessons = ClassSchedule.objects.select_related(
        "time_interval", "classroom", "teacher", "course"
    )
    conflicts = lessons.first().conflicts if lessons.exists() else None
    timetable = []
    for interval in intervals:
        interval_data = {"interval": interval, "days": []}
        for day in days:
            day_lessons = lessons.filter(
                day=day, 
                time_interval=interval
            ).values(
                "id",
                "course__name", 
                "teacher__user__last_name", 
                "classroom__name", 
                "time_interval__start_time", 
                "time_interval__end_time",
            )
            interval_data["days"].append({"day": day, "lessons": list(day_lessons)})
        timetable.append(interval_data)
    if request.method == "POST":
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return handle_schedule_update(request)
        if "update_availability" in request.POST:
            print(request.POST)
            with transaction.atomic():
                for day in days:
                    for interval in intervals:
                        Availability.objects.filter(day=day, time_interval=interval).delete()
                for key, classroom_ids in request.POST.lists():
                    if key.startswith("availability-classroom-"):
                        _, _, day, interval_id = key.split("-", 3)
                        interval = get_object_or_404(TimeInterval, id=interval_id)
                        availability, _ = Availability.objects.get_or_create(
                            day=day, time_interval=interval
                        )
                        availability.classrooms.set(classroom_ids)
                        availability.save()
                for key, employee_ids in request.POST.lists():
                    if key.startswith("availability-employee-"):
                        _, _, day, interval_id = key.split("-", 3)
                        interval = get_object_or_404(TimeInterval, id=interval_id)
                        availability, _ = Availability.objects.get_or_create(
                            day=day, time_interval=interval
                        )
                        availability.employees.set(employee_ids)
                        availability.save()
            return redirect("timetable", user_role=user_role)

        if "add_edit_classroom" in request.POST:
            classroom_id = request.POST.get("classroom_id")
            name = request.POST.get("name")
            if name:
                if classroom_id:
                    classroom = get_object_or_404(Classroom, id=classroom_id)
                    classroom.name = name
                    classroom.save()
                else:
                    Classroom.objects.create(name=name)
            return redirect("timetable", user_role=user_role)
        if "delete_classroom" in request.POST:
            classroom_id = request.POST.get("classroom_id")
            if classroom_id:
                classroom = get_object_or_404(Classroom, id=classroom_id)
                classroom.delete()
            return redirect("timetable", user_role=user_role)

        if "update_intervals" in request.POST:
            start_times = request.POST.getlist("startTime[]")
            end_times = request.POST.getlist("endTime[]")
            TimeInterval.objects.all().delete()
            for start, end in zip(start_times, end_times):
                if start and end and start != "--:--" and end != "--:--":
                    TimeInterval.objects.create(start_time=start, end_time=end)
            return redirect("timetable", user_role=user_role)
    print(conflicts)
    context = {
        "days": days,
        "timetable": timetable,
        "user_role": user_role,
        "intervals": intervals,
        "classrooms": classrooms,
        "availability_list": availability_list,
        "employees": employees,
        "conflicts": conflicts,
        "cur_semesters": Semester.get_current_semesters(),
    }
    return render(request, "admin_and_employee/a_timetable.html", context)


def generate_timetable(request, user_role):
    ClassSchedule.objects.all().delete()
    best_schedule, conflicts = genetic_algorithm_schedule(population_size=50, generations=100)
    for schedule in best_schedule:
        ClassSchedule.objects.create(
            course=schedule[0],            # Kurs
            day=schedule[1],               # Dzień
            time_interval=schedule[2],     # Interwał czasu
            classroom=schedule[3],         # Sala
            teacher=schedule[4],           # Nauczyciel
            conflicts=conflicts,
        )
    return redirect("timetable", user_role=user_role)


def handle_schedule_update(request):
    """Obsługuje AJAX-owe aktualizacje planu w modelu ClassSchedule."""
    if request.method != "POST":
        return JsonResponse({"error": "Metoda żądania musi być POST."}, status=405)

    try:
        data = json.loads(request.body)  # Wczytaj dane JSON z żądania
        lesson_id = data.get("lesson_id")
        new_day = data.get("day")
        classroom_id = data.get("classroom_id")
        teacher_id = data.get("teacher_id")
        new_interval_id = data.get("interval_id")

        # Pobierz rekord ClassSchedule
        schedule = ClassSchedule.objects.get(id=lesson_id)

        # Aktualizacja dnia i interwału czasu
        if new_day:
            schedule.day = new_day
        if new_interval_id:
            schedule.time_interval_id = new_interval_id

        # Aktualizacja sali i nauczyciela (jeśli podano)
        if classroom_id is not None:
            schedule.classroom_id = classroom_id
        if teacher_id is not None:
            schedule.teacher_id = teacher_id

        # Zapisz zmiany
        schedule.save()

        return JsonResponse({"success": True, "message": "Plan zaktualizowany pomyślnie."})

    except ClassSchedule.DoesNotExist:
        return JsonResponse({"error": "Lekcja o podanym ID nie istnieje."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Wystąpił błąd: {str(e)}"}, status=400)
