# Generated by Django 4.1.7 on 2023-09-22 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_information', '0008_alter_employee_personal_employee_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='login_hours',
            name='break_time',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='login_hours',
            name='session_time',
            field=models.TimeField(null=True),
        ),
    ]