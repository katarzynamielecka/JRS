# Generated by Django 5.1.3 on 2024-12-26 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_recruitment_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitment',
            name='max_people',
            field=models.IntegerField(default=1000000),
        ),
        migrations.AlterField(
            model_name='recruitment',
            name='semester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recruitments', to='base.semester', verbose_name='Semestr'),
        ),
    ]
