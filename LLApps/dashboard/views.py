from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse , HttpResponse

from LLApps.dashboard.forms import contactRequestForm
from LLApps.labour.models import Labour, LabourPersonalInformation , LabourWorker , DailyAttendance , MonthlySalary
from LLApps.master.helpers import validators, emails, tokens, sms, unique
from LLApps.parties.models import PartiesDetail , Task 
from .forms import TaskForm
from functools import wraps
from django.utils.timezone import now
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from datetime import datetime
from django.db.models import Count, Q
from django.db.models import Sum

import time
import jwt
import requests
import json
# Create your views here.

LOCAL_SERVER = 'http://127.0.0.1:8000'

def get_labour_from_session(request):
    llid = Labour.objects.get(llid=request.session['LL_labour_id'])
    personal_info = LabourPersonalInformation.objects.get(labour_id=request.session['LL_labour_id'])
    if llid:
        return llid, personal_info
    return None

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'LL_labour_id' not in request.session:
            messages.error(request, 'You need to be logged in to access this page.')
            return redirect('login_view')
        return view_func(request, *args, **kwargs)
    return wrapper

def login_view(request):
    if request.method == 'POST':
        email_ = request.POST.get('email')
        password_ = request.POST.get('password')

        if not Labour.objects.filter(email=email_).exists():
            messages.error(request, 'Invalid email or password')
            return redirect('login_view')
        else:
            labour_ = Labour.objects.get(email=email_)
            labourPersonalInfo = LabourPersonalInformation.objects.get(labour_id=labour_.llid)
            if not check_password(password_, labour_.password):
                messages.error(request, 'Invalid email or password')
                return redirect('login_view')
            else:
                request.session['LL_labour_id'] = str(labour_.llid)
                request.session['LL_name'] = labour_.first_name + " " + labour_.last_name
                request.session['LL_profile'] = str(labourPersonalInfo.profile.url)
                messages.success(request, "Now, you are logged in.")
                return redirect('dashboard_view')
    return render(request, 'dashboard/login.html')

def logout(request):
    if 'LL_labour_id' in request.session:
        del request.session['LL_labour_id']
        del request.session['LL_name']
    messages.success(request, 'You have been logged out.')
    return redirect('login_view')

def register_view(request):
    if request.method == 'POST':
        first_name_ = request.POST['first_name']
        last_name_ = request.POST['last_name']
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        password_ = request.POST['password']
        confirm_password_ = request.POST['confirm_password']
        terms_and_condition_ = request.POST['terms_and_condition']

        if terms_and_condition_ == 'on':
            terms_and_condition_ = True
        else:
            terms_and_condition_ = False

        is_email_vaild = validators.is_valid_email(email_)

        if not is_email_vaild[0]:
            messages.error(request, is_email_vaild[1])
            return redirect('register_view')
        
        if Labour.objects.filter(email=email_).exists():
            messages.error(request, 'Email already exists')
            return redirect('register_view')
        
        is_valid_mobile = validators.is_valid_mobile_number(mobile_)

        if not is_valid_mobile[0]:
            messages.error(request, is_valid_mobile[1])
            return redirect('register_view')
        
        is_valid_password = validators.is_valid_password(password_)

        if not is_valid_password[0]:
            messages.error(request, is_valid_password[1])
            return redirect('register_view')
        
        if not password_ == confirm_password_:
            messages.error(request, 'Password and confirm password do not match')
            return redirect('register_view')

        new_labour = Labour.objects.create(
            first_name=first_name_,
            last_name=last_name_,
            email=email_,
            mobile=mobile_,
            password=make_password(password_),
            terms_and_condition=terms_and_condition_
        )
        new_labour.save()

        labour_profile = LabourPersonalInformation.objects.create(
            labour_id = new_labour.llid
        )
        labour_profile.save()
        labour = {
                'labour_id':new_labour.llid,
                'name': new_labour.first_name + " " + new_labour.last_name,
                'email': email_,
                'verification_token':tokens.create_jwt_token(labour_id=str(new_labour.llid))
            }
        emails.send_activation_email(request, labour)
        messages.success(request, 'Registration successful! Please check your email to activate your account.')
        return redirect('login_view')
    return render(request, 'dashboard/register.html')

def activate_account(request, labour_id, token):
    try:
        # Decode the token
        payload = tokens.verify_jwt_token(token)
        
        # Check if the customer ID in the payload matches the customer ID in the URL
        if payload['labour_id'] != labour_id:
            messages.error(request, "Invalid confirmation link.")
            return redirect('some_error_page')  # Redirect to an error page

        # Check if the token is expired
        if payload['exp'] < time.time():
            messages.error(request, "Confirmation link has expired.")
            return redirect('some_error_page')  # Redirect to an error page

        # Find the customer and activate the account
        customer = Labour.objects.get(llid=labour_id)
        customer.is_active = True  # Assuming you have an is_active field
        customer.save()

        messages.success(request, "Your account has been activated successfully.")
        return redirect('login_view')  # Redirect to the login page

    except jwt.ExpiredSignatureError:
        messages.error(request, "Confirmation link has expired.")
        return redirect('some_error_page')  # Redirect to an error page
    except jwt.InvalidTokenError:
        messages.error(request, "Invalid confirmation link.")
        return redirect('some_error_page')  # Redirect to an error page
    except Labour.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('some_error_page')  # Redirect to an error page

def some_error_page(request):
    return render(request, 'web/some_error_page.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email_ = request.POST.get('email')
        otp_ = unique.generate_otp()
        data = {
            'message': f'Your OTP for password reset is: {otp_}. Please use this code to reset your password.',
            'to_email': email_
        }
        emails.send_password_reset_email(data)
        get_labour = Labour.objects.get(email=email_)
        get_labour.otp = otp_
        get_labour.save()
        messages.success(request, 'OTP sent successfully. Please check your email for the OTP.')
        return render(request, 'dashboard/otp-verification.html', {'email': email_})
    return render(request, 'dashboard/forgot-password.html')

def verify_otp_view(request):
    if request.method == 'POST':
        email_ = request.POST.get('email')
        otp_ = request.POST.get('otp')
        new_password_ = request.POST.get('new_password')
        confirm_password_ = request.POST.get('confirm_password')
        get_labour = Labour.objects.get(email=email_)
        if get_labour.otp == otp_:
            print(email_, otp_,get_labour.otp , new_password_, confirm_password_)
            if new_password_ != confirm_password_:
                messages.error(request, 'New password and confirm password do not match')
                return render(request, 'dashboard/otp-verification.html', {'email': email_})
            else:
                is_valid_password = validators.is_valid_password(new_password_)
                if not is_valid_password[0]:
                    messages.error(request, is_valid_password[1])
                    return render(request, 'dashboard/otp-verification.html', {'email': email_})
                else:
                    get_labour.password = make_password(new_password_)
                    get_labour.save()
                    messages.success(request, 'Password reset successfully')
                    return redirect('login_view')
        else:
            messages.error(request, 'Invalid OTP')
            return render(request, 'dashboard/otp-verification.html', {'email': email_})
                
    print("Bhar")
    return render(request, 'dashboard/otp-verification.html')



@login_required
def dashboard_view(request):
    labour_id_ = request.session['LL_labour_id']
    total_parties = PartiesDetail.objects.filter(labour_id=labour_id_).count()
    total_task = Task.objects.count()
    total_labours = LabourWorker.objects.count()  
    total_payment = Task.objects.filter()
    context = {
        'total_parties': total_parties,
        'total_task' : total_task,
        'total_labour': total_labours,
    }
    return render(request, 'dashboard/dashboard.html', context)

# @login_required
# def parties_view(request):
#     labour_id = request.session['LL_labour_id']
#     partyListAPI = f'{LOCAL_SERVER}/api/parties/?labour={labour_id}'
#     response = requests.get(partyListAPI)
#     if response.status_code == 200:
#         parties = response.json()
#         return render(request, 'dashboard/parties.html', {'parties': parties})
#     return render(request, 'dashboard/parties.html')

@login_required
def parties_view(request):
    labour_id = request.session.get('LL_labour_id')
    parties = PartiesDetail.objects.filter(labour_id=labour_id)
    return render(request, 'dashboard/parties.html', {'parties': parties})

def party_tasks_view(request, party_id):
    """View to list all tasks for a particular party with filter."""
    party = get_object_or_404(PartiesDetail, llid=party_id)
    filter_type = request.GET.get("filter", "all")  # Default is "all"

    # Filtering tasks based on selected filter
    tasks = Task.objects.filter(party=party)
    if filter_type == "completed":
        tasks = tasks.filter(task_complete=True)
    elif filter_type == "not_completed":
        tasks = tasks.filter(task_complete=False)
    elif filter_type == "pending":
        tasks = tasks.filter(pending_amount__gt=0)

    return render(
        request,
        "dashboard/parties_task.html",
        {"party": party, "tasks": tasks, "filter_type": filter_type},
    )

@csrf_exempt
@login_required
def add_new_party(request):
    if request.method == 'POST':
        firm_name_ = request.POST.get('firm_name', '').strip()
        party_name_ = request.POST.get('party_name', '').strip()
        party_mobile_ = request.POST.get('party_mobile', '').strip()
        address_ = request.POST.get('address', '').strip()
        description_ = request.POST.get('description', '').strip()
        labour_id = request.session.get('LL_labour_id')

        # Create and save a new Party instance
        PartiesDetail.objects.create(
            firm_name=firm_name_,
            party_name=party_name_,
            party_mobile=party_mobile_,
            address=address_,
            description=description_,
            labour_id=labour_id
        )

        messages.success(request, 'Party added successfully.')
        return redirect('parties_view')
    
    return render(request, 'dashboard/parties_create.html')

@login_required
def edit_party(request, party_id):
    party = get_object_or_404(PartiesDetail, llid=party_id)
    
    if request.method == 'POST':
        party.firm_name = request.POST.get('firm_name', party.firm_name)
        party.party_name = request.POST.get('party_name', party.party_name)
        party.party_mobile = request.POST.get('party_mobile', party.party_mobile)
        party.address = request.POST.get('address', party.address)
        party.description = request.POST.get('description', party.description)
        party.save()

        messages.success(request, 'Party updated successfully.')
        return redirect('parties_view')
    
    return render(request, 'dashboard/edit_party.html', {'party': party})

@login_required
def delete_party(request, party_id):
    party = get_object_or_404(PartiesDetail, llid=party_id)
    party.delete()
    messages.success(request, 'Party deleted successfully.')
    return redirect('parties_view')




# @login_required
# def add_new_party(request):
#     if request.method == 'POST':
#         firm_name_ = request.POST.get('firm_name', '').strip()
#         party_name_ = request.POST.get('party_name', '').strip()
#         party_mobile_ = request.POST.get('party_mobile', '').strip()
#         address_ = request.POST.get('address', '').strip()
#         description_ = request.POST.get('description', '').strip()

#         partyListAPI = f'{LOCAL_SERVER}/api/parties/'
            
#         party_data = {
#             "firm_name": firm_name_,
#             "party_name": party_name_,
#             "party_mobile": party_mobile_,
#             "address": address_,
#             "description": description_,
#             "labour": request.session.get('LL_labour_id') 
#         }

#         response = requests.post(partyListAPI, json=party_data)

#         if response.status_code == 201:
#             messages.success(request, 'Party added successfully.')
#             return redirect('parties_view')

#         # ❌ API request failed, return an error response
#         messages.error(request, 'Failed to add party. Please try again.')
#         return redirect('parties_view')  # Redirect to the form again with an error message

#     # ❌ Invalid request method (not POST)
#     return render(request, 'dashboard/parties_create.html')

# @login_required
# def edit_party(request, party_id):
#     partyDetailAPI = f'{LOCAL_SERVER}/api/party/{party_id}'

#     # Handle POST request (Update the party)
#     if request.method == 'POST':
#         # Safely retrieve form data
#         firm_name_ = request.POST.get('firm_name', '')
#         party_name_ = request.POST.get('party_name', '')
#         party_mobile_ = request.POST.get('party_mobile', '')
#         address_ = request.POST.get('address', '')
#         description_ = request.POST.get('description', '')

#         party_data = {
#             "firm_name": firm_name_,
#             "party_name": party_name_,
#             "party_mobile": party_mobile_,
#             "address": address_,
#             "description": description_,
#             "labour": request.session['LL_labour_id']  # Assuming there's a labour ID in the session
#         }

#         try:
#             # Send PUT request to update the party
#             response = requests.put(partyDetailAPI, json=party_data)
#             print(response)
#             if response.status_code == 200:
#                 messages.success(request, 'Party updated successfully.')
#                 return redirect('parties_view')
#             else:
#                 print(f"Error: {response.status_code}, {response.text}")
#                 messages.error(request, 'Failed to update party. Please try again.')
#         except requests.exceptions.RequestException as e:
#             print(f"Request Exception: {e}")
#             messages.error(request, 'Error connecting to the server.')

#         # Redirect back to the edit page in case of failure
#         return redirect('edit_party', party_id=party_id)

#     # Handle GET request (Fetch party details)
#     try:
#         response = requests.get(partyDetailAPI)
#         if response.status_code == 200:
#             party = response.json()
#             return render(request, 'dashboard/edit_party.html', {'party': party})
#         else:
#             messages.error(request, 'Failed to fetch party details.')
#     except requests.exceptions.RequestException as e:
#         print(f"Request Exception: {e}")
#         messages.error(request, 'Error connecting to the server.')

#     # Redirect to the parties list if party details are unavailable
#     return redirect('parties_view')
    

# @login_required
# def delete_party(request, party_id):
#         partyDetailAPI = f'{LOCAL_SERVER}/api/party/{party_id}'
#         response = requests.delete(partyDetailAPI)

#         if response.status_code == 204:
#             messages.success(request, 'Party deleted successfully.')
#         else:
#             messages.error(request, 'Failed to delete the party. Please try again later.')

#         return redirect('parties_view')

@login_required
def payments_view(request):
    return render(request, 'dashboard/payments.html')
@login_required
def contact_view(request):
    if request.method == 'POST':
        form = contactRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'dashboard/contact.html', {'form': form,'success_message': 'Your message has been sent successfully'})
    form = contactRequestForm()
    print(form)
    return render(request, 'dashboard/contact.html', {'form': form})
@login_required
def profile_view(request):
    context = {
        'get_labour': get_labour_from_session(request)[0],
        'get_labour_personal_info': get_labour_from_session(request)[1]
    }
    print(context)
    return render(request, 'dashboard/profiles.html', context)

@login_required
def update_profile_view(request):
    get_labour, get_labour_personal_info = get_labour_from_session(request)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        gender = request.POST.get('gender', '').strip()
        dob = request.POST.get('dob', '').strip()
        profile_image = request.FILES.get('profile_image', None)  # Handle file input

        try:
            # Update Labour details
            get_labour.first_name = first_name
            get_labour.last_name = last_name
            get_labour.email = email
            get_labour.mobile = mobile
            get_labour.save()
            
            # Update Personal Info details
            get_labour_personal_info.gender = gender
            get_labour_personal_info.date_of_birth = dob
            
            if profile_image:
                get_labour_personal_info.profile = profile_image  # Update profile image if uploaded
                
            
            get_labour_personal_info.save()
            request.session['LL_name'] = get_labour.first_name + " " + get_labour.last_name
            request.session['LL_profile'] = str(get_labour_personal_info.profile.url)

            # Success message
            messages.success(request, 'Profile updated successfully!')
            return redirect('update_profile_view')
        
        except Exception as e:
            messages.error(request, f"An error occurred while updating the profile: {str(e)}")
            return redirect('update_profile_view')
    context = {
        'get_labour': get_labour_from_session(request)[0],
        'get_labour_personal_info': get_labour_from_session(request)[1]
    }
    return render(request, 'dashboard/update-profile.html', context)



def tasks_view(request):
    party_id = request.session.get('LL_labour_id')  # Get Labour ID from session

    if party_id:
        tasks = Task.objects.filter(party__labour_id=party_id)
    filter_type = request.GET.get('filter', 'all')

    # Fetch tasks based on filter
    # tasks = Task.objects.all()

    if filter_type == 'completed':
        tasks = tasks.filter(task_complete=True)
    elif filter_type == 'not_completed':
        tasks = tasks.filter(task_complete=False)
    elif filter_type == 'pending':
        tasks = tasks.filter(pending_amount__gt=0)

    # Task counts
    incomplete_task_count = Task.objects.filter(task_complete=False).count()
    completed_task_count = Task.objects.filter(task_complete=True).count()
    pending_amount_task_count = Task.objects.filter(pending_amount__gt=0).count()
    total_pending_amount = Task.objects.aggregate(Sum("pending_amount"))["pending_amount__sum"] or 0

    return render(request, "dashboard/task_read.html", {
        "tasks": tasks,
        "incomplete_task_count": incomplete_task_count,
        "completed_task_count": completed_task_count,
        "pending_amount_task_count": pending_amount_task_count,
        "total_pending_amount": total_pending_amount,
        "filter_type": filter_type,  # Pass filter type to template
    })



@login_required
def add_task(request, party_id):
    party = get_object_or_404(PartiesDetail, pk=party_id)
    task = None  # Initialize task to None before checking for POST request

    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)  # Create the task but don't save yet
            task.party = party  # Set the related party automatically
            task.save()  # Save the task to the database
            messages.success(request, "Task added successfully.")
            return redirect("parties_view")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TaskForm()  # Initialize an empty form

    return render(request, "dashboard/tasks.html", {"party": party, "form": form})

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    task.delete()
    
    return redirect('tasks_view') 

def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()  # Save the updated task
            return redirect('tasks_view')  # Redirect to the task view page after saving
    else:
        form = TaskForm(instance=task)  # Pre-fill the form with the task's data

    return render(request, 'dashboard/task_update.html', {'form': form, 'task': task})


def labour_read(request):
    current_month = now().month
    current_year = now().year

    # workers = LabourWorker.objects.all()
    labour_id = request.session.get('LL_labour_id')
    workers = LabourWorker.objects.filter(labour_id=labour_id)

    for worker in workers:
        # Ensure MonthlySalary exists for this worker
        salary_record, _ = MonthlySalary.objects.get_or_create(
            worker=worker, month=current_month, year=current_year,
            defaults={'calculated_salary': 0, 'paid': False, 'payment_date': None}
        )

        # Ensure salary is calculated
        salary_record.calculate_salary()

        # Attach correct salary info to the worker for display
        worker.present_days = DailyAttendance.objects.filter(
            worker=worker, date__month=current_month, date__year=current_year, status="Present"
        ).count()
        worker.calculated_salary = salary_record.calculated_salary
        worker.salary_paid = salary_record.paid
        worker.payment_date = salary_record.payment_date

    return render(request, 'dashboard/labour_read.html', {"data": workers})






# Create Labour Worker View (Using Python code)
def create_labour_worker(request):
    if request.method == 'POST':
        # Get the data from the POST request (You can change it as per your request data)
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        labour_description = request.POST.get('labour_description')
        joining_date_str = request.POST.get('joining_date') 
        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date()
        salary = request.POST.get('salary')

        # Get the Labour object (Assuming you know the Labour id, here we use the first one as an example)
        labour = Labour.objects.first()  # Change this as per your actual case

        # Create the new LabourWorker object
        new_worker = LabourWorker(
            labour=labour,
            name=name,
            mobile_number=mobile_number,
            email=email,
            labour_description=labour_description,
            joining_date=joining_date,
            salary=salary,
            total_days=0,  # Default value, you can adjust this as needed
            present_days=0  # Default value, you can adjust this as needed
        )
        # Save the new LabourWorker to the database
        new_worker.save()

        # Optionally, redirect to a success page or return a response
        return redirect('labour_read')

    return render(request, 'dashboard/labour_create.html')  # Render the form to create a new worker

def labour_update(request, worker_id):
    # Get the worker object from the database
    worker = get_object_or_404(LabourWorker, id=worker_id)

    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        labour_description = request.POST.get('labour_description')
        joining_date_str = request.POST.get('joining_date')
        salary = request.POST.get('salary')

        # Convert the date safely
        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date() if joining_date_str else worker.joining_date

        # Update the worker object
        worker.name = name
        worker.mobile_number = mobile_number
        worker.email = email
        worker.labour_description = labour_description
        worker.joining_date = joining_date
        worker.salary = float(salary) if salary else worker.salary  # Convert salary safely

        # Save changes
        worker.save()

        return redirect('labour_read')  # Redirect to the worker list

    # Pass 'worker' to the template
    return render(request, 'dashboard/labour_update.html', {'worker': worker}) 
        


def labour_delete(request , worker_id):
    labour = get_object_or_404(LabourWorker, id=worker_id)

    labour.delete()

    return redirect('labour_read')


def mark_attendance(request, worker_id):
    worker = get_object_or_404(LabourWorker, id=worker_id)
    today = now().date()  # Get the current date

    if request.method == "POST":
        date_str = request.POST.get("date", str(today))  # Get date as string
        date = datetime.strptime(date_str, "%Y-%m-%d").date()  # Get date from form or default to today
        status = request.POST.get("status")  # Get attendance status

        if status not in ["Present", "Absent"]:
            messages.error(request, "Invalid status selected.")
            return render(request, "mark_attendance.html", {"worker": worker, "today": today})

        # Check if attendance already exists
        existing_attendance = DailyAttendance.objects.filter(worker=worker, date=date).first()

        if existing_attendance:
            existing_attendance.status = status  # Update existing attendance
            existing_attendance.save()
            messages.success(request, "Attendance updated successfully!")
        else:
            # Create new attendance record
            DailyAttendance.objects.create(worker=worker, date=date, status=status)
            messages.success(request, "Attendance recorded successfully!")

        return redirect("labour_read")

    return render(request, "dashboard/mark_attendance.html", {"worker": worker, "today": today})


def generate_salary(request, worker_id):
    """Generate or update the monthly salary record for a worker."""
    worker = get_object_or_404(LabourWorker, id=worker_id)
    current_month = now().month
    current_year = now().year

    # Check if a salary record already exists
    salary_record, created = MonthlySalary.objects.get_or_create(
        worker=worker,
        month=current_month,
        year=current_year
    )

    # Calculate salary based on attendance
    salary_record.calculate_salary()
    salary_record.save()

    if created:
        messages.success(request, f"Salary record for {worker.name} ({current_month}/{current_year}) created successfully!")
    else:
        messages.info(request, f"Salary record for {worker.name} updated.")

    return redirect("salary_list")


def salary_list(request):
    """Display all worker salaries."""
    salaries = MonthlySalary.objects.all().order_by("-year", "-month")
    return render(request, "dashboard/labour_salary.html", {"salaries": salaries})

def pay_salary(request, worker_id):
    current_month = now().month
    current_year = now().year

    salary_record = get_object_or_404(MonthlySalary, worker_id=worker_id, month=current_month, year=current_year)

    # ✅ Ensure salary is calculated before marking as paid
    if salary_record.calculated_salary == 0:
        salary_record.calculate_salary()

    if not salary_record.paid:
        salary_record.mark_paid()
        messages.success(request, f"Salary for {salary_record.worker.name} marked as paid!")
    else:
        messages.warning(request, "This salary is already marked as paid.")

    return redirect("labour_read")



def undo_salary_payment(request, worker_id):
    """Undo salary payment and mark it as unpaid."""
    current_month = now().month
    current_year = now().year

    salary_record = get_object_or_404(
        MonthlySalary, worker_id=worker_id, month=current_month, year=current_year
    )

    if salary_record.paid:  # Only allow undoing if it's already paid
        salary_record.paid = False
        salary_record.payment_date = None  # Remove payment date
        salary_record.save()

        messages.success(request, f"Payment for {salary_record.worker.name} has been undone.")
    else:
        messages.warning(request, "This salary is already unpaid.")

    return redirect("labour_read")













