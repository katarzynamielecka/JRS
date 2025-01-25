# Generated by Django 5.1.4 on 2025-01-07 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_languagecourse_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='languagecourse',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teaching_courses', to='base.employee'),
        ),
    ]
