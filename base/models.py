from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_countries.fields import CountryField


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    courses = models.ManyToManyField(
        "LanguageCourse", related_name="teachers", blank=True
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


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

    def get_nationality_name(self):
        return self.nationality.name

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Semester(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    @classmethod
    def get_current_semesters(cls):
        today = now().date()
        return cls.objects.filter(start_date__lte=today, end_date__gte=today)

class LanguageTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.title


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


class UserAnswer(models.Model):
    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.CASCADE)
    text_answer = models.TextField(null=True, blank=True)
    awarded_points = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Answer by {self.refugee} to {self.question}"


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

    def __str__(self):
        return f"{self.name} ({self.language})"


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
