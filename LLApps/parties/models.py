from django.db import models
from LLApps.master.models import BaseModel
from LLApps.labour.models import Labour

class PartiesDetail(BaseModel):
    labour = models.ForeignKey(Labour, on_delete=models.CASCADE, related_name='parties_details')
    firm_name = models.CharField(max_length=255)
    party_name = models.CharField(max_length=255)
    party_mobile = models.CharField(max_length=15)
    address = models.TextField()
    description = models.TextField()

    def __str__(self):
        return f"{self.party_name} - {self.firm_name}"

    class Meta:
        verbose_name = "Party Detail"
        verbose_name_plural = "Parties Details"
        ordering = ['party_name']


class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("partial", "Partially Paid"),
    ]
    party = models.ForeignKey(PartiesDetail, on_delete=models.CASCADE, related_name="tasks")
    task_description = models.TextField()
    assign_date = models.DateField(auto_now_add=True)
    complete_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    received_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    task_complete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.pending_amount = self.amount - self.received_amount  

        if self.pending_amount > 0 and self.received_amount > 0:
            self.status = "partial"
        elif self.pending_amount == 0:
            self.status = "completed"
        else:
            self.status = "pending"

        super().save(*args, **kwargs)

    @property
    def party_name(self):
       return self.party.party_name


    def __str__(self):
        return f"{self.task_description} ({self.status}) - {self.party_name}"
    
   



     