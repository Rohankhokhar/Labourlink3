from django.db import models
from LLApps.master.models import BaseModel
from LLApps.labour.models import Labour
import uuid

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





# Task Model
class Task(BaseModel):
    party = models.ForeignKey(PartiesDetail, on_delete=models.CASCADE)
    task_description = models.TextField()
    assign_date = models.DateField(auto_now_add=True)
    complete_date = models.DateField(null=True, blank=True)  # If completed
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task: {self.task_description} - {self.party.party_name}"

# Payment Model
class Payment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="payments")
    received_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.pending_amount = self.task.amount - self.received_amount  # Auto-calculate pending amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.task.task_description} - Received: {self.received_amount}"
     