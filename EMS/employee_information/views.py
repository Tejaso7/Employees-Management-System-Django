import json
from io import BytesIO

from django import template
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template
from num2words import num2words
from xhtml2pdf import pisa
from employee_information.models import *


def update_time(request, event):
    d = datetime.now()
    user = request.user
    print(user)
    if request.user.user_type == 'Employee' or request.user.user_type == 'HR' or request.user.user_type == 'Manager':
        emp = Employee_personal.objects.get(user=user)
        employee = emp
        update_employee_login_hrs(request, employee, d, event)
    else:
        return redirect('personal_info')


def update_employee_login_hrs(request, employee, d, event):
    if event == 'Login':
        login_time = EmployeeLoginHrs(employee=employee, date=d, login_dtime=d)
        login_time.save()
    elif event == 'Logout':
        print('logging out')
        emp = EmployeeLoginHrs.objects.filter(employee=employee).order_by('-id')[0]
        emp.logout_dtime = d
        emp.save()

        emp = EmployeeLoginHrs.objects.filter(employee=employee).order_by('-id')[0]
        session_time = emp.logout_dtime - emp.login_dtime
        emp.session_time = session_time
        print(session_time)

        break_time = emp.break_end_dtime - emp.break_start_dtime
        emp.break_time = break_time
        print(break_time)

        active_time = session_time - break_time
        print(active_time)

        emp.active_time = active_time
        emp.save()

    elif event == 'break_start':
        print('Break Time Start')
        emp = EmployeeLoginHrs.objects.filter(employee=employee).order_by('-id')[0]
        emp.break_start_dtime = d
        emp.save()
        return render(request, 'employee_information/login_hrs_details.html')

    elif event == 'break_end':
        emp = EmployeeLoginHrs.objects.filter(employee=employee).order_by('-id')[0]
        emp.break_end_dtime = d
        emp.save()
        return render(request, 'employee_information/login_hrs_details.html')

    return render(request, 'employee_information/Leave_request.html')


def saveBreak(request):
    if 'start' in request.POST:
        update_time(request, 'break_start')
    elif 'end' in request.POST:
        update_time(request, 'break_end')
    else:
        print('Nothing')
    return redirect('personal_info')


def registrations(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')

        if password1 != password2:
            context1 = {"message1": "Password mismatch", "class1": "danger"}
            return render(request, 'employee_information/Signup.html', context1)

        user = User.objects.create_user(
            first_name=first_name, last_name=last_name, username=username, email=email, password=password1,
            user_type=user_type)
        user.save()
        return redirect('login')

    return render(request, 'employee_information/Signup.html')


# Logout
def logout_user(request):
    try:
        update_time(request, 'Logout')
    except:
        print('User Personal Details are not saved')
    logout(request)
    return redirect('/')


# Create your views here.
@login_required
def home(request):
    context = {
        'page_title': 'Home',
        'employees': employees,
        'total_department': len(Department.objects.all()),
        'total_position': len(Position.objects.all()),
        'total_employee': len(Employee_personal.objects.all()),
    }
    try:
        update_time(request, 'Login')
    except:
        print('User Personal Details are not saved')
        messages.warning(request, 'User Personal Details are not saved, Kindly Fill!!')
    messages.success(request, "You Are Successfully Login!!")
    return render(request, 'employee_information/home.html', context)


def about(request):
    context = {
        'page_title': 'About',
    }
    return render(request, 'employee_information/about.html', context)


# Departments
@login_required
def departments(request):
    department_list = Department.objects.all()
    context = {
        'page_title': 'Departments',
        'departments': department_list,
    }
    return render(request, 'employee_information/departments.html', context)


@login_required
def manage_departments(request):
    department = {}
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            department = Department.objects.filter(id=id).first()

    context = {
        'department': department
    }
    return render(request, 'employee_information/manage_department.html', context)


@login_required
def save_department(request):
    data = request.POST
    resp = {'status': 'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0:
            department = Department.objects.filter(id=data['id']).update(name=data['name'],
                                                                         description=data['description'],
                                                                         status=data['status'])
        else:
            department = Department(name=data['name'], description=data['description'], status=data['status'])
            department.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_department(request):
    data = request.POST
    resp = {'status': ''}
    try:
        Department.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


# Positions
@login_required
def positions(request):
    position_list = Position.objects.all()
    context = {
        'page_title': 'Positions',
        'positions': position_list,
    }
    return render(request, 'employee_information/positions.html', context)


@login_required
def manage_positions(request):
    position = {}
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            position = Position.objects.filter(id=id).first()

    context = {
        'position': position
    }
    return render(request, 'employee_information/manage_position.html', context)


@login_required
def save_position(request):
    data = request.POST
    resp = {'status': 'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0:
            position = Position.objects.filter(id=data['id']).update(name=data['name'], description=data['description'],
                                                                     status=data['status'])
        else:
            position = Position(name=data['name'], description=data['description'], status=data['status'])
            position.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_position(request):
    data = request.POST
    resp = {'status': ''}
    try:
        Position.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
# Employees
def employees(request):
    employee_list = ManagerEmployee.objects.all()
    managers = User.objects.filter(user_type='Manager')
    context = {
        'page_title': 'Employees',
        'employees': employee_list,
        'managers': managers,
    }
    return render(request, 'employee_information/employees.html', context)


def save_tag_employee(request, id):
    employee = Employee_personal.objects.get(id=id)
    manager_id = request.POST.get('manager')
    manager = User.objects.get(id=manager_id)

    if ManagerEmployee.objects.filter(employee=employee).order_by('-id')[0]:
        assignee = ManagerEmployee.objects.filter(employee=employee).order_by('-id')[0]
    else:
        assignee = ManagerEmployee()

    assignee.employee = employee
    assignee.manager = manager
    assignee.save()

    messages.success(request, "Manager Assign To Employee Successfully!!"),
    return redirect('employee-page')
    # except:
    #     return redirect('employee-page')


def personal_info(request):
    try:
        if Employee_personal.objects.get(user=request.user):
            user = request.user
            emp = Employee_personal.objects.get(user=user)
            emp_education = Employee_Education.objects.get(user=user)
            experience_list = Experience.objects.filter(user=user)
            department = Department.objects.filter(status=1).all()
            designations = Position.objects.filter(status=1).all()
            return render(request, 'employee_information/Employee_update.html', {'emp': emp,
                                                                                 'departments': department,
                                                                                 'designations': designations,
                                                                                 'emp1': emp_education,
                                                                                 'experience_list': experience_list})
    except:
        employee = {}
        department = Department.objects.filter(status=1).all()
        designations = Position.objects.filter(status=1).all()
        if request.method == 'GET':
            data = request.GET
            id = ''
            if 'id' in data:
                id = data['id']
            if id.isnumeric() and int(id) > 0:
                employee = Employee_personal.objects.filter(id=id).first()
        context = {
            'employee': employee,
            'departments': department,
            'designations': designations
        }
        messages.warning(request, 'Kindly Fill Personal Details for Further Updates!!')
        return render(request, 'employee_information/Add_employee.html', context)


def savePersonal(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        email = request.POST.get('email')
        emp_id = request.POST.get('empid')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        emer_contact = request.POST.get('emer_contact')
        blood = request.POST.get('blood')
        pan_card = request.POST.get('pan')
        aadhar_card = request.POST.get('aadhar')

        depart = request.POST.get('department_id')
        department = Department.objects.get(id=depart)

        position = request.POST.get('designation')
        designation = Position.objects.get(id=position)

        joining_date = request.POST.get('joining')

        personal = Employee_personal(user=user, employee_ID=emp_id, emp_name=name, email=email, phone=contact,
                                     emergency_phone=emer_contact, address=address, blood_grp=blood, pancard=pan_card,
                                     adharcard=aadhar_card, designation=designation, department=department,
                                     joining_date=joining_date)

        personal.save()
        context = {"message": "Successfully Personal Information Added", "class2": "alert1 success"}
        return render(request, 'employee_information/Add_employee.html', context)

    return render(request, 'employee_information/Add_employee.html')


def update_employee(request, id):
    print(id)
    return render(request, 'employee_information/Add_employee.html')


def updatePersonal(request, id):
    emp = Employee_personal.objects.get(id=id)

    emp.employee_ID = request.POST.get('empid')
    emp.emp_name = request.POST.get('name')
    emp.email = request.POST.get('email')
    emp.phone = request.POST.get('contact')
    emp.emergency_phone = request.POST.get('emer_contact')
    emp.address = request.POST.get('address')
    emp.blood_grp = request.POST.get('blood')
    emp.pancard = request.POST.get('pan')
    emp.adharcard = request.POST.get('aadhar')
    emp.joining_date = request.POST.get('joining')

    department = request.POST.get('department_id')
    emp.department = Department.objects.get(id=department)

    designation = request.POST.get('designation')
    emp.designation = Position.objects.get(id=designation)

    emp.save()
    context = {"message": "Successfully Personal Information Updated", "class2": "alert1 success "}
    return render(request, 'employee_information/Add_employee.html', context)


def saveEducational(request):
    if request.method == 'POST':
        education = Employee_Education(user=request.user, tenth_stream=request.POST.get('tenth_stream'),
                                       tenth_university=request.POST.get('tenth_Uni'),
                                       tenth_year=request.POST.get('tenth_year'),
                                       tenth_percent=request.POST.get('tenth_percent'),
                                       tenth_pdf=request.FILES['tenth_pdf'],
                                       twelfth_stream=request.POST.get('twelfth_stream'),
                                       twelfth_university=request.POST.get('twelfth_Uni'),
                                       twelfth_year=request.POST.get('twelfth_year'),
                                       twelfth_percent=request.POST.get('twelfth_percent'),
                                       twelfth_pdf=request.FILES['twelfth_pdf'],
                                       degree_stream=request.POST.get('degree_stream'),
                                       degree_university=request.POST.get('degree_Uni'),
                                       degree_year=request.POST.get('degree_year'),
                                       degree_percent=request.POST.get('degree_percent'),
                                       degree_pdf=request.FILES['degree_pdf'],
                                       other_stream=request.POST.get('other_stream'),
                                       other_university=request.POST.get('other_Uni'),
                                       other_year=request.POST.get('other_year'),
                                       other_percent=request.POST.get('other_percent'),
                                       other_pdf=request.POST.get('other_pdf'))
        education.save()
        context = {"message": "Successfully Personal Information Added", "class2": "alert1 success"}
        return render(request, 'employee_information/Add_employee.html', context)

    return render(request, 'employee_information/Add_employee.html')


def Edit_education(request, id):
    emp = Employee_Education.objects.get(user=id)
    return render(request, 'employee_information/EditEducation.html', {'emp': emp})


def updateEducation(request, id):
    emp = Employee_Education.objects.get(id=id)

    emp.tenth_stream = request.POST.get('tenth_stream')
    emp.tenth_university = request.POST.get('tenth_Uni')
    emp.tenth_year = request.POST.get('tenth_year')
    emp.tenth_percent = request.POST.get('tenth_percent')
    tenth_pdf = request.FILES.get('tenth_pdf')
    if tenth_pdf == None:
        print("Nothing")
    else:
        emp.tenth_pdf = tenth_pdf
    emp.twelfth_stream = request.POST.get('twelfth_stream')
    emp.twelfth_university = request.POST.get('twelfth_Uni')
    emp.twelfth_year = request.POST.get('twelfth_year')
    emp.twelfth_percent = request.POST.get('twelfth_percent')
    twelfth_pdf = request.FILES.get('twelfth_pdf')
    if twelfth_pdf == None:
        print("Nothing")
    else:
        emp.twelfth_pdf = twelfth_pdf
    emp.degree_stream = request.POST.get('degree_stream')
    emp.degree_university = request.POST.get('degree_Uni')
    emp.degree_year = request.POST.get('degree_year')
    emp.degree_percent = request.POST.get('degree_percent')
    degree_pdf = request.FILES.get('degree_pdf')
    if degree_pdf == None:
        print("Nothing")
    else:
        emp.degree_pdf = degree_pdf
    emp.other_stream = request.POST.get('other_stream')
    emp.other_university = request.POST.get('other_Uni')
    emp.other_year = request.POST.get('other_year')
    emp.other_percent = request.POST.get('other_percent')
    other_pdf = request.FILES.get('other_pdf')
    if other_pdf == None:
        print("Nothing")
    else:
        emp.other_pdf = other_pdf
    emp.save()
    return redirect('personal_info')


def saveExperience(request):
    if request.method == 'POST':
        experience = Experience(user=request.user, company=request.POST.get('company_name'),
                                designation=request.POST.get('designation'),
                                start_date=request.POST.get('month_year_start'),
                                end_date=request.POST.get('month_year_end'),
                                leave_reason=request.POST.get('leave_reason'),
                                offer_letter=request.FILES['offer_letter_pdf'],
                                relieving_letter=request.FILES['relieving_letter_pdf'])

        experience.save()
        count = Experience.objects.filter(user=request.user).order_by('-id')[0]
        months = count.count_months
        print(months)
        count.total_months = months
        count.save()
        return redirect('personal_info')

    return render(request, 'employee_information/Add_employee.html')


def add_education(request):
    return render(request, 'employee_information/Add_employee.html')


def add_experience(request):
    return render(request, 'employee_information/Add_employee.html')


def View_experience(request):
    user = request.user
    experience_list = Experience.objects.filter(user=user)
    return render(request, 'employee_information/Experience_list.html', {'experience_list': experience_list})


def Edit_experience(request, id):
    experience = Experience.objects.get(id=id)
    return render(request, 'employee_information/Update_Experience.html', {'experience': experience})


def updateExperience(request, id):
    try:
        experience = Experience.objects.get(id=id)

        experience.company = request.POST.get('company_name')
        experience.designation = request.POST.get('designation')
        experience.start_date = request.POST.get('month_year_start')
        experience.end_date = request.POST.get('month_year_end')
        experience.leave_reason = request.POST.get('leave_reason')
        experience.offer_letter = request.FILES['offer_letter_pdf']
        experience.relieving_letter = request.FILES['relieving_letter_pdf']

        experience.save()
        experience = Experience.objects.get(id=id)
        months = experience.count_months
        print(months)
        experience.total_months = months
        experience.save()
        return redirect('personal_info')
    except:
        return redirect('personal_info')


def leave_request(request):
    leave1 = LeaveType.objects.get(id=1)
    leave2 = LeaveType.objects.get(id=2)
    leave3 = LeaveType.objects.get(id=3)
    try:
        if Employee_personal.objects.get(user=request.user):
            emp = Employee_personal.objects.get(user=request.user)

            manager = ManagerEmployee.objects.filter(employee=emp.id).order_by('-id')[0]

            leave_type = LeaveType.objects.all()

            user = request.user
            emp = Employee_personal.objects.get(user=user)

            try:
                casual_leave = Leave.objects.filter(employee=emp.id, leave_type=leave1.id).order_by('-id')[0]
            except:
                casual_leave = 0

            try:
                privilege_leave = Leave.objects.filter(employee=emp.id, leave_type=leave2.id).order_by('-id')[0]
            except:
                privilege_leave = 0

            try:
                sick_leave = Leave.objects.filter(employee=emp.id, leave_type=leave3.id).order_by('-id')[0]
            except:
                sick_leave = 0

            employee = Employee_personal.objects.get(user=request.user)
            context = {
                'employee': employee,
                'leave_type': leave_type,
                'leave1': leave1,
                'leave2': leave2,
                'leave3': leave3,
                'casual_leave': casual_leave,
                'privilege_leave': privilege_leave,
                'sick_leave': sick_leave,
                'approver': manager
            }
            return render(request, 'employee_information/Leave_request.html', context)
        else:
            messages.warning(request, 'Manager is not assign yet!!')
            return redirect('leave_request')
    except:
        messages.warning(request, 'Kindly Fill Personal Details first for Further Updates!!')
        return render(request, 'employee_information/Add_employee.html')


def saveLeave(request):
    if request.method == 'POST':
        emp = Employee_personal.objects.get(user=request.user)
        print(emp.id)

        leave_type = request.POST.get('leave_type')
        type_leave = LeaveType.objects.get(id=leave_type)

        half_day = request.POST.get('halfday')
        print('Half Day:', half_day)
        half_day = True if half_day else False

        if half_day and request.POST.get('start_date') == request.POST.get('end_date'):
            total_leave_days = 1
            total_days = total_leave_days / 2
        else:
            total_days = request.POST.get('total_leave_days')

        leave = LeaveRecord(employee=emp, leave_type=type_leave, start_date=request.POST.get('start_date'),
                            end_date=request.POST.get('end_date'), total_days=total_days, half_day=half_day,
                            reason=request.POST.get('leave_reason'), Letter_head=request.POST.get('letter_head'))

        leave.save()

    return redirect('personal_info')


def update_leave_request(request, id):
    emp = Employee_personal.objects.get(user=id)
    emp_leave_request = LeaveRecord.objects.filter(employee=emp).order_by('-id')[0]
    leave_type = LeaveType.objects.all()

    return render(request, 'employee_information/leave_request_update.html', {'leave_request': emp_leave_request,
                                                                              'leave_type': leave_type})


def updateLeave(request, id):
    if request.method == 'POST':
        leave_update = LeaveRecord.objects.get(id=id)

        leave_type = request.POST.get('leave_type')
        print(leave_type)
        type_leave = LeaveType.objects.get(id=leave_type)
        print(type_leave)

        half_day = request.POST.get('halfday')
        print('Half Day:', half_day)
        half_day = True if half_day else False

        if half_day and request.POST.get('start_date') == request.POST.get('end_date'):
            total_leave_days = 1
            total_days = total_leave_days / 2
        else:
            total_days = request.POST.get('total_leave_days')

        leave_update.leave_type = type_leave
        leave_update.start_date = request.POST.get('start_date')
        leave_update.end_date = request.POST.get('end_date')
        leave_update.total_days = total_days
        leave_update.reason = request.POST.get('leave_reason')
        leave_update.half_day = half_day
        leave_update.Letter_head = request.POST.get('letter_head')

        leave_update.save()

    return redirect('personal_info')


def login_hrs(request):
    try:
        if Employee_personal.objects.get(user=request.user):
            emp = Employee_personal.objects.get(user=request.user)
            emp_login_hrs = EmployeeLoginHrs.objects.filter(employee=emp.id).order_by('-date')

            return render(request, 'employee_information/login_hrs_details.html', {'login_hrs': emp_login_hrs})
    except:
        messages.warning(request, 'Kindly Fill Personal Details first for Further Updates!!')
        return render(request, 'employee_information/Add_employee.html')


def employee_login(request):
    try:
        emp_login_hrs = EmployeeLoginHrs.objects.all().order_by('-date')
        return render(request, 'employee_information/login_hrs.html', {'login_hrs_details': emp_login_hrs})
    except:
        return render(request, 'employee_information/Add_employee.html')


register = template.Library()


def employee_leave(request):
    manager_id = request.user.id
    emp_leave_request = LeaveRecord.objects.raw(f'select * from public.employee_information_leaverecord where '
                                                f'status= \'Pending\' and employee_id '
                                                f'in(select employee_id '
                                                f'from public.employee_information_manageremployee'
                                                f' where manager_id in ({manager_id}))')

    return render(request, 'employee_information/Employee_leave_request.html', {'leave': emp_leave_request})


def update_emp_request(request, id):
    manager_id = request.user.id
    emp_leave_request = LeaveRecord.objects.raw(f'select * from public.employee_information_leaverecord where '
                                                f'status= \'Pending\' and employee_id '
                                                f'in(select employee_id '
                                                f'from public.employee_information_manageremployee'
                                                f' where manager_id in ({manager_id}))')
    if request.method == 'POST':
        leave = LeaveRecord.objects.get(id=id)

        leave.status = request.POST.get('status')
        print("status:", request.POST.get('status'))
        leave.leave_approver = request.user.first_name + request.user.last_name
        leave.save()

        record = LeaveRecord.objects.get(id=id)

        if record.status == 'Approved':
            leave_record = LeaveRecord.objects.filter(employee=record.employee.id).order_by('-id')[0]
            print('inside leave')

            emp = Employee_personal.objects.get(id=record.employee.id)
            print('emp id:', emp)

            print('leave record:', leave_record)

            used_leaves = leave_record.Used_leaves
            print(used_leaves)

            if Leave.objects.filter(employee=emp.id).order_by('-id')[0]:
                leave_allocation = Leave.objects.filter(employee=emp.id).order_by('-id')[0]

            else:
                leave_allocation = Leave()

            leave_allocation.employee = emp

            leave_type = LeaveType.objects.get(id=leave_record.leave_type.id)
            leave_allocation.leave_type = leave_type

            leave_allocation.used_leaves = leave_allocation.used_leaves + used_leaves

            pending = LeaveRecord.objects.filter(leave_type=leave_record.leave_type, status='Pending').count()

            leave_allocation.pending_leaves = pending

            leave_allocation.save()

            emp = Employee_personal.objects.get(id=record.employee.id)
            last_record = Leave.objects.filter(employee=emp.id).order_by('-id')[0]

            leave_allocate = \
                Leave.objects.filter(employee=emp.id, leave_type=last_record.leave_type.id).order_by('-id')[0]

            if leave_allocate.leave_type.leave_name == "Casual Leaves":
                leave_allocate.available_leaves = leave_allocate.casual_leave - used_leaves
                leave_allocate.casual_leave = leave_allocate.casual_leave - leave_allocate.used_leaves

            elif leave_allocate.leave_type.leave_name == "Privilege Leaves":
                leave_allocate.available_leaves = leave_allocate.privilege_leave - used_leaves
                leave_allocate.privilege_leave = leave_allocate.privilege_leave - leave_allocate.used_leaves
            else:
                leave_allocate.available_leaves = leave_allocate.sick_leave - used_leaves
                leave_allocate.sick_leave = leave_allocate.sick_leave - leave_allocate.used_leaves

            leave_allocate.save()
            return redirect('leave_request')
        else:
            messages.warning(request, 'Leave Request is not Approved yet!!')
            return render(request, 'employee_information/Employee_leave_request.html', {'leave': emp_leave_request})

    return render(request, 'employee_information/Employee_leave_request.html', {'leave': emp_leave_request})


def select_salary_date(request):
    try:
        employee = Employee_personal.objects.get(user=request.user)
        salary_date = Salary.objects.filter(employee=employee)

        return render(request, 'employee_information/Select_date.html', {'salary_date': salary_date})
    except:
        messages.warning(request, 'Kindly update your Personal Details!!')
        return render(request, 'employee_information/Add_employee.html')


def salary_details(request):
    try:
        if Employee_personal.objects.get(user=request.user):
            employee = Employee_personal.objects.get(user=request.user)
            salary_id = request.POST.get('date')
            salary = Salary.objects.get(id=salary_id)

            total_payment = salary.basic_salary + salary.HRA + salary.medical_allowance + salary.conveyance_allowance \
                + salary.leave_travel_allowance + salary.special_allowance

            deduction = salary.pt_maharashtra + salary.employers_share_in_pf + salary.health_insurance + \
                salary.employee_share_in_pf + salary.other

            net_pay = total_payment - deduction
            net_pay_in_words = num2words(net_pay)
            net_payment = net_pay_in_words.replace('-', '  ').title()

            return render(request, 'employee_information/Salary_details.html', {'employee': employee,
                                                                                'salary': salary,
                                                                                'total_payment': total_payment,
                                                                                'deduction': deduction,
                                                                                'net_pay': net_pay,
                                                                                'net_pay_in_words': net_payment
                                                                                })
    except:
        messages.warning(request, 'Salary is not updated yet by HR!!')
        return render(request, 'employee_information/Add_employee.html')


def select_employee(request):
    employee = Employee_personal.objects.all()
    return render(request, 'employee_information/Select_employee.html', {'employee': employee})


def salary_hr(request):
    employee = Employee_personal.objects.all()
    emp = request.POST.get('employee')
    id = Employee_personal.objects.get(id=emp)
    try:
        salary = Salary.objects.filter(employee=id).order_by('-id')[0]
        return render(request, 'employee_information/salary_hr.html', {'salary': salary,
                                                                       'employee': employee})
    except:
        return render(request, 'employee_information/salary_hr.html', {'employee': employee})


def save_salary(request):
    try:
        salary = Salary()
        emp_id = request.POST.get('employee')
        employee = Employee_personal.objects.get(id=emp_id)

        salary.employee = employee
        salary.date = request.POST.get('select_date')
        salary.basic_salary = request.POST.get('basic_salary')
        salary.HRA = request.POST.get('hra')
        salary.medical_allowance = request.POST.get('medical_allowance')
        salary.conveyance_allowance = request.POST.get('conveyance_allowance')
        salary.leave_travel_allowance = request.POST.get('leave_allowance')
        salary.special_allowance = request.POST.get('special_allowance')
        salary.pt_maharashtra = request.POST.get('pt_maharashtra')
        salary.employers_share_in_pf = request.POST.get('Employer_share_pf')
        salary.employee_share_in_pf = request.POST.get('Employee_share_pf')
        salary.health_insurance = request.POST.get('health_insurance')
        salary.gross = request.POST.get('gross')
        salary.ctc = request.POST.get('ctc')
        salary.uan_no = request.POST.get('uan_no')
        salary.payable_days = request.POST.get('payable_days')
        salary.other = request.POST.get('other')
        salary.save()
        return redirect('select_employee')
    except:
        return redirect('personal_info')


def view_employee_salary(request):
    return render(request, 'employee_information/View_Salary_List.html', {'salary': Salary.objects.all()})


def Edit_salary(request, id):
    salary = Salary.objects.filter(id=id).order_by('-id')[0]
    return render(request, 'employee_information/Edit_Salary.html', {'salary': salary})


def updateSalary(request, id):
    salary = Salary.objects.get(id=id)
    salary.date = request.POST.get('select_date')
    salary.basic_salary = request.POST.get('basic_salary')
    salary.HRA = request.POST.get('hra')
    salary.medical_allowance = request.POST.get('medical_allowance')
    salary.conveyance_allowance = request.POST.get('conveyance_allowance')
    salary.leave_travel_allowance = request.POST.get('leave_allowance')
    salary.special_allowance = request.POST.get('special_allowance')
    salary.pt_maharashtra = request.POST.get('pt_maharashtra')
    salary.employers_share_in_pf = request.POST.get('Employer_share_pf')
    salary.employee_share_in_pf = request.POST.get('Employee_share_pf')
    salary.health_insurance = request.POST.get('health_insurance')
    salary.gross = request.POST.get('gross')
    salary.ctc = request.POST.get('ctc')
    salary.uan_no = request.POST.get('uan_no')
    salary.payable_days = request.POST.get('payable_days')
    salary.other = request.POST.get('other')
    salary.save()

    return render(request, 'employee_information/View_Salary_List.html', {'salary': Salary.objects.all()})


def render_to_pdf(request):
    employee = Employee_personal.objects.get(user=request.user)
    salary = Salary.objects.filter(employee=employee.id).order_by('-id')[0]

    total_payment = salary.basic_salary + salary.HRA + salary.medical_allowance + salary.conveyance_allowance \
        + salary.leave_travel_allowance + salary.special_allowance

    deduction = salary.pt_maharashtra + salary.employers_share_in_pf + salary.health_insurance + \
        salary.employee_share_in_pf + salary.other

    net_pay = total_payment - deduction
    net_pay_in_words = num2words(net_pay)
    net_payment = net_pay_in_words.replace('-', '  ').title()
    temp = get_template('employee_information/payment_bill.html')

    context_dict = {'employee': employee, 'salary': salary, 'total_payment': total_payment, 'deduction': deduction,
                    'net_pay': net_pay, 'net_pay_in_words': net_payment}
    html = temp.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def view_average_login_hrs(request, id):
    try:
        emp = Employee_personal.objects.get(user=request.user)

        login_time = EmployeeLoginHrs.objects.filter(employee=emp).values_list('login_dtime', flat=True, )

        logout_time = EmployeeLoginHrs.objects.filter(employee=emp).values_list('logout_dtime', flat=True)

        session_time = EmployeeLoginHrs.objects.filter(employee=emp).values_list('session_time', flat=True)

        active_time = EmployeeLoginHrs.objects.filter(employee=emp).values_list('active_time', flat=True)

        locked_time = EmployeeLoginHrs.objects.filter(employee=emp).values_list('break_time', flat=True)

        if login_time:
            timestamps = [entry.timestamp() for entry in login_time]
            average_timestamp = sum(timestamps) / len(timestamps)
            average_login_time = datetime.fromtimestamp(average_timestamp)
            print(average_login_time)
        else:
            average_login_time = None

        if logout_time:
            timestamps = [entry.timestamp() for entry in logout_time]
            average_timestamp = sum(timestamps) / len(timestamps)
            average_logout_time = datetime.fromtimestamp(average_timestamp)
            print(average_logout_time)
        else:
            average_logout_time = None

        if session_time:
            timestamps = [entry.timestamp() for entry in session_time]
            average_timestamp = sum(timestamps) / len(timestamps)
            avg_session_time = datetime.fromtimestamp(average_timestamp)
            print(average_logout_time)
        else:
            avg_session_time = None

        if active_time:
            timestamps = [entry.timestamp() for entry in active_time]
            average_timestamp = sum(timestamps) / len(timestamps)
            avg_active_time = datetime.fromtimestamp(average_timestamp)
            print(average_logout_time)
        else:
            avg_active_time = None

        if locked_time:
            timestamps = [entry.timestamp() for entry in locked_time]
            average_timestamp = sum(timestamps) / len(timestamps)
            avg_locked_time = datetime.fromtimestamp(average_timestamp)
            print(average_logout_time)
        else:
            avg_locked_time = None

        return render(request, 'employee_information/employee_avg_work_table.html',
                      {'average_login_time': average_login_time,
                       'emp': emp,
                       'average_logout_time': average_logout_time,
                       'avg_session_time': avg_session_time,
                       'avg_active_time': avg_active_time,
                       'avg_locked_time': avg_locked_time,
                       })
    except:
        return redirect('personal_info')


def help_desk(request):
    return render(request, 'employee_information/IT_help.html')


def send_mail_for_issue(request, email):
    try:
        subject = 'IT Help Desk : Issue Alert'
        message = f'Help for Issue as updated!!'
        email_from = request.user.email
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    except:
        messages.error(request, 'Error while Sending Email,kindly authenticate Gmail Account!!')


def save_IT_Help(request):
    issue = ITHelpDesk(user=request.user, issue_type=request.POST.get('issue-type'),
                       issue_description=request.POST.get('issue_description'),
                       priority=request.POST.get('priority'),
                       to_send_email=request.POST.get('to_email'))
    issue.save()

    email_id = ITHelpDesk.objects.filter(user=request.user).order_by('-id')[0]
    print('to send mail id:', email_id.to_send_email)
    send_mail_for_issue(request, email=email_id.to_send_email)
    return redirect('help_desk')


def view_leave(request):
    leave = LeaveType.objects.all()
    return render(request, 'employee_information/View_leave_type.html', {'leave': leave})


def update_leave(request, id):
    leave = LeaveType.objects.get(id=id)
    return render(request, 'employee_information/update_leave_type.html', {'leave': leave})


def save_leave_type(request, id):
    try:
        leave = LeaveType.objects.get(id=id)
        leave.leave_name = request.POST.get('leave_name')
        leave.total_allocation = request.POST.get('total_allocation')

        leave.save()
        return redirect('view_leave')
    except:
        return redirect('personal_info')


def save_new_leave(request):
    try:
        leave_type = LeaveType(leave_name=request.POST.get('leave_name'),
                               total_allocation=request.POST.get('total_allocation'))
        leave_type.save()
        return redirect('view_leave')
    except:
        return redirect('personal_info')
