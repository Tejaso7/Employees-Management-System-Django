# from django.conf import settings
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_type = models.CharField(max_length=100, default='Admin')


# Create your models here.
class Department(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField()
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.TextField()
    description = models.TextField()
    status = models.IntegerField()
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Employee_personal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_ID = models.CharField(max_length=5, unique=True)
    emp_name = models.TextField()
    email = models.CharField(max_length=200)
    phone = models.BigIntegerField()
    emergency_phone = models.BigIntegerField()
    address = models.TextField()
    blood_grp = models.TextField()
    pancard = models.CharField(max_length=10)
    adharcard = models.CharField(max_length=12)
    designation = models.ForeignKey(Position, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    joining_date = models.DateField()


class Employee_Education(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenth_stream = models.TextField(default='None')
    tenth_university = models.TextField(default='None')
    tenth_year = models.TextField(default='None')
    tenth_percent = models.TextField(default='None')
    tenth_pdf = models.FileField(upload_to='attachments/', default='None')
    twelfth_stream = models.TextField(null=True)
    twelfth_university = models.TextField(null=True)
    twelfth_year = models.TextField(null=True)
    twelfth_percent = models.TextField(null=True)
    twelfth_pdf = models.FileField(upload_to='attachments/', null=True)
    degree_stream = models.TextField(null=True)
    degree_university = models.TextField(null=True)
    degree_year = models.TextField(null=True)
    degree_percent = models.TextField(null=True)
    degree_pdf = models.FileField(upload_to='attachments/', null=True)
    # master_degree_stream = models.TextField(null=True)
    # master_degree_university = models.TextField(null=True)
    # master_degree_year = models.TextField(null=True)
    # master_degree_percent = models.TextField(null=True)
    # master_degree_pdf = models.FileField(upload_to='attachments/', null=True)
    # diploma_stream = models.TextField(null=True)
    # diploma_university = models.TextField(null=True)
    # diploma_year = models.TextField(null=True)
    # diploma_percent = models.TextField(null=True)
    # diploma_pdf = models.FileField(upload_to='attachments/', null=True)
    other_stream = models.TextField(null=True)
    other_university = models.TextField(null=True)
    other_year = models.TextField(null=True)
    other_percent = models.TextField(null=True)
    other_pdf = models.FileField(upload_to='attachments/', null=True)


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.TextField()
    designation = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_months = models.TextField(null=True)
    leave_reason = models.TextField()
    offer_letter = models.FileField(upload_to='company_letter/', null=True)
    relieving_letter = models.FileField(upload_to='company_letter/', null=True)

    @property
    def count_months(self):
        if self.start_date and self.end_date:
            # Calculate the difference between end_date and start_date
            delta = self.end_date - self.start_date

            # Calculate the number of months
            total_months = delta.days // 30  # Assuming a month is approximately 30 days

            return total_months
        else:
            return None  # Handle the case where either date is missing


class LeaveType(models.Model):
    leave_name = models.CharField(max_length=50)
    total_allocation = models.IntegerField()


class Leave(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    used_leaves = models.IntegerField(default=0)
    pending_leaves = models.IntegerField()
    available_leaves = models.IntegerField(default=0)
    casual_leave = models.IntegerField(default=10, null=True)
    privilege_leave = models.IntegerField(default=20, null=True)
    sick_leave = models.IntegerField(default=10, null=True)


class LeaveRecord(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.FloatField()
    half_day = models.BooleanField(default=False)
    reason = models.TextField()
    leave_approver = models.CharField(max_length=30, null=True)
    status = models.CharField(max_length=20, default='Pending')
    Letter_head = models.CharField(max_length=40, null=True)

    @property
    def count_days(self):
        if self.start_date and self.end_date:
            # Calculate the difference between end_date and start_date
            total_days = (self.end_date - self.start_date).days + 1

            return total_days
        else:
            return None  # Handle the case where either date is missing

    @property
    def Used_leaves(self):
        if self.start_date and self.end_date:
            used_leaves = int(self.total_days) + 1
            return used_leaves
        else:
            used_leaves = 0
            return used_leaves


def default_start_time():
    now = datetime.now()
    start = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)


class Login_Hours(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    day_time = models.DateTimeField(null=True)
    login_dtime = models.DateTimeField(null=True)
    logout_dtime = models.DateTimeField(null=True)
    break_start_dtime = models.DateTimeField(null=True, default=default_start_time)
    break_end_dtime = models.DateTimeField(null=True, default=default_start_time)
    session_time = models.TimeField(null=True)
    break_time = models.TimeField(null=True)
    active_time = models.CharField(max_length=500)


class Login_Details(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    login_dtime = models.DateTimeField(null=True)
    logout_dtime = models.DateTimeField(null=True)
    break_start_dtime = models.DateTimeField(null=True)
    break_end_dtime = models.DateTimeField(null=True)
    session_time = models.DateTimeField(null=True)
    break_time = models.DateTimeField(null=True)
    active_time = models.DateTimeField(null=True)


class EmployeeLoginHrs(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    login_dtime = models.DateTimeField(null=True)
    logout_dtime = models.DateTimeField(null=True)
    break_start_dtime = models.DateTimeField(null=True, default=default_start_time)
    break_end_dtime = models.DateTimeField(null=True, default=default_start_time)
    session_time = models.CharField(max_length=500)
    break_time = models.CharField(max_length=500)
    active_time = models.CharField(max_length=500)


class Salary(models.Model):
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)
    date = models.DateField()
    basic_salary = models.FloatField()
    HRA = models.FloatField()
    medical_allowance = models.FloatField()
    conveyance_allowance = models.FloatField()
    leave_travel_allowance = models.FloatField()
    special_allowance = models.FloatField()
    pt_maharashtra = models.FloatField()
    employee_share_in_pf = models.FloatField()
    health_insurance = models.FloatField()
    employers_share_in_pf = models.FloatField(default=1584)
    gross = models.FloatField(default=30000)
    ctc = models.FloatField(default=30000)
    uan_no = models.FloatField(default=101731461799)
    payable_days = models.FloatField(default=10)
    other = models.FloatField(default=40000)


class ManagerEmployee(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee_personal, on_delete=models.CASCADE)


class ITHelpDesk(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_type = models.TextField()
    issue_description = models.CharField(max_length=500)
    priority = models.TextField()
    to_send_email = models.TextField()
