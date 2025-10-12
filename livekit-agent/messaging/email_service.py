"""
Email Service for message delivery
=================================
Handles email message delivery via SMTP or SendGrid.
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import SendGrid (optional)
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending email messages via SMTP or SendGrid."""
    
    def __init__(self):
        """Initialize email service with configured provider."""
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SMTP_USER") or os.getenv("FROM_EMAIL", "noreply@company.com")
        
        # Initialize SendGrid if available and configured
        if SENDGRID_AVAILABLE and self.sendgrid_api_key:
            try:
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
                self.use_sendgrid = True
                logger.info("Email service initialized with SendGrid")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
                self.sendgrid_client = None
                self.use_sendgrid = False
        else:
            self.sendgrid_client = None
            self.use_sendgrid = False
        
        # Check SMTP configuration
        if all([self.smtp_host, self.smtp_user, self.smtp_password]):
            self.smtp_configured = True
            if not self.use_sendgrid:
                logger.info("Email service initialized with SMTP")
        else:
            self.smtp_configured = False
            if not self.use_sendgrid:
                logger.warning("Email service not configured. Email functionality will be disabled.")
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        from_email: Optional[str] = None,
        is_html: bool = False
    ) -> Dict[str, Any]:
        """Send an email message.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Email content
            from_email: Sender email address
            is_html: Whether the message is HTML format
            
        Returns:
            Dictionary with delivery status and details
        """
        from_addr = from_email or self.from_email
        
        if self.use_sendgrid:
            return await self._send_via_sendgrid(to_email, subject, message, from_addr, is_html)
        elif self.smtp_configured:
            return await self._send_via_smtp(to_email, subject, message, from_addr, is_html)
        else:
            return {
                "success": False,
                "error": "Email service not configured",
                "message_id": None
            }
    
    async def _send_via_sendgrid(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        from_email: str,
        is_html: bool
    ) -> Dict[str, Any]:
        """Send email via SendGrid."""
        try:
            from_email_obj = Email(from_email)
            to_email_obj = To(to_email)
            
            if is_html:
                content = Content("text/html", message)
            else:
                content = Content("text/plain", message)
            
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            
            response = self.sendgrid_client.send(mail)
            
            logger.info(f"Email sent via SendGrid: {response.status_code} to {to_email}")
            
            return {
                "success": True,
                "message_id": response.headers.get('X-Message-Id'),
                "status_code": response.status_code,
                "to": to_email,
                "from": from_email,
                "provider": "sendgrid",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"SendGrid error sending email to {to_email}: {e}")
            return {
                "success": False,
                "error": f"SendGrid error: {str(e)}",
                "message_id": None,
                "provider": "sendgrid"
            }
    
    async def _send_via_smtp(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        from_email: str,
        is_html: bool
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Add content
            if is_html:
                content = MIMEText(message, 'html')
            else:
                content = MIMEText(message, 'plain')
            
            msg.attach(content)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            message_id = msg.get('Message-ID', f"<{datetime.now().timestamp()}@company.com>")
            
            logger.info(f"Email sent via SMTP to {to_email}")
            
            return {
                "success": True,
                "message_id": message_id,
                "to": to_email,
                "from": from_email,
                "provider": "smtp",
                "error": None
            }
            
        except Exception as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}",
                "message_id": None,
                "provider": "smtp"
            }
    
    async def send_message_notification(
        self, 
        employee_email: str, 
        caller_phone: str, 
        message_text: str,
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send a message notification email to an employee.
        
        Args:
            employee_email: Employee's email address
            caller_phone: Caller's phone number
            message_text: The message content
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        subject = f"New Message from {caller_phone}"
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>New Message</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .message {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #007cba; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>New Message for {employee_name}</h2>
        </div>
        
        <p>You have received a new message from <strong>{caller_phone}</strong>:</p>
        
        <div class="message">
            <p><em>"{message_text}"</em></p>
        </div>
        
        <p>This message was taken by our switchboard assistant. Please respond when convenient.</p>
        
        <div class="footer">
            <p>Best regards,<br>Your Switchboard Assistant</p>
            <p><small>This is an automated message. Please do not reply to this email.</small></p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Hi {employee_name},

You have a new message from {caller_phone}:

"{message_text}"

This message was taken by our switchboard assistant. Please respond when convenient.

Best regards,
Your Switchboard Assistant
"""
        
        return await self.send_email(
            employee_email, 
            subject, 
            html_message, 
            is_html=True
        )
    
    async def send_transfer_notification(
        self, 
        employee_email: str, 
        caller_info: Dict[str, Any],
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send a transfer notification email to an employee.
        
        Args:
            employee_email: Employee's email address
            caller_info: Information about the caller
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        caller_name = caller_info.get('name', 'Unknown Caller')
        caller_phone = caller_info.get('phone', 'Unknown Number')
        caller_reason = caller_info.get('reason', 'No specific reason provided')
        
        subject = f"Incoming Call Transfer from {caller_name}"
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Incoming Call Transfer</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #e8f4fd; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .caller-info {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Incoming Call Transfer</h2>
        </div>
        
        <p>Hi {employee_name},</p>
        
        <p>You have an incoming call transfer:</p>
        
        <div class="caller-info">
            <p><strong>Caller:</strong> {caller_name}</p>
            <p><strong>Phone:</strong> {caller_phone}</p>
            <p><strong>Reason:</strong> {caller_reason}</p>
        </div>
        
        <p>Please prepare to receive the call.</p>
        
        <div class="footer">
            <p>Best regards,<br>Your Switchboard Assistant</p>
            <p><small>This is an automated message. Please do not reply to this email.</small></p>
        </div>
    </div>
</body>
</html>
"""
        
        return await self.send_email(
            employee_email, 
            subject, 
            html_message, 
            is_html=True
        )
    
    async def send_availability_reminder(
        self, 
        employee_email: str, 
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send an availability reminder email to an employee.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        subject = "Availability Status Reminder"
        
        message = f"""
Hi {employee_name},

This is a reminder that you're currently marked as available in our switchboard system. If your availability has changed, please update your status.

Best regards,
Your Switchboard Assistant
"""
        
        return await self.send_email(employee_email, subject, message)

# Global instance
email_service = EmailService()


