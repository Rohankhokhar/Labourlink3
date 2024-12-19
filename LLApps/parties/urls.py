from django.urls import path
from LLApps.parties.views import PartiesListAPI, PartiesDetailAPI

urlpatterns = [
    path('parties/', PartiesListAPI, name='PartiesListAPI'),
    path('party/<uuid:party_id>', PartiesDetailAPI, name='PartiesDetailAPI')
]