# Generated by Django 4.1.7 on 2023-09-21 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_information', '0006_alter_login_hours_break_end_dtime_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='login_hours',
            name='break_end_dtime',
            field=models.DateTimeField(default='2000-01-01 00:00:00', null=True),
        ),
        migrations.AlterField(
            model_name='login_hours',
            name='break_start_dtime',
            field=models.DateTimeField(default='2000-01-01 00:00:00', null=True),
        ),
    ]