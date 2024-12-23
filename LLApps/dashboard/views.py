from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

from LLApps.dashboard.forms import contactRequestForm
from LLApps.labour.models import Labour, LabourPersonalInformation
from LLApps.master.helpers import validators, emails, tokens, sms, unique

from functools import wraps

import time
import jwt
import requests
# Create your views here.

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
    return render(request, 'dashboard/dashboard.html')
@login_required
def parties_view(request):
    labour_id = request.session['LL_labour_id']
    partyListAPI = f'https://llapps.pythonanywhere.com/api/parties/?labour={labour_id}'
    response = requests.get(partyListAPI)
    if response.status_code == 200:
        parties = response.json()
        return render(request, 'dashboard/parties.html', {'parties': parties})
    

@login_required
def tasks_view(request):
    return render(request, 'dashboard/tasks.html')
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