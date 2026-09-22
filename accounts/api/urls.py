from django.urls import path

from accounts.api.views import (
    AccountActivateView,
    RegisterView,
    ResendVerificationCodeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "account-verification/",
        AccountActivateView.as_view(),
        name="account-verification",
    ),
    path(
        "resend-verification-code/",
        ResendVerificationCodeView.as_view(),
        name="resend-verification-code",
    ),
]
