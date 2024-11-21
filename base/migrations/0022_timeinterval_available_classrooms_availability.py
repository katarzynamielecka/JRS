# Generated by Django 5.1.3 on 2024-11-18 20:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_timeinterval_remove_classschedule_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeinterval',
            name='available_classrooms',
            field=models.ManyToManyField(blank=True, to='base.classroom', verbose_name='Dostępne sale'),
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Mon', 'Poniedziałek'), ('Tue', 'Wtorek'), ('Wed', 'Środa'), ('Thu', 'Czwartek'), ('Fri', 'Piątek')], max_length=3, verbose_name='Dzień tygodnia')),
                ('classrooms', models.ManyToManyField(blank=True, to='base.classroom', verbose_name='Dostępne sale')),
                ('employees', models.ManyToManyField(blank=True, to='base.employee', verbose_name='Dostępni pracownicy')),
                ('time_interval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.timeinterval', verbose_name='Przedział godzinowy')),
            ],
            options={
                'verbose_name': 'Dostępność',
                'verbose_name_plural': 'Dostępności',
                'unique_together': {('day', 'time_interval')},
            },
        ),
    ]
