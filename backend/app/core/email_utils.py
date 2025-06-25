from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

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


async def send_password_reset_email(email: str, reset_url: str) -> bool:
    """
    Send password reset email to user
    """
    try:
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>You have requested to reset your password. Click the link below to proceed:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>If you did not request this password reset, please ignore this email.</p>
                    <p>This link will expire in 1 hour.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False


async def send_email_change_confirmation(email: str, confirmation_url: str) -> bool:
    """
    Send email change confirmation email to user
    """
    try:
        message = MessageSchema(
            subject="Email Change Confirmation",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Email Change Confirmation</h2>
                    <p>You have requested to change your email address. Click the link below to confirm:</p>
                    <p><a href="{confirmation_url}">Confirm Email Change</a></p>
                    <p>If you did not request this email change, please ignore this email.</p>
                    <p>This link will expire in 1 hour.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email change confirmation sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email change confirmation to {email}: {str(e)}")
        return False


async def send_email_change_code(email: str, code: str) -> bool:
    """
    Send email change confirmation code to user
    """
    try:
        message = MessageSchema(
            subject="Email Change Confirmation Code",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <h2>Email Change Confirmation</h2>
                    <p>You have requested to change your email address. Use the code below to confirm:</p>
                    <h3 style="font-size: 24px; color: #4CAF50; text-align: center; padding: 20px; background: #f5f5f5; border-radius: 8px; margin: 20px 0;">{code}</h3>
                    <p>If you did not request this email change, please ignore this email.</p>
                    <p>This code will expire in 1 hour.</p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email change code sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email change code to {email}: {str(e)}")
        return False 