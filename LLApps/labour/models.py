from django.db import models


from LLApps.master.models import BaseModel
# Create your models here.

class Labour(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    mobile= models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    terms_and_condition = models.BooleanField(default=False)
    otp = models.CharField(default='000000', max_length=6)

    def __str__(self):
        return self.first_name + " " + self.last_name + "-" + str(self.llid)
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(Labour, self).save(*args, **kwargs)

class LabourPersonalInformation(BaseModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    labour = models.ForeignKey(Labour, on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='Labour_profiles/')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()


