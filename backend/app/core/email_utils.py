from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import Optional
from app.core.config import settings
from app_logging.logger import logger

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_verification_email(email: str, verification_url: str) -> bool:
    """
    Send verification email to user
    """
    try:
        message = MessageSchema(
            subject="Complete your registration",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Welcome to our platform!</h2>
                    <p>To complete your registration, please click the link below:</p>
                    <p><a href="{verification_url}">Verify your email</a></p>
                    <p>If you did not request this registration, please ignore this email.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Verification email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False 