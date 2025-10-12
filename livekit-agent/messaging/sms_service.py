"""
SMS Service for message delivery via Twilio
==========================================
Handles SMS message delivery to employees.
"""

import os
import logging
from typing import Dict, Any, Optional
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)

class SMSService:
    """Service for sending SMS messages via Twilio."""
    
    def __init__(self):
        """Initialize SMS service with Twilio credentials."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.sms_number = os.getenv("TWILIO_SMS_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.sms_number]):
            logger.warning("Twilio SMS credentials not configured. SMS functionality will be disabled.")
            self.client = None
        else:
            try:
                self.client = TwilioClient(self.account_sid, self.auth_token)
                logger.info("SMS service initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
    
    async def send_message(
        self, 
        to_phone: str, 
        message: str, 
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an SMS message.
        
        Args:
            to_phone: Recipient phone number
            message: Message content
            from_phone: Sender phone number (defaults to configured SMS number)
            
        Returns:
            Dictionary with delivery status and details
        """
        if not self.client:
            return {
                "success": False,
                "error": "SMS service not configured",
                "message_id": None
            }
        
        try:
            from_number = from_phone or self.sms_number
            
            # Send the SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully: {message_obj.sid} to {to_phone}")
            
            return {
                "success": True,
                "message_id": message_obj.sid,
                "status": message_obj.status,
                "to": to_phone,
                "from": from_number,
                "error": None
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}",
                "message_id": None
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_phone}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message_id": None
            }
    
    async def send_message_notification(
        self, 
        employee_phone: str, 
        caller_phone: str, 
        message_text: str,
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send a message notification to an employee.
        
        Args:
            employee_phone: Employee's phone number
            caller_phone: Caller's phone number
            message_text: The message content
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        formatted_message = f"""
Hi {employee_name},

You have a new message from {caller_phone}:

"{message_text}"

This message was taken by our switchboard assistant. Please respond when convenient.

Best regards,
Your Switchboard Assistant
"""
        
        return await self.send_message(employee_phone, formatted_message)
    
    async def send_transfer_notification(
        self, 
        employee_phone: str, 
        caller_info: Dict[str, Any],
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send a transfer notification to an employee.
        
        Args:
            employee_phone: Employee's phone number
            caller_info: Information about the caller
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        caller_name = caller_info.get('name', 'Unknown Caller')
        caller_phone = caller_info.get('phone', 'Unknown Number')
        caller_reason = caller_info.get('reason', 'No specific reason provided')
        
        formatted_message = f"""
Hi {employee_name},

You have an incoming call transfer:

Caller: {caller_name}
Phone: {caller_phone}
Reason: {caller_reason}

Please prepare to receive the call.

Best regards,
Your Switchboard Assistant
"""
        
        return await self.send_message(employee_phone, formatted_message)
    
    async def send_availability_reminder(
        self, 
        employee_phone: str, 
        employee_name: str = "Employee"
    ) -> Dict[str, Any]:
        """Send an availability reminder to an employee.
        
        Args:
            employee_phone: Employee's phone number
            employee_name: Employee's name for personalization
            
        Returns:
            Delivery result
        """
        formatted_message = f"""
Hi {employee_name},

This is a reminder that you're currently marked as available in our switchboard system. If your availability has changed, please update your status.

Best regards,
Your Switchboard Assistant
"""
        
        return await self.send_message(employee_phone, formatted_message)
    
    async def check_message_status(self, message_id: str) -> Dict[str, Any]:
        """Check the status of a sent message.
        
        Args:
            message_id: Twilio message SID
            
        Returns:
            Message status information
        """
        if not self.client:
            return {
                "success": False,
                "error": "SMS service not configured"
            }
        
        try:
            message = self.client.messages(message_id).fetch()
            
            return {
                "success": True,
                "message_id": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except TwilioException as e:
            logger.error(f"Error checking message status for {message_id}: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error checking message status for {message_id}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

# Global instance
sms_service = SMSService()

