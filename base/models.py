from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    function = models.CharField(max_length=100)
    
class Question(models.Model):
    QUESTION_TYPES = (
        ('open', 'Open-Ended'),
        ('multiple_choice', 'Multiple Choice'),
    )
    text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES)

    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

# Create your models here.
class Test(models.Model):
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text