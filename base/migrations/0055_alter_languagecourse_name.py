# Generated by Django 5.1.5 on 2025-01-21 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0054_refugee_attended_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languagecourse',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
