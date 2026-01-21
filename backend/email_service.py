import resend
from config import settings

resend.api_key = settings.RESEND_API_KEY


def send_password_reset_email(email: str, reset_token: str, user_name: str = None):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Passwort zurücksetzen</h2>
            <p>Hallo{f" {user_name}" if user_name else ""},</p>
            <p>Du hast eine Anfrage zum Zurücksetzen deines Passworts erhalten.</p>
            <p>Klicke auf den folgenden Button, um dein Passwort zurückzusetzen:</p>
            <a href="{reset_url}" class="button">Passwort zurücksetzen</a>
            <p>Oder kopiere diesen Link in deinen Browser:</p>
            <p style="word-break: break-all;">{reset_url}</p>
            <p>Dieser Link ist 1 Stunde lang gültig.</p>
            <p>Wenn du diese Anfrage nicht gestellt hast, kannst du diese E-Mail ignorieren.</p>
            <div class="footer">
                <p>Diese E-Mail wurde automatisch generiert. Bitte antworte nicht darauf.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "Passwort zurücksetzen",
            "html": html_content,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_welcome_email(email: str, user_name: str = None):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Willkommen!</h2>
            <p>Hallo{f" {user_name}" if user_name else ""},</p>
            <p>Dein Account wurde erfolgreich erstellt.</p>
            <p>Du kannst dich jetzt mit deiner E-Mail-Adresse und deinem Passwort anmelden.</p>
            <p><a href="{settings.FRONTEND_URL}/login">Zum Login</a></p>
            <div class="footer">
                <p>Diese E-Mail wurde automatisch generiert. Bitte antworte nicht darauf.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "Willkommen bei der Nutzerverwaltung",
            "html": html_content,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
