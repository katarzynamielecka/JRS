# Generated by Django 5.1.2 on 2024-10-23 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_languagetest_is_current'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('language', models.CharField(max_length=100)),
            ],
        ),
    ]
