from django.contrib import admin

from .models import CustomUser, EmailVerificationCode


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("email", "first_name", "last_name")
    exclude = (
        "groups",
        "user_permissions",
        "is_superuser",
        "is_staff",
        "password",
        "username",
    )
    readonly_fields = (
        "date_joined",
        "last_login",
        "agb_accepted",
        "agb_accepted_at",
        "privacy_accepted",
        "privacy_accepted_at",
    )


class EmailVerificationCodeAdmin(admin.ModelAdmin):
    verbose_name = "E-Mail-Verifizierungscode"
    list_display = (
        "user",
        "code",
        "created_at",
        "expires_at",
    )
    search_fields = ("user__email",)


admin.site.register(EmailVerificationCode, EmailVerificationCodeAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
