# Generated by Django 5.1.1 on 2024-09-18 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_delete_test'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]
