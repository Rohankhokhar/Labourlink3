from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from LLApps.dashboard.forms import contactRequestForm
from LLApps.labour.models import Labour
from LLApps.master.helpers import validators, emails, tokens

import time
import jwt
# Create your views here.

def login_view(request):
    return render(request, 'dashboard/login.html')

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
    return render(request, 'dashboard/forgot-password.html')

def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

def parties_view(request):
    return render(request, 'dashboard/parties.html')

def tasks_view(request):
    return render(request, 'dashboard/tasks.html')

def payments_view(request):
    return render(request, 'dashboard/payments.html')

def contact_view(request):
    if request.method == 'POST':
        form = contactRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'dashboard/contact.html', {'form': form,'success_message': 'Your message has been sent successfully'})
    form = contactRequestForm()
    print(form)
    return render(request, 'dashboard/contact.html', {'form': form})

def profile_view(request):
    return render(request, 'dashboard/profiles.html')