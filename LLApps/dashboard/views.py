from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from LLApps.dashboard.forms import contactRequestForm


from LLApps.labour.models import Labour

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

        new_labour = Labour.objects.create(
            first_name=first_name_,
            last_name=last_name_,
            email=email_,
            mobile=mobile_,
            password=make_password(password_),
            terms_and_condition=terms_and_condition_
        )
        new_labour.save()
        return render(request, 'dashboard/login.html')

       

    return render(request, 'dashboard/register.html')

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