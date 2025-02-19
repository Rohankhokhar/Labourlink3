from django import forms
from LLApps.parties.models import Task
from LLApps.dashboard.models import ContactRequest

class contactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['first_name', 'last_name', 'email', 'mobile', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'Email'}),
            'mobile': forms.TextInput(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'Mobile'}),
            'message': forms.Textarea(attrs={'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'Message', 'rows': 4}),
        }


class TaskForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Task.STATUS_CHOICES,
        widget=forms.RadioSelect,
        required=False  # Don't force the user to choose a status manually
    )

    class Meta:
        model = Task
        fields = [
            "task_description",
            "complete_date",
            "amount",
            "received_amount",
            "payment_date",
            "status",
            "task_complete",
        ]
        exclude = ["assign_date", "party", "status"]  # Do not include 'party' or 'status' here, as they'll be set in the view

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_received_amount(self):
        received_amount = self.cleaned_data.get('received_amount')
        if received_amount < 0:
            raise forms.ValidationError("Received amount cannot be negative.")
        return received_amount

