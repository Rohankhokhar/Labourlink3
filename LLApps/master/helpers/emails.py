from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def send_activation_email(request, labour):
    verification_url = f"http://{get_current_site(request).domain}/activate/{labour['labour_id']}/{labour['verification_token']}/"

    subject = 'Activate Your Account | LabourLink'
    html_message = render_to_string('dashboard/emails/labourVerification.html', {
        'user': labour,
        'verification_url': verification_url,
    })
    plain_message = strip_tags(html_message)  # Optional: Create a plain-text version

    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,  # From email
        [labour['email']],              # To email
        html_message=html_message,  # HTML message
    )