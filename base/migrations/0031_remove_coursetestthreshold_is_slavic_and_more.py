# Generated by Django 5.1.3 on 2024-12-21 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_coursetestthreshold_is_slavic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursetestthreshold',
            name='is_slavic',
        ),
        migrations.AddField(
            model_name='languagecourse',
            name='is_slavic',
            field=models.BooleanField(default=False),
        ),
    ]
