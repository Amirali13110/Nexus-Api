import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_reset_password_email(email: str, reset_link: str) -> None:
    params = {
        "from": settings.MAIL_FROM,
        "to": [email],
        "subject": "Reset your Nexus password",
        "html": (
            f"<p>We received a request to reset your password.</p>"
            f'<p><a href="{reset_link}">Click here to reset your password</a></p>'
            f"<p>This link expires in 30 minutes. If you didn't request this, ignore this email.</p>"
        ),
    }
    await resend.Emails.send_async(params)


async def send_email_change_confirmation(new_email: str, confirm_link: str) -> None:
    params = {
        "from": settings.MAIL_FROM,
        "to": [new_email],
        "subject": "Confirm your new Nexus email address",
        "html": (
            f"<p>Click the link below to confirm this as your new email address.</p>"
            f'<p><a href="{confirm_link}">Confirm new email</a></p>'
            f"<p>This link expires in 30 minutes. If you didn't request this, ignore this email.</p>"
        ),
    }
    print(params)
    await resend.Emails.send_async(params)
