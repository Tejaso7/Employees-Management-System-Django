# Generated by Django 4.1.7 on 2023-09-26 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_information', '0010_manageremployee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee_education',
            name='diploma_pdf',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='diploma_percent',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='diploma_stream',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='diploma_university',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='diploma_year',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='master_degree_pdf',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='master_degree_percent',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='master_degree_stream',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='master_degree_university',
        ),
        migrations.RemoveField(
            model_name='employee_education',
            name='master_degree_year',
        ),
        migrations.AddField(
            model_name='experience',
            name='offer_letter',
            field=models.FileField(null=True, upload_to='company_letter/'),
        ),
        migrations.AddField(
            model_name='experience',
            name='relieving_letter',
            field=models.FileField(null=True, upload_to='company_letter/'),
        ),
    ]
