from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_countries.fields import CountryField


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class LanguageTest(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Semester(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    @classmethod
    def get_current_semesters(cls):
        today = now().date()
        return cls.objects.filter(start_date__lte=today, end_date__gte=today)

class Recruitment(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nazwa rekrutacji",  unique=True )
    start_date = models.DateField(verbose_name="Data rozpoczęcia")
    end_date = models.DateField(verbose_name="Data zakończenia")
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="recruitments",
        verbose_name="Na semestr",
        null=True
    )
    max_people = models.IntegerField(default=1000000, verbose_name="Maksymalna ilość zarekrutowanych osób")
    active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    manually_closed = models.BooleanField(default=False)
    language_tests = models.ManyToManyField(LanguageTest, related_name="recruitments", verbose_name="Testy językowe", blank=True)
    
    def update_active_status(self):
        if not self.manually_closed and self.start_date <= now().date() <= self.end_date:
            self.active = True
            if not self.activated_at: 
                self.activated_at = now()
        else:
            self.active = False
        self.save()

    @property
    def is_within_active_dates(self):
        today = now().date()
        return self.start_date <= today <= self.end_date
    
    def get_courses(self, language=None):
        courses = LanguageCourse.objects.filter(semesters=self.semester).prefetch_related("refugees")
        if language:
            courses = courses.filter(language=language)
        return courses
    
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    courses = models.ManyToManyField(
        "LanguageCourse", related_name="teachers", blank=True
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"




class Refugee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=[("female", "Female"), ("male", "Male"), ("other", "Other")],
    )
    dob = models.DateField()
    phone_number = models.CharField(max_length=15)
    nationality = CountryField(blank_label="Select country")
    residency = models.CharField(
        max_length=20,
        choices=[
            ("permanent", "Permanent"),
            ("temporary", "Temporary"),
            ("refugee", "Refugee"),
            ("other", "Other"),
        ],
    )
    rodo_consent = models.BooleanField(default=False)
    truth_confirmation = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    courses = models.ManyToManyField(
        "LanguageCourse", related_name="refugees", blank=True
    )

    SLOVIC_COUNTRIES = [
        "PL",  # Polska
        "CZ",  # Czechy
        "SK",  # Słowacja
        "RU",  # Rosja
        "BY",  # Białoruś
        "UA",  # Ukraina
        "RS",  # Serbia
        "HR",  # Chorwacja
        "BA",  # Bośnia i Hercegowina
        "ME",  # Czarnogóra
        "SI",  # Słowenia
        "MK",  # Macedonia Północna
        "BG",  # Bułgaria
    ]

    def is_slavic_speaker(self):
        return self.nationality.code in self.SLOVIC_COUNTRIES


    def get_nationality_name(self):
        return self.nationality.name

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Question(models.Model):
    QUESTION_TYPES = (
        ("open", "Otwarte"),
        ("choice", "Zamknięte"),
    )

    test = models.ForeignKey(
        LanguageTest, related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0)
    max_points = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class FilledTest(models.Model):
    refugee = models.ForeignKey(
        Refugee, on_delete=models.CASCADE, related_name="completed_tests"
    )
    test = models.ForeignKey(
        LanguageTest, on_delete=models.CASCADE, related_name="completed_tests"
    )
    recruitment = models.ForeignKey(
        Recruitment, on_delete=models.CASCADE, related_name="completed_tests"
    )
    total_points = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.refugee} - {self.test} ({self.recruitment.name})"

    def calculate_total_points(self):
        """
        Recalculate total points based on related UserAnswer objects.
        """
        total_points = UserAnswer.objects.filter(filled_test=self).aggregate(
            models.Sum("awarded_points")
        )["awarded_points__sum"] or 0.0
        self.total_points = total_points
        self.save()

    

class UserAnswer(models.Model):
    filled_test = models.ForeignKey(
        FilledTest,
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name="Completed Test",
        null=True, blank=True
    )
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.SET_NULL)
    choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    choice_text = models.TextField(null=True, blank=True) 
    text_answer = models.TextField(null=True, blank=True)
    awarded_points = models.FloatField(null=True, blank=True)
    question_text = models.TextField(null=True, blank=True) 
    max_points = models.FloatField(default=1.0)

    def __str__(self):
        return f"Answer to {self.question} in {self.completed_test}"

    def copy_question_data(self):
        if self.question:
            self.question_text = self.question.text
            self.question_type = self.question.question_type
            self.max_points = self.question.max_points
        if self.choice:
            self.choice_text = self.choice.text

    def save(self, *args, **kwargs):
        if not self.pk:
            self.copy_question_data()
        super().save(*args, **kwargs)



class TimeInterval(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    available_classrooms = models.ManyToManyField(
        "Classroom", blank=True, verbose_name="Dostępne sale"
        # czy to potrzebne tu? nie dodaje do modelu !!!!!!!!!!!!!!!!!!!!!!!
    )

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

    class Meta:
        ordering = ["start_time"]
        verbose_name = "Przedział godzinowy"
        verbose_name_plural = "Przedziały godzinowe"


class LanguageCourse(models.Model):
    name = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    weekly_classes = models.PositiveIntegerField(default=1)
    semesters = models.ManyToManyField(Semester, related_name="courses")
    is_slavic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.language})"

class CourseTestThreshold(models.Model):
    course = models.ForeignKey(LanguageCourse, on_delete=models.CASCADE, related_name="test_thresholds")
    test = models.ForeignKey(LanguageTest, on_delete=models.CASCADE)
    min_points = models.PositiveIntegerField(null=True, blank=True)
    max_points = models.PositiveIntegerField(null=True, blank=True)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name="course_test_thresholds", null=True, blank=True)
    
    def __str__(self):
        return f"{self.course.name} - {self.test.title} ({self.min_points}-{self.max_points} pkt)"

class Classroom(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ("Mon", "Poniedziałek"),
        ("Tue", "Wtorek"),
        ("Wed", "Środa"),
        ("Thu", "Czwartek"),
        ("Fri", "Piątek"),
    ]

    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_interval = models.ForeignKey(
        TimeInterval,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Przedział godzinowy",
    )
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Employee, on_delete=models.CASCADE, limit_choices_to={"courses__isnull": False}
    )
    course = models.ForeignKey(LanguageCourse, on_delete=models.CASCADE)
    conflicts = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course} by {self.teacher} in {self.classroom} on {self.day}"


class Availability(models.Model):
    DAY_CHOICES = [
        ("Mon", "Poniedziałek"),
        ("Tue", "Wtorek"),
        ("Wed", "Środa"),
        ("Thu", "Czwartek"),
        ("Fri", "Piątek"),
    ]
    day = models.CharField(
        max_length=3, choices=DAY_CHOICES, verbose_name="Dzień tygodnia"
    )
    time_interval = models.ForeignKey(
        TimeInterval, on_delete=models.CASCADE, verbose_name="Przedział godzinowy"
    )
    classrooms = models.ManyToManyField(
        Classroom, blank=True, verbose_name="Dostępne sale"
    )
    employees = models.ManyToManyField(
        Employee, blank=True, verbose_name="Dostępni pracownicy"
    )

    def __str__(self):
        return f"{self.get_day_display()} {self.time_interval}"

    class Meta:
        unique_together = ("day", "time_interval")
        verbose_name = "Dostępność"
        verbose_name_plural = "Dostępności"

# class Attendance(models.Model):
#     schedule = models.ForeignKey(
#         ClassSchedule, on_delete=models.CASCADE, related_name="attendances"
#     )
#     refugee = models.ForeignKey(
#         Refugee, on_delete=models.CASCADE, related_name="attendances"
#     )
#     date = models.DateField()
#     status = models.CharField(
#         max_length=10,
#         choices=[("present", "Obecny"), ("absent", "Nieobecny"), ("late", "Spóźniony"), ("excused absence", "Nieobecny usprawiedliwiony")],
#         default="absent"
#     )
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.refugee} - {self.schedule} on {self.date}: {self.get_status_display()}"

#     class Meta:
#         unique_together = ("schedule", "refugee", "date")