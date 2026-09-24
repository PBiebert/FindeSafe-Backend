from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_activation_email(user, activation_code):
    context = {"user": user, "activation_code": activation_code}
    html_content = render_to_string("app/activation_email.html", context)
    text_content = strip_tags(html_content)
    subject = "Aktiviere deinen Account"
    msg = EmailMultiAlternatives(subject, text_content, None, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
