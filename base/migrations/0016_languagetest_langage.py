# Generated by Django 5.1.2 on 2024-10-23 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_languagecourse'),
    ]

    operations = [
        migrations.AddField(
            model_name='languagetest',
            name='langage',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
