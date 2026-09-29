import django_rq
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()


def send_activation_email(user_id, activation_code):
    """
    Rendert und versendet die Aktivierungs-E-Mail mit dem Verifizierungscode.

    Wird als Hintergrund-Job über `enqueue_activation_email` ausgeführt, daher
    wird hier die User-ID statt eines kompletten User-Objekts entgegengenommen:
    Job-Argumente werden in Redis zwischengespeichert und müssen serialisierbar
    sein.
    """
    user = User.objects.get(id=user_id)
    context = {"user": user, "activation_code": activation_code}
    html_content = render_to_string("app/activation_email.html", context)
    text_content = strip_tags(html_content)
    subject = "Aktiviere deinen Account"
    msg = EmailMultiAlternatives(subject, text_content, None, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def enqueue_activation_email(user_id, activation_code):
    """
    Reiht den Versand der Aktivierungs-E-Mail in die Standard-Queue ein,
    statt den Request auf den E-Mail-Versand warten zu lassen.
    """
    django_rq.enqueue(send_activation_email, user_id, activation_code)
