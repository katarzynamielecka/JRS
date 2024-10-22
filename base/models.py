from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
class Refugee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other')])
    dob = models.DateField()
    phone_number = models.CharField(max_length=15)
    nationality = CountryField(blank_label='Select country')
    residency = models.CharField(max_length=20, choices=[('permanent', 'Permanent'), ('temporary', 'Temporary'), ('refugee', 'Refugee'), ('other', 'Other')])
    rodo_consent = models.BooleanField(default=False)  
    truth_confirmation = models.BooleanField(default=False)
    comments = models.TextField(blank=True)

    def get_nationality_name(self):
        return self.nationality.name
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class LanguageTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('open', 'Otwarte'),
        ('choice', 'Wielokrotnego wyboru'),
    )
    
    test = models.ForeignKey(LanguageTest, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES)
    order = models.IntegerField(default=0) 
    max_points = models.FloatField(default=1.0)
    
    def __str__(self):
        return f'{self.text} ({self.get_question_type_display()})'

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
class UserAnswer(models.Model):
    refugee = models.ForeignKey(Refugee, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.CASCADE)  # Jeśli pytanie to choice
    text_answer = models.TextField(null=True, blank=True) 
    awarded_points = models.FloatField(null=True, blank=True) 

    def __str__(self):
        return f'Answer by {self.refugee} to {self.question}'