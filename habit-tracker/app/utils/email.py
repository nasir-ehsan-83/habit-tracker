from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib

from app.config import (
    logger,
    settings
)


async def send_email(
    email: str,
    verify_code: int
) -> None:
    try:

        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials are not set")
            return

        message = MIMEMultipart()
        message["From"] = settings.SMTP_USER
        message["To"] = email
        message["Subject"] = "🔐 Account Verification Code"

        html_body = f"""
        <!DOCTYPE html>
        <html dir="ltr" lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f6f9;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 500px;
                    margin: 40px auto;
                    background: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    overflow: hidden;
                    border: 1px solid #eef2f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #4f46e5, #6366f1);
                    padding: 30px 20px;
                    text-align: center;
                    color: #ffffff;
                }}
                .header h2 {{
                    margin: 0;
                    font-size: 22px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px;
                    text-align: center;
                    color: #334155;
                    line-height: 1.6;
                }}
                .code-container {{
                    background-color: #f8fafc;
                    border: 2px dashed #cbd5e1;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 25px 0;
                    display: inline-block;
                    letter-spacing: 6px;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #4f46e5;
                    font-family: monospace;
                }}
                .footer {{
                    background-color: #f8fafc;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #64748b;
                    border-top: 1px solid #e2e8f0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Identity Verification</h2>
                </div>
                <div class="content">
                    <p>Dear user, your request to receive a verification code was registered successfully.</p>
                    <p>Please use the following code to verify your identity:</p>
                    <div class="code-container">
                        <span class="code">{verify_code}</span>
                    </div>
                    <p style="font-size: 13px; color: #ef4444;">For security reasons, this code will expire in 5 minutes.</p>
                </div>
                <div class="footer">
                    <p>If you did not request this email, please ignore it.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            message,
            hostname = settings.SMTP_HOST,
            port = settings.SMTP_PORT,
            username = settings.SMTP_USER,
            password = settings.SMTP_PASSWORD,
            start_tls = True,
            timeout = 30,
            use_tls = False
        )
        
        logger.info(f"Verification email sent successfully to {email}")

    except aiosmtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check username/password.")
    
    except aiosmtplib.SMTPException as smtp_error:
        logger.error(f"SMTP error: {smtp_error}")
    
    except Exception as error:
        logger.error(f"Unexpected error in send_email: {error}", exc_info = True)