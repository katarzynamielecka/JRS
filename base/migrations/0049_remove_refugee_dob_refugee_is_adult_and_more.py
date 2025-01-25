# Generated by Django 5.1.4 on 2025-01-09 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_languagecourse_teacher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refugee',
            name='dob',
        ),
        migrations.AddField(
            model_name='refugee',
            name='is_adult',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='refugee',
            name='gender',
            field=models.CharField(choices=[('female', 'Female'), ('male', 'Male')], max_length=10),
        ),
    ]
