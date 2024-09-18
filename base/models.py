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
    comments = models.TextField(blank=True)

    def get_nationality_name(self):
        return self.nationality.name

