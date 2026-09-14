from django.urls import path

from accounts.api.views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]
