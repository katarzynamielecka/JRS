# Generated by Django 5.1.3 on 2024-12-29 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0038_remove_languagetest_is_current'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useranswer',
            name='refugee',
        ),
        migrations.CreateModel(
            name='FilledTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_points', models.FloatField(default=0.0)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('recruitment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_tests', to='base.recruitment')),
                ('refugee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_tests', to='base.refugee')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_tests', to='base.languagetest')),
            ],
        ),
        migrations.AddField(
            model_name='useranswer',
            name='completed_test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='base.filledtest', verbose_name='Completed Test'),
        ),
    ]
