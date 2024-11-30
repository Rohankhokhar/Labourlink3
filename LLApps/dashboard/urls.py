from django.urls import path
from LLApps.dashboard.views import *

urlpatterns = [
    path('', dashboard_view, name='dashboard_view'),
    path('parties/', parties_view, name='parties_view'),
    path('tasks/', tasks_view, name='tasks_view'),
    path('payments/', payments_view, name='payments_view'),
    path('profile/', profile_view, name='profile_view'),
]