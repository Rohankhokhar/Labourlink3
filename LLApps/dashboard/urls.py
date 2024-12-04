from django.urls import path
from LLApps.dashboard.views import *

urlpatterns = [
    path('', login_view, name='login_view'),
    path('register/', register_view, name='register_view'),
    path('activate/<str:labour_id>/<str:token>/', activate_account, name='activate_account'),
    path('forgot-password/', forgot_password_view, name='forgot_password_view'),
    path('dashboard/', dashboard_view, name='dashboard_view'),
    path('parties/', parties_view, name='parties_view'),
    path('tasks/', tasks_view, name='tasks_view'),
    path('payments/', payments_view, name='payments_view'),
    path('contact/', contact_view, name='contact_view'),
    path('profile/', profile_view, name='profile_view'),
]