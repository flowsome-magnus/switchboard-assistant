"""
Twilio webhook service for handling SIP call routing and SMS.
"""

import logging
from typing import Dict, Any
from datetime import datetime
import os

from ...twilio_services.twiml_service import twiml_service
from ...db.supabase_client import get_db_client

logger = logging.getLogger(__name__)

class TwilioWebhookService:
    """Service for handling Twilio webhook events."""
    
    def __init__(self):
        self.db_client = get_db_client()
        self.twiml_service = twiml_service
    
    async def handle_inbound_call(self, call_info: Dict[str, Any]) -> str:
        """Handle incoming voice calls and route to LiveKit.
        
        Args:
            call_info: Call information from Twilio webhook
            
        Returns:
            TwiML response string
        """
        try:
            caller_phone = call_info.get("from", "")
            call_sid = call_info.get("call_sid", "")
            
            logger.info(f"Processing inbound call from {caller_phone}, SID: {call_sid}")
            
            # Create unique room name for this call
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caller_id = caller_phone.replace("+", "").replace("-", "") if caller_phone else "unknown"
            room_name = f"call_{timestamp}_{caller_id}"
            
            # Log the incoming call
            await self.db_client.log_call(
                caller_phone=caller_phone,
                status="incoming",
                room_id=room_name,
                notes=f"Incoming call from {caller_phone}"
            )
            
            # Generate TwiML to route to LiveKit
            twiml_response = self.twiml_service.create_inbound_twiml(room_name, caller_phone)
            
            logger.info(f"Generated TwiML for room: {room_name}")
            
            return twiml_response
            
        except Exception as e:
            logger.error(f"Error handling inbound call: {e}")
            # Return error TwiML
            from twilio.twiml import VoiceResponse
            response = VoiceResponse()
            response.say("I'm sorry, there was an error processing your call. Please try again later.")
            return str(response)
    
    async def handle_voice_fallback(self, call_info: Dict[str, Any]) -> str:
        """Handle voice webhook fallback.
        
        Args:
            call_info: Call information from Twilio webhook
            
        Returns:
            Fallback TwiML response string
        """
        try:
            caller_phone = call_info.get("from", "")
            
            logger.warning(f"Voice webhook fallback for call from {caller_phone}")
            
            # Log the fallback
            await self.db_client.log_call(
                caller_phone=caller_phone,
                status="failed",
                notes="Voice webhook fallback triggered"
            )
            
            # Return fallback TwiML
            from twilio.twiml import VoiceResponse
            response = VoiceResponse()
            response.say("I'm sorry, I'm having trouble connecting you right now. Please try again later.")
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling voice fallback: {e}")
            from twilio.twiml import VoiceResponse
            response = VoiceResponse()
            response.say("I'm sorry, there was an error. Please try again later.")
            return str(response)
    
    async def handle_status_update(self, status_info: Dict[str, Any]) -> None:
        """Handle call status updates from Twilio.
        
        Args:
            status_info: Status information from Twilio webhook
        """
        try:
            call_sid = status_info.get("call_sid")
            call_status = status_info.get("call_status")
            duration = status_info.get("duration")
            start_time = status_info.get("start_time")
            end_time = status_info.get("end_time")
            
            logger.info(f"Call status update: {call_sid} -> {call_status}")
            
            # Update call log in database
            # Note: In a real implementation, you'd need to match the call_sid to a record
            # For now, we'll log the status update
            
            if call_status in ["completed", "busy", "no-answer", "failed", "canceled"]:
                # Call ended, update the log
                await self.db_client.log_call(
                    caller_phone=status_info.get("from", "Unknown"),
                    duration=duration,
                    status="completed" if call_status == "completed" else "failed",
                    notes=f"Call ended with status: {call_status}"
                )
            
        except Exception as e:
            logger.error(f"Error handling status update: {e}")
    
    async def handle_sms(self, sms_info: Dict[str, Any]) -> str:
        """Handle incoming SMS messages.
        
        Args:
            sms_info: SMS information from Twilio webhook
            
        Returns:
            TwiML response string
        """
        try:
            from_phone = sms_info.get("from", "")
            to_phone = sms_info.get("to", "")
            message_body = sms_info.get("body", "")
            
            logger.info(f"Processing SMS from {from_phone}: {message_body}")
            
            # Check if this is from an employee
            employee = await self.db_client.get_employee_by_phone(from_phone)
            
            if employee:
                # This is an SMS from an employee
                # You could implement employee SMS commands here
                # For now, just acknowledge receipt
                
                from twilio.twiml import MessagingResponse
                response = MessagingResponse()
                response.message(f"Hi {employee.name}, I received your message. How can I help you?")
                return str(response)
            else:
                # This is an SMS from a caller
                # You could implement SMS-based message taking here
                
                from twilio.twiml import MessagingResponse
                response = MessagingResponse()
                response.message("Thank you for your message. I'll make sure it gets to the right person. For immediate assistance, please call us.")
                return str(response)
            
        except Exception as e:
            logger.error(f"Error handling SMS: {e}")
            from twilio.twiml import MessagingResponse
            response = MessagingResponse()
            response.message("I'm sorry, there was an error processing your message.")
            return str(response)
    
    async def handle_sms_fallback(self, sms_info: Dict[str, Any]) -> str:
        """Handle SMS webhook fallback.
        
        Args:
            sms_info: SMS information from Twilio webhook
            
        Returns:
            Fallback TwiML response string
        """
        try:
            from_phone = sms_info.get("from", "")
            
            logger.warning(f"SMS webhook fallback for message from {from_phone}")
            
            from twilio.twiml import MessagingResponse
            response = MessagingResponse()
            response.message("I'm sorry, I'm having trouble processing your message right now. Please try calling us instead.")
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling SMS fallback: {e}")
            from twilio.twiml import MessagingResponse
            response = MessagingResponse()
            response.message("I'm sorry, there was an error. Please try again later.")
            return str(response)
    
    async def handle_recording(self, recording_info: Dict[str, Any]) -> None:
        """Handle call recording webhooks.
        
        Args:
            recording_info: Recording information from Twilio webhook
        """
        try:
            call_sid = recording_info.get("call_sid")
            recording_url = recording_info.get("recording_url")
            recording_status = recording_info.get("recording_status")
            recording_duration = recording_info.get("recording_duration")
            
            logger.info(f"Recording webhook: {call_sid} -> {recording_status}")
            
            if recording_status == "completed" and recording_url:
                # Update call log with recording URL
                # Note: In a real implementation, you'd need to match the call_sid to a record
                logger.info(f"Call recording completed: {recording_url}")
                
                # You could store the recording URL in the database here
                # await self.db_client.update_call_log(call_sid, {"recording_url": recording_url})
            
        except Exception as e:
            logger.error(f"Error handling recording: {e}")
    
    async def create_outbound_call_twiml(self, employee_phone: str, room_name: str) -> str:
        """Create TwiML for outbound calls to employees.
        
        Args:
            employee_phone: Employee's phone number
            room_name: LiveKit room name for consultation
            
        Returns:
            TwiML response string
        """
        try:
            logger.info(f"Creating outbound call TwiML for {employee_phone} to room {room_name}")
            
            return self.twiml_service.create_outbound_twiml(employee_phone, room_name)
            
        except Exception as e:
            logger.error(f"Error creating outbound call TwiML: {e}")
            from twilio.twiml import VoiceResponse
            response = VoiceResponse()
            response.say("I'm sorry, there was an error connecting you. Please try again later.")
            return str(response)

