"""Email service for sending notifications and verification emails."""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@copytrading.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            if not self.smtp_user or not self.smtp_password:
                logger.warning("SMTP credentials not configured. Email not sent.")
                # In development, log the email content
                logger.info(f"EMAIL TO: {to_email}")
                logger.info(f"SUBJECT: {subject}")
                logger.info(f"CONTENT: {html_content}")
                return False

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add both plain text and HTML versions
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(self, email: str, verification_token: str) -> bool:
        """Send email verification link."""
        verify_url = f"{self.frontend_url}/verify-email?token={verification_token}"

        subject = "Verify Your Email Address"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #0db9f2; color: white; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome to Copy Trading Platform!</h2>
                <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                <p><a href="{verify_url}" class="button">Verify Email</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{verify_url}</p>
                <p><strong>This link will expire in 24 hours.</strong></p>
                <div class="footer">
                    <p>If you didn't create an account, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"Verify your email by visiting: {verify_url}\nThis link expires in 24 hours."

        return self.send_email(email, subject, html_content, text_content)

    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset link."""
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"

        subject = "Reset Your Password"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #0db9f2; color: white; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Reset Your Password</h2>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p><a href="{reset_url}" class="button">Reset Password</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <div class="footer">
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"Reset your password by visiting: {reset_url}\nThis link expires in 1 hour."

        return self.send_email(email, subject, html_content, text_content)

    def send_login_alert(self, email: str, ip_address: str, timestamp: datetime) -> bool:
        """Send login alert for new device/IP."""
        subject = "New Login Detected"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>New Login Detected</h2>
                <div class="alert">
                    <p><strong>Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                    <p><strong>IP Address:</strong> {ip_address}</p>
                </div>
                <p>If this was you, you can safely ignore this email.</p>
                <p>If you didn't recognize this activity, please secure your account immediately by changing your password.</p>
            </div>
        </body>
        </html>
        """
        text_content = f"New login detected at {timestamp} from IP: {ip_address}"

        return self.send_email(email, subject, html_content, text_content)

    def send_welcome_email(self, email: str, name: Optional[str] = None) -> bool:
        """Send welcome email after verification."""
        display_name = name or email.split('@')[0]

        subject = "Welcome to Copy Trading Platform!"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #0db9f2; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome, {display_name}!</h2>
                <p>Your email has been verified successfully. You can now start using the Copy Trading Platform.</p>
                <p><a href="{self.frontend_url}/dashboard" class="button">Go to Dashboard</a></p>
                <h3>Getting Started:</h3>
                <ol>
                    <li>Connect your broker account (Zerodha or Dhan)</li>
                    <li>Set up your trading profile and risk preferences</li>
                    <li>Start copying trades from expert traders</li>
                </ol>
                <p>If you have any questions, feel free to reach out to our support team.</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Welcome {display_name}! Your email is verified. Start trading now: {self.frontend_url}/dashboard"

        return self.send_email(email, subject, html_content, text_content)

    def generate_verification_token(self) -> str:
        """Generate a secure verification token."""
        return secrets.urlsafe_urlsafe(32)

    def generate_reset_token(self) -> str:
        """Generate a secure password reset token."""
        return secrets.urlsafe_urlsafe(32)

    def get_verification_expiry(self) -> datetime:
        """Get verification token expiry (24 hours)."""
        return datetime.utcnow() + timedelta(hours=24)

    def get_reset_expiry(self) -> datetime:
        """Get reset token expiry (1 hour)."""
        return datetime.utcnow() + timedelta(hours=1)


# Singleton instance
email_service = EmailService()
