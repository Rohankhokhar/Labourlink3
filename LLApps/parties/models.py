from django.db import models
from LLApps.master.models import BaseModel
from LLApps.labour.models import Labour
# Create your models here.


class PartiesDetail(models.Model):
    labour = models.ForeignKey(Labour, on_delete=models.CASCADE, related_name='parties_details')
    firm_name = models.CharField(max_length=255)
    party_name = models.CharField(max_length=255)
    party_mobile = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.party_name} - {self.firm_name}"
    
    class Meta:
        verbose_name = "Party Detail"
        verbose_name_plural = "Parties Details"
        ordering = ['party_name']