from django.db import models
from datetime import date
from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from project.settings import DEFAULT_FROM_EMAIL
import calendar

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
    profile = models.ImageField(upload_to='Labour_profiles/', default='default-images/labour-default-profile.png')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='O')
    date_of_birth = models.DateField(default=date(2000, 1, 1))


class LabourWorker(models.Model):
    labour = models.ForeignKey(Labour, on_delete=models.CASCADE, related_name="workers")
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    labour_description = models.TextField()
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_days = models.IntegerField()
    present_days = models.IntegerField(default=0)  # Start with 0, will be calculated based on attendance
    paid = models.BooleanField(default=False)
    last_salary_update = models.DateField(default=now)

    def calculate_working_days(self, month, year):
        """Calculate total working days by excluding Sundays."""
        total_days_in_month = calendar.monthrange(year, month)[1]
        sunday_count = sum(1 for day in range(1, total_days_in_month + 1)
                           if calendar.weekday(year, month, day) == calendar.SUNDAY)
        working_days = total_days_in_month - sunday_count
        return working_days

    def set_default_total_days(self):
        """Set total_days for the current month, excluding Sundays."""
        current_month = self.joining_date.month
        current_year = self.joining_date.year
        self.total_days = self.calculate_working_days(current_month, current_year)


    def save(self, *args, **kwargs):
        # Automatically set total_days if not set
        if not self.total_days:
            self.set_default_total_days()

        super(LabourWorker, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.labour_description} - ₹{self.calculated_salary if self.calculated_salary else 0}"




class DailyAttendance(models.Model):
    worker = models.ForeignKey('LabourWorker', on_delete=models.CASCADE)
    date = models.DateField(default=now)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def save(self, *args, **kwargs):
        # Ensure attendance is updated correctly
        existing_attendance = DailyAttendance.objects.filter(worker=self.worker, date=self.date).first()

        if existing_attendance:
            if existing_attendance.status == 'Absent' and self.status == 'Present':
                self.worker.present_days += 1
            elif existing_attendance.status == 'Present' and self.status == 'Absent':
                self.worker.present_days -= 1
        else:
            if self.status == 'Present':
                self.worker.present_days += 1

        super().save(*args, **kwargs)

        # Ensure the salary is recalculated after attendance changes
        current_month = self.date.month
        current_year = self.date.year
        salary_record, _ = MonthlySalary.objects.get_or_create(
            worker=self.worker, month=current_month, year=current_year
        )
        salary_record.calculate_salary()

        if self.status == 'Absent':
            self.notify_worker()  # Call notify_worker method

    def notify_worker(self):
        """Notify the worker about their absence via email only."""
        message = f"Hello {self.worker.name}, you were marked absent on {self.date}. Please contact the owner if this is incorrect."
        
        # Send Email Notification
        if self.worker.email:
            send_mail(
                'Attendance Alert',
                message,
                'DEFAULT_FROM_EMAIL',  # Replace with your actual sender email
                [self.worker.email],
                fail_silently=True,
            )

    def __str__(self):
        return f"{self.worker.name} - {self.date} - {self.status}"



from django.core.mail import send_mail
from django.utils.timezone import now

class MonthlySalary(models.Model):
    worker = models.ForeignKey(LabourWorker, on_delete=models.CASCADE)
    month = models.IntegerField(default=now().month)
    year = models.IntegerField(default=now().year)
    calculated_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def calculate_salary(self):
        """Calculate salary based on attendance and working days (excluding Sundays)."""
        working_days = self.worker.calculate_working_days(self.month, self.year)

        present_days = DailyAttendance.objects.filter(
            worker=self.worker,
            date__year=self.year,
            date__month=self.month,
            status="Present"
        ).count()

        if working_days > 0:
            daily_wage = self.worker.salary / working_days
            self.calculated_salary = daily_wage * present_days
        else:
            self.calculated_salary = 0.00

        self.save()

        # Update LabourWorker with present days
        self.worker.present_days = present_days
        self.worker.save()

    def calculate_absent_days(self):
        """Calculate the number of absent days for this worker."""
        total_days = self.worker.calculate_working_days(self.month, self.year)
        present_days = DailyAttendance.objects.filter(
            worker=self.worker, 
            date__year=self.year, 
            date__month=self.month, 
            status="Present"
        ).count()
        return total_days - present_days

    def mark_paid(self):
        """Mark salary as paid and send an email notification."""
        self.paid = True
        self.payment_date = now().date()
        self.save()

        # Calculate absent days
        absent_days = self.calculate_absent_days()

        # Send an email to the worker
        if self.worker.email:
            subject = f"Salary Payment for {self.month}/{self.year}"
            message = f"""
            Hello {self.worker.name},

            Your salary for {self.month}/{self.year} has been processed.

            - Total Salary: ₹{self.calculated_salary}
            - Total Absent Days: {absent_days}
            - Paid on: {self.payment_date}

            Please reach out if you have any concerns.

            Regards,
            Labour Management
            """
            send_mail(subject, message, 'admin@example.com', [self.worker.email], fail_silently=False)

        # Create next month's salary record
        self.create_next_month_salary()

    def create_next_month_salary(self):
        """Create a salary record for the next month if it does not already exist."""
        next_month = self.month + 1 if self.month < 12 else 1
        next_year = self.year if self.month < 12 else self.year + 1

        if not MonthlySalary.objects.filter(worker=self.worker, month=next_month, year=next_year).exists():
            new_salary = MonthlySalary(worker=self.worker, month=next_month, year=next_year)
            new_salary.save()

    def __str__(self):
        return f"{self.worker.name} - {self.month}/{self.year} - Paid: {self.paid}"





