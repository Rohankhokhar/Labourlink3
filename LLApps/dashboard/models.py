from django.db import models
from LLApps.master.models import BaseModel
# Create your models here.

class ContactRequest(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    mobile = models.CharField(max_length=255)
    message = models.TextField()