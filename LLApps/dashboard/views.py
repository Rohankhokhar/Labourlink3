from django.shortcuts import render

# Create your views here.
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

def parties_view(request):
    return render(request, 'dashboard/parties.html')

def tasks_view(request):
    return render(request, 'dashboard/tasks.html')

def payments_view(request):
    return render(request, 'dashboard/payments.html')

def profile_view(request):
    return render(request, 'dashboard/profiles.html')