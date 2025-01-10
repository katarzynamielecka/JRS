from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
import random
import requests
from django.contrib.auth import authenticate, login
from django.utils import formats
from googletrans import Translator
from django.db import transaction
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth import logout
import csv
from django.db.models import Subquery, OuterRef, Min
from datetime import datetime
from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from django.db.models import Sum, Q
from datetime import timedelta
import datetime
from django.http import HttpResponse
from datetime import time
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .utils import genetic_algorithm_schedule
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from .forms import (
    EmployeeRegisterForm,
    LanguageCourseForm,
    RefugeeRegistrationForm,
    LanguageTestForm,
    LanguageForm,
    RecruitmentForm,
    AttendanceFormSet
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
    CourseTestThreshold,
    FilledTest,
    Recruitment,
    Attendance,

)
from .decorators import admin_required, employee_required, admin_or_employee_required
from django.shortcuts import get_object_or_404, redirect
from .models import LanguageTest, Refugee, Question, Choice, UserAnswer
from datetime import datetime
from django.http import HttpResponseNotFound


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def test_404(request):
    return render(request, '404.html')

# REFUGEES

def get_user_language(request):
    lang = request.GET.get('lang')
    if lang:
        request.session['lang'] = lang
    else:
        lang = request.session.get('lang', 'en')
    return lang


def home(request, user_role):
    active_recruitment = Recruitment.objects.filter(
        active=True
    ).first()
    if not active_recruitment:
        return redirect("no_registration")
    if active_recruitment and active_recruitment.semester:
        active_semester = active_recruitment.semester
        earliest_semesters = LanguageCourse.objects.filter(
            id=OuterRef('id')
        ).values('semesters__start_date').order_by('semesters__start_date')[:1]
        courses = LanguageCourse.objects.annotate(
            earliest_semester=Subquery(earliest_semesters)
        ).filter(
            earliest_semester=active_semester.start_date
        )
    else:
        courses = LanguageCourse.objects.none()
    lang = get_user_language(request)
    original_texts = {
        'welcome_message': "Welcome to Our Language Register Platform",
        'goal': (
            "Our goal is to provide language courses for refugees to help them integrate, "
            "communicate and build a better future. Our courses are designed to suit a variety "
            "of skill levels, from beginner to advanced, and are tailored to the unique needs of our students."
        ),
        'available_courses': "Available Courses",
        'no_courses': "No courses available at the moment.",
        'important_info': "Important information",
        'info_details': (
            "Please note that registration for any of our courses requires the purchase of specific textbooks "
            "and materials, which are necessary to fully participate and succeed in the program. By enrolling, "
            "you commit to attending all classes and completing assignments. We strive to make these resources "
            "as affordable as possible and are here to support you every step of the way."
        ),
        'how_to_register': "How to Register?",
        'register_instructions': "Click on the 'Register Now' button to start your journey with us.",
        'register_now': "Register Now",
    }
    translator = Translator()
    try:
        translated_texts = {
            key: translator.translate(text, dest=lang).text
            for key, text in original_texts.items()
        }
    except Exception:
        translated_texts = original_texts
    context = {
        "user_role": user_role,
        "courses": courses,
        "translated_texts": translated_texts,
        "lang": lang,
    }
    return render(request, "refugees/home.html", context)



def no_registration_view(request, user_role):
    translator = Translator()
    lang = get_user_language(request)
    active_recruitment = Recruitment.objects.filter(active=True).exists()
    if active_recruitment:
        return redirect("home", user_role=user_role)
    upcoming_recruitments = Recruitment.objects.filter(
        start_date__gt=now().date()
    ).order_by("start_date")[:3]
    original_texts = {
        'no_active_registration': "No Active Registration",
        'no_active_registration_message': "Currently, there is no active registration available.",
        'upcoming_recruitments': "Upcoming Recruitments",
        'no_upcoming_recruitments': "There are no upcoming recruitments scheduled at this time.",
        'start_date': "Start Date",
        'end_date': "End Date",
        'semester': "Semester",
    }
    translated_texts = {}
    for key, text in original_texts.items():
        if text:
            try:
                translated_texts[key] = translator.translate(text, dest=lang).text
            except Exception as e:
                print(f"Błąd tłumaczenia dla '{key}': {e}")
                translated_texts[key] = text 
    context = {
        "user_role": user_role,
        "upcoming_recruitments": upcoming_recruitments,
        "translated_texts": translated_texts, 
        "lang": lang,
    }
    return render(request, "refugees/no_registration.html", context)

def refugee_registration_view(request, user_role):
    translator = Translator()
    lang = get_user_language(request)
    recaptcha_lang = get_recaptcha_lang(lang)
    if request.method == "POST":
        form = RefugeeRegistrationForm(request.POST, lang=lang)
        if form.is_valid():
            # Pobranie odpowiedzi z reCAPTCHA
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not validate_recaptcha(recaptcha_response):
                print('nie przeszło')
                form.add_error(None, 'Invalid reCAPTCHA. Please try again.')
                return render(request, "refugees/form.html", {'form': form, 'user_role': user_role, 'lang': lang})
            
            # Jeżeli wszystko jest poprawne, zapisujemy dane i przechodzimy do następnego kroku
            refugee_data = form.cleaned_data
            refugee_data["language_id"] = refugee_data["language"].id
            del refugee_data["language"]

            request.session["refugee_data"] = refugee_data
            return redirect("language_test")
    else:
        form = RefugeeRegistrationForm(lang=lang)
    original_texts = {
        'registration_title': "Registration Form",
        'next_button': "Next",
    }
    translated_texts = {}
    for key, text in original_texts.items():
        if text: 
            try:
                translated_texts[key] = translator.translate(text, dest=lang).text 
            except Exception as e:
                translated_texts[key] = original_texts[key]
    context = {
        "form": form,
        "user_role": user_role,
        "translated_texts": translated_texts,
        "lang": lang,
        "recaptcha_lang": recaptcha_lang 
    }
    return render(request, "refugees/form.html", context)

def get_recaptcha_lang(lang):
    supported_languages = ['en', 'pl', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'ja'] 
    return lang if lang in supported_languages else 'en' 


def validate_recaptcha(recaptcha_response):
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    secret_key = settings.RECAPTCHA_SECRET_KEY
    payload = {
        'secret': secret_key,
        'response': recaptcha_response,
    }
    response = requests.post(recaptcha_url, data=payload)
    result = response.json()

    print("ReCAPTCHA Response:", recaptcha_response)
    print("Google API Payload:", payload)
    print("Google API Result:", result)

    return result.get('success', False)


def language_test_view(request, user_role):
    translator = Translator()
    lang = get_user_language(request)
    refugee_data = request.session.get("refugee_data")
    if not refugee_data:
        return redirect("home")
    recruitment = Recruitment.objects.filter(active=True).first()
    if not recruitment:
        return redirect("no_recruitment")
    language_id = refugee_data.get("language_id")
    language = get_object_or_404(Language, id=language_id)
    test = recruitment.language_tests.filter(language=language).first()
    if not test:
        return redirect("no_recruitment")  
    questions = test.questions.filter(
        Q(question_type="open") | Q(question_type="choice", choices__isnull=False)
    ).distinct()
    original_texts = {
        'language_test': "Language Test",
    }
    translated_texts = {}
    for key, text in original_texts.items():
        if text: 
            try:
                translated_texts[key] = translator.translate(text, dest=lang).text 
            except Exception as e:
                translated_texts[key] = original_texts[key]
    if request.method == "POST":
        answers = {}
        total_points = 0
        refugee = None
        for question in questions:
            if question.question_type == "choice":
                selected_choice_id = request.POST.get(f"question_{question.id}")
                answers[question.id] = selected_choice_id
            elif question.question_type == "open":
                open_answer = request.POST.get(f"question_{question.id}")
                answers[question.id] = open_answer
        if refugee_data:
            refugee = Refugee.objects.create(**refugee_data)
            filled_test = FilledTest.objects.create(
                refugee=refugee,
                test=test,
                recruitment=recruitment
            )
            for question_id, answer in answers.items():
                question = Question.objects.get(id=question_id)
                if question.question_type == "choice":
                    selected_choice = Choice.objects.get(id=answer)
                    awarded_points = (
                        question.max_points if selected_choice.is_correct else 0
                    )
                    total_points += awarded_points
                    UserAnswer.objects.create(
                        question=question,
                        choice=selected_choice,
                        awarded_points=awarded_points,
                        filled_test=filled_test
                    )
                else:
                    UserAnswer.objects.create(
                        question=question,
                        text_answer=answer,
                        filled_test=filled_test
                    )
            filled_test.total_points = total_points
            filled_test.save()
            request.session.pop("refugee_data", None)
            request.session.pop("test_answers", None)
            return redirect("success_view")
    context = {
        "questions": questions,
        "user_role": user_role,
        "translated_texts": translated_texts,
    }
    return render(request, "refugees/language_test.html", context)



def success_view(request, user_role):
    translator = Translator()
    lang = get_user_language(request)
    try:
        success_message = translator.translate("Your registration was successful. We have sent a confirmation email to your address.", dest=lang).text
        instructions_message = translator.translate("Check your inbox for further instructions.", dest=lang).text
        contact_message = translator.translate("If you have any questions, ", dest=lang).text
        contact_link = translator.translate("contact us.", dest=lang).text
    except Exception as e:
        success_message = "Your registration was successful. We have sent a confirmation email to your address."
        instructions_message = "Check your inbox for further instructions."
        contact_message = "If you have any questions, "
        contact_link = "contact us."
    context = {
        "user_role": user_role,
        "success_message": success_message,
        "instructions_message": instructions_message,
        "contact_message": contact_message,
        "contact_link": contact_link,
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
    languages = Language.objects.prefetch_related("languagetest_set").all()
    last_active_recruitment = Recruitment.objects.filter(
        activated_at__isnull=False
    ).order_by('-activated_at').first()
    last_recruitment_tests = []
    if last_active_recruitment:
        last_recruitment_tests = (
            LanguageTest.objects
            .filter(recruitments=last_active_recruitment)
            .select_related('language')
        )
    context = {
        "user_role": user_role,
        "languages": languages,
        "last_recruitment": last_active_recruitment,
        "last_recruitment_tests": last_recruitment_tests,
    }
    return render(request, "admin_and_employee/ae_frm_man_sec.html", context)


@login_required
@admin_or_employee_required
def test_check_view(request, test_id, user_role):
    test = LanguageTest.objects.get(pk=test_id)
    filled_tests = FilledTest.objects.filter(test=test).select_related("refugee", "recruitment")
    refugee_data = []
    for filled_test in filled_tests:
        refugee = filled_test.refugee
        filled_test_id = filled_test.id
        total_points = filled_test.total_points
        answers = filled_test.user_answers.all()
        max_points = (
            answers.aggregate(total_max=Sum("max_points"))["total_max"] or 0
        )
        checked_tasks = answers.filter(awarded_points__isnull=False).count()
        refugee_data.append(
            {
                "filled_test": filled_test_id,
                "recruitment_name": filled_test.recruitment.name,
                "refugee": refugee,
                "total_points": total_points,
                "checked_tasks": checked_tasks,
                "total_tasks": answers.count(),
                "answers": answers,
                "max_points": max_points,
            }
        )
    grouped_data = {}
    for key, group in groupby(sorted(refugee_data, key=itemgetter("recruitment_name")), key=itemgetter("recruitment_name")):
        grouped_data[key] = list(group)
    context = {
        "user_role": user_role,
        "test": test,
        "grouped_data": grouped_data,
    }
    return render(request, "admin_and_employee/ae_filled_tests.html", context)


@login_required
@admin_or_employee_required
def save_points(request, user_role):
    if request.method == "POST":
        test_id = request.POST.get("test_id")
        filled_test_id = request.POST.get("filled_test_id")
        try:
            filled_test = FilledTest.objects.get(id=filled_test_id)
        except FilledTest.DoesNotExist:
            return HttpResponseNotFound("Filled Test not found")
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
            filled_test.calculate_total_points()
        if user_role == "admin":
            return redirect("test_check", test_id=test_id, user_role=user_role)
        else:
            return redirect("test_check_employee", test_id=test_id, user_role=user_role)

        

@login_required
@admin_required
def assignment_to_courses(request, test_id, recruitment_name, user_role):
    test = LanguageTest.objects.get(pk=test_id)
    recruitment = Recruitment.objects.get(name = recruitment_name)
    filled_tests = FilledTest.objects.filter(test=test, recruitment=recruitment).select_related("refugee", "recruitment")
    courses = recruitment.get_courses().filter(language=test.language)
    course_data = []
    for course in courses:
        threshold = CourseTestThreshold.objects.filter(course=course, test=test).first()
        refugees_with_scores = []
        filled_tests_in_course = FilledTest.objects.filter(
            test=test, refugee__in=course.refugees.all(), recruitment=recruitment
        ).select_related("refugee")
        for filled_test in filled_tests_in_course:
            answers = filled_test.user_answers.all()
            max_points = (
                answers.aggregate(total_max=Sum("max_points"))["total_max"] or 0
            )
            filled_test.calculate_total_points()
            refugees_with_scores.append({
                "refugee": filled_test.refugee,
                "test_score": filled_test.total_points,
                "max_points": max_points,
                "is_slavic": filled_test.refugee.is_slavic_speaker() 
            })
        course_data.append({
            "course": course,
            "min_points": threshold.min_points if threshold else None,
            "max_points": threshold.max_points if threshold else None,
            "refugees_with_scores": refugees_with_scores,
            "is_slavic": course.is_slavic,
        })
        unassigned_refugees = Refugee.objects.filter(
        courses=None, language=test.language,
        completed_tests__recruitment=recruitment
        ).distinct()

        unassigned_refugees_data = []
        for refugee in unassigned_refugees:
            filled_test = FilledTest.objects.filter(
                test=test, refugee=refugee, recruitment=recruitment
            ).first()

            if filled_test:
                filled_test.calculate_total_points()
                unassigned_refugees_data.append({
                    "refugee": refugee,
                    "test_score": filled_test.total_points,
                    "is_slavic": refugee.is_slavic_speaker(),
                })
    if request.method == "POST":
        if request.POST.get("remove_course"):
            refugee_id = request.POST.get("refugee_id")
            course_id = request.POST.get("course_id")

            refugee = get_object_or_404(Refugee, id=refugee_id)
            course = get_object_or_404(LanguageCourse, id=course_id)
            refugee.courses.remove(course)
            return redirect(request.path)

        if request.POST.get("change_course"):
            refugee_id = request.POST.get("refugee_id")
            new_course_id = request.POST.get("new_course_id")
            refugee = get_object_or_404(Refugee, id=refugee_id)
            new_course = get_object_or_404(LanguageCourse, id=new_course_id)
            refugee.courses.clear()
            refugee.courses.add(new_course)
            return redirect(request.path)
        else:
            course_id = request.POST.get("course_id")
            test_id = request.POST.get("test_id")
            min_points = request.POST.get("min_points")
            max_points = request.POST.get("max_points")
            course = get_object_or_404(LanguageCourse, id=course_id)
            test = get_object_or_404(LanguageTest, id=test_id)
            try:
                min_points = int(min_points) if min_points else None
                max_points = int(max_points) if max_points else None
                if min_points is not None and max_points is not None and min_points > max_points:
                    messages.error(request, "Minimalna liczba punktów nie może być większa niż maksymalna.")
                    return redirect(request.path)

                overlapping_thresholds = CourseTestThreshold.objects.filter(test=test, recruitment=recruitment, course__is_slavic=course.is_slavic).exclude(course=course)

                for threshold in overlapping_thresholds:
                    if not (
                        (max_points is not None and threshold.min_points is not None and max_points <= threshold.min_points) or
                        (min_points is not None and threshold.max_points is not None and min_points >= threshold.max_points)
                    ):
                        messages.error(
                            request,
                            f"Przedziały punktowe nakładają się z kursem: {threshold.course.name} ({threshold.min_points}-{threshold.max_points} pkt)."
                        )
                        return redirect(request.path)

                threshold, created = CourseTestThreshold.objects.get_or_create(course=course, recruitment=recruitment, test=test)
                threshold.min_points = min_points
                threshold.max_points = max_points
                threshold.save()
                refugees = Refugee.objects.filter(
                    completed_tests__test=test,
                    completed_tests__recruitment=recruitment 
                ).distinct()

                for refugee in refugees:
                    assignment_function(refugee, test, recruitment)
            except ValueError:
                messages.error(request, "Wprowadź poprawne wartości liczby punktów.")
            return redirect(request.path)
    context = {
    "user_role": user_role,
    "courses": courses,
    "course_data": course_data,
    "test": test,
    "unassigned_refugees_data": unassigned_refugees_data,
    }
    return render(request, "admin_and_employee/a_assignment_to_courses.html", context)


def assignment_function(refugee, test, recruitment):
    filled_test = FilledTest.objects.filter(refugee=refugee, test=test, recruitment=recruitment).first()
    if not filled_test:
        return None
    filled_test.calculate_total_points()
    total_ref_points = filled_test.total_points
    thresholds = CourseTestThreshold.objects.filter(test=test, recruitment=recruitment)
    refugee.courses.clear()
    assigned = False
    for threshold in thresholds:
        course = threshold.course
        if course.is_slavic:
            if refugee.is_slavic_speaker() and threshold.min_points <= total_ref_points < threshold.max_points:
                refugee.courses.add(course)
                assigned = True
            elif refugee.is_slavic_speaker() and threshold.min_points == total_ref_points == threshold.max_points:
                refugee.courses.add(course)
                assigned = True
        else:
            if not refugee.is_slavic_speaker() and threshold.min_points <= total_ref_points < threshold.max_points:
                refugee.courses.add(course)
                assigned = True
            elif not refugee.is_slavic_speaker() and threshold.min_points == total_ref_points == threshold.max_points:
                refugee.courses.add(course)
                assigned = True

    return assigned


@login_required
@admin_required
def recruitment_management(request, user_role):
    for recruitment in Recruitment.objects.all():
        recruitment.update_active_status()
    form = RecruitmentForm()
    if request.method == "POST":
        if "finish_recruitment" in request.POST:
            recruitment_id = request.POST.get("recruitment_id")
            recruitment = get_object_or_404(Recruitment, id=recruitment_id)
            recruitment.active = False
            recruitment.manually_closed = True
            recruitment.save()
            return redirect('recruitment_management', user_role=user_role)
        elif "resume_recruitment" in request.POST:
            recruitment_id = request.POST.get("recruitment_id")
            recruitment = get_object_or_404(Recruitment, id=recruitment_id)
            if recruitment.start_date <= now().date() <= recruitment.end_date:
                overlapping_recruitments = Recruitment.objects.filter(
                    active=True,
                    start_date__lte=recruitment.end_date,
                    end_date__gte=recruitment.start_date
                ).exclude(id=recruitment.id)  

                if overlapping_recruitments.exists():
                    messages.error(request, "Nie możesz wznowić rekrutacji, ponieważ istnieje już aktywna rekrutacja w tym okresie.")
                else:
                    recruitment.active = True
                    recruitment.manually_closed = False
                    recruitment.save()
            return redirect('recruitment_management', user_role=user_role)
        elif "delete" in request.POST:
            recruitment_id = request.POST.get("recruitment_id")
            recruitment = get_object_or_404(Recruitment, id=recruitment_id)
            recruitment.delete()
            return redirect('recruitment_management', user_role=user_role)
        elif "add_recruitment" in request.POST:
            form = RecruitmentForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                active = form.cleaned_data.get('active', False)
                overlapping_recruitments = Recruitment.objects.filter(
                    active=True,
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )

                if overlapping_recruitments.exists():
                    form.add_error(None, "Istnieje już aktywna rekrutacja w tym okresie.")
                else:
                    form.save()  
                    form = RecruitmentForm() 
            else:
                messages.error(request, "Wystąpił błąd w formularzu.")
            return redirect('recruitment_management', user_role=user_role)
    
    recruitments = Recruitment.objects.all().order_by('-start_date')
    for r in recruitments:
        print(f"Rekrutacja: {r.name}, Testy: {[t.id for t in r.language_tests.all()]}")

    context = {
        "user_role": user_role,
        "form": form,
        "recruitments": recruitments,
    }
    return render(request, "admin_and_employee/a_recruitment_management.html", context)


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
    overlapping_recruitments = Recruitment.objects.filter(
        active=True,
        language_tests=test,
        start_date__lte=now().date(),
        end_date__gte=now().date()
    )

    if overlapping_recruitments.exists():
        messages.error(
            request, 
            "Nie możesz edytować tego testu, ponieważ jest używany w aktywnej rekrutacji."
        )
        return redirect("frm_man_sec") 
    if request.method == "POST":
        if "add_open_question" in request.POST:
            text = request.POST.get("open_question_text")
            if text:
                Question.objects.create(test=test, text=text, question_type="open")
                if user_role == "admin":
                    return redirect("edit_test", id=id)
                else:
                    return redirect("edit_test_employee", id=id)
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
                if user_role == "admin":
                    return redirect("edit_test", id=id)
                else:
                    return redirect("edit_test_employee", id=id)

        elif "update_question" in request.POST:
            question_id = request.POST.get("question_id")
            question = get_object_or_404(Question, id=question_id)
            question.text = request.POST.get("updated_question_text")
            question.save()
            if user_role == "admin":
                return redirect("edit_test", id=id)
            else:
                return redirect("edit_test_employee", id=id)
        elif "delete_question" in request.POST:
            question_id = request.POST.get("question_id")
            question = get_object_or_404(Question, id=question_id)
            question.delete()
            if user_role == "admin":
                return redirect("edit_test", id=id)
            else:
                return redirect("edit_test_employee", id=id)
        elif "question_id" in request.POST and "max_points" in request.POST:
            question_id = request.POST.get("question_id")
            max_points = request.POST.get("max_points")
            question = get_object_or_404(Question, id=question_id)
            question.max_points = max_points
            question.save()
            if user_role == "admin":
                return redirect("edit_test", id=id)
            else:
                return redirect("edit_test_employee", id=id)
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
@login_required
@admin_required
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
    
@login_required
@admin_required
def handle_language_form(request):
    language_form = LanguageForm(request.POST or None)
    if language_form.is_valid():
        language_form.save()
        return True
    return language_form

@login_required
@admin_required
def handle_course_deletion(request):
    course_id = request.GET.get("delete")
    if course_id:
        course_to_delete = get_object_or_404(LanguageCourse, id=course_id)
        course_to_delete.delete()
        return True
    return False

@login_required
@admin_required
def handle_language_deletion(request):
    language_id = request.GET.get("delete_language")
    if language_id:
        language_to_delete = get_object_or_404(Language, id=language_id)
        language_to_delete.delete()
        return True
    return False

@login_required
@admin_required
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

@login_required
@admin_required
def handle_weekly_classes_update(request):
    course_id = request.POST.get("course_id")
    weekly_classes = request.POST.get("weekly_classes")
    if course_id and weekly_classes and weekly_classes.isdigit():
        course = get_object_or_404(LanguageCourse, id=course_id)
        course.weekly_classes = int(weekly_classes)
        course.save()
        return True
    return False

@login_required
@admin_required
def handle_semester_deletion(request):
    semester_id = request.POST.get("semester_id")
    if request.POST.get("delete_semester") and semester_id:
        semester = get_object_or_404(Semester, id=semester_id)
        semester.delete()
        return True
    return False

@login_required
@admin_required
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

@login_required
@admin_required
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
@admin_required
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
def delete_employee(request, user_role, email):
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

@login_required
@admin_required
def generate_timetable(request, user_role):
    ClassSchedule.objects.all().delete()
    best_schedule, conflicts = genetic_algorithm_schedule(population_size=50, generations=100)
    for schedule in best_schedule:
        course = schedule[0] 
        teacher = schedule[4] 
        course.teacher = teacher
        course.save() 
        ClassSchedule.objects.create(
            course=schedule[0],            # Kurs
            day=schedule[1],               # Dzień
            time_interval=schedule[2],     # Interwał czasu
            classroom=schedule[3],         # Sala
            teacher=schedule[4],           # Nauczyciel
            conflicts=conflicts,
        )
    return redirect("timetable", user_role=user_role)

@login_required
@admin_required
def handle_schedule_update(request):
    """Obsługuje AJAX-owe aktualizacje planu w modelu ClassSchedule."""
    if request.method != "POST":
        return JsonResponse({"error": "Metoda żądania musi być POST."}, status=405)

    try:
        data = json.loads(request.body)  
        lesson_id = data.get("lesson_id")
        new_day = data.get("day")
        classroom_id = data.get("classroom_id")
        teacher_id = data.get("teacher_id")
        new_interval_id = data.get("interval_id")
        schedule = ClassSchedule.objects.get(id=lesson_id)

        if new_day:
            schedule.day = new_day
        if new_interval_id:
            schedule.time_interval_id = new_interval_id

        
        if classroom_id is not None:
            schedule.classroom_id = classroom_id
        if teacher_id is not None:
            schedule.teacher_id = teacher_id
            course = schedule.course
            course.teacher = schedule.teacher
            course.save()
        schedule.save()

        return JsonResponse({"success": True, "message": "Plan zaktualizowany pomyślnie."})

    except ClassSchedule.DoesNotExist:
        return JsonResponse({"error": "Lekcja o podanym ID nie istnieje."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Wystąpił błąd: {str(e)}"}, status=400)


DAY_MAPPING = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
}

def generate_course_dates(start_date, end_date, weekday):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == weekday:
            dates.append(current_date)
        current_date += timedelta(days=1)
    return dates

@login_required
@admin_or_employee_required
def attendance_view(request, user_role):
    user = request.user
    try: 
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        employee = None
    current_semesters = Semester.get_current_semesters()
    schedules = ClassSchedule.objects.filter(
        teacher=employee, 
        course__semesters__in=current_semesters
    ).distinct()
    for schedule in schedules:
        semester = schedule.course.semesters.first()
        weekday = DAY_MAPPING[schedule.day]
        schedule.dates = generate_course_dates(
            semester.start_date, semester.end_date, weekday
        )
    context = {
        "user_role": user_role, 
        "schedules": schedules,
    }
    return render(request, "admin_and_employee/e_attendance.html", context)

@login_required
@admin_or_employee_required
def mark_attendance(request, user_role, schedule_id, date):
    schedule = get_object_or_404(ClassSchedule, id=schedule_id)
    refugees = schedule.course.refugees.all()
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Nieprawidłowy format daty!", status=400)
    for refugee in refugees:
        Attendance.objects.get_or_create(schedule=schedule, date=selected_date, refugee=refugee)
    attendance_queryset = Attendance.objects.filter(schedule=schedule, date=selected_date)
    if request.method == "POST":
        formset = AttendanceFormSet(request.POST, queryset=attendance_queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Obecności zostały zapisane.")
            return redirect("mark_attendance", schedule_id=schedule_id, date=selected_date)
    else:
        formset = AttendanceFormSet(queryset=attendance_queryset)
    context = {
        "user_role": user_role,
        "schedule": schedule,
        "refugees": refugees,
        "formset": formset,
    }
    return render(request, "admin_and_employee/e_mark_attendance.html", context)

@login_required
@admin_required
def export_courses_csv(request, user_role):
    courses = LanguageCourse.objects.prefetch_related('semesters').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nazwa', 'Opis', 'Semestr', 'Email_nauczyciela'])
    for course in courses:
        semesters = course.semesters.all() 
        for semester in semesters:
            teacher = course.teacher.user.email if course.teacher else ""
            writer.writerow([course.name, course.description, semester.name, teacher])
    return response

@login_required
@admin_required
def export_refugees_csv(request, user_role):
    refugees = Refugee.objects.prefetch_related('courses')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="refugees.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['nazwa kursu', 'nazwa semestru', 'imie', 'nazwisko', 'telefon', 'mail', 'czy_pelnoletni', 'plec', 'kraj', 'cecha charakterystyczna', 'opis'])
    for refugee in refugees:
        for course in refugee.courses.all():
            first_semester = course.semesters.order_by('start_date').first()
            semester_name = first_semester.name if first_semester else "brak"
            gender = refugee.gender
            if gender == 'female':
                gender = 'kobieta'
            elif gender == 'male':
                gender = 'mężczyzna'
            age=''
            if refugee.is_adult == True:
                age='pełnoletni'
            else:
                age='niepełnoletni'
            writer.writerow([
                course.name,
                semester_name,
                refugee.first_name,
                refugee.last_name,
                refugee.phone_number,
                refugee.email,
                age,
                gender,
                refugee.get_nationality_name(),
                '',
                ''
            ])
    return response

@login_required
@admin_required
def export_employees_csv(request, user_role):
    employees = Employee.objects.select_related('user').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employees.csv"'
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['lp', 'imie', 'nazwisko', 'telefon', 'mail', 'plec', 'kraj', 'cecha charakterystyczna', 'opis'])
    
    for employee in employees:
        writer.writerow([
            '',
            employee.user.first_name,
            employee.user.last_name,
            '',  # Telefon (brak w modelu Employee)
            employee.user.email,
            '',  # Płeć (brak w modelu Employee)
            '',  # Kraj (brak w modelu Employee)
            '',  # Cecha charakterystyczna (brak w modelu Employee)
            ''  # Opis (brak w modelu Employee)
        ])
    context = {
        "user_role": user_role,
    }
    return response



