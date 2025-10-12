"""
TwiML Service for Twilio SIP Integration
======================================
Handles TwiML webhook responses for SIP call routing to LiveKit.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from twilio.twiml import VoiceResponse
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)

class TwiMLService:
    """Service for generating TwiML responses and managing Twilio SIP calls."""
    
    def __init__(self):
        """Initialize TwiML service with Twilio credentials."""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.sip_trunk_id = os.getenv("TWILIO_SIP_TRUNK_ID")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not configured. SIP functionality will be disabled.")
            self.client = None
        else:
            try:
                self.client = TwilioClient(self.account_sid, self.auth_token)
                logger.info("TwiML service initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.client = None
    
    def create_inbound_twiml(self, room_name: str, caller_phone: str = "") -> str:
        """Create TwiML response for inbound calls to route to LiveKit.
        
        Args:
            room_name: LiveKit room name to connect the call to
            caller_phone: Caller's phone number (if available)
            
        Returns:
            TwiML XML string
        """
        try:
            response = VoiceResponse()
            
            # Create unique room name if not provided
            if not room_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                caller_id = caller_phone.replace("+", "").replace("-", "") if caller_phone else "unknown"
                room_name = f"call_{timestamp}_{caller_id}"
            
            # Get LiveKit SIP endpoint URL
            livekit_url = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.com")
            livekit_sip_endpoint = f"{livekit_url}/sip"
            
            # Create SIP dial to LiveKit
            dial = response.dial()
            
            # Add SIP URI for LiveKit
            sip_uri = f"sip:{room_name}@{livekit_sip_endpoint}"
            dial.sip(sip_uri)
            
            # Add fallback if SIP fails
            response.say("I'm sorry, I'm having trouble connecting you right now. Please try again later.")
            
            logger.info(f"Created TwiML for room: {room_name}, caller: {caller_phone}")
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error creating inbound TwiML: {e}")
            # Return error TwiML
            response = VoiceResponse()
            response.say("I'm sorry, there was an error processing your call. Please try again later.")
            return str(response)
    
    def create_outbound_twiml(self, employee_phone: str, room_name: str) -> str:
        """Create TwiML response for outbound calls to employees.
        
        Args:
            employee_phone: Employee's phone number to call
            room_name: LiveKit room name for the consultation
            
        Returns:
            TwiML XML string
        """
        try:
            response = VoiceResponse()
            
            # Get LiveKit SIP endpoint URL
            livekit_url = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.com")
            livekit_sip_endpoint = f"{livekit_url}/sip"
            
            # Create SIP dial to LiveKit consultation room
            dial = response.dial()
            
            # Add SIP URI for LiveKit consultation room
            sip_uri = f"sip:{room_name}@{livekit_sip_endpoint}"
            dial.sip(sip_uri)
            
            # Add fallback if employee doesn't answer
            response.say("The employee is not available right now. Please try again later.")
            
            logger.info(f"Created outbound TwiML for employee: {employee_phone}, room: {room_name}")
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error creating outbound TwiML: {e}")
            # Return error TwiML
            response = VoiceResponse()
            response.say("I'm sorry, there was an error connecting you. Please try again later.")
            return str(response)
    
    async def make_outbound_call(
        self, 
        to_phone: str, 
        twiml_url: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an outbound call via Twilio.
        
        Args:
            to_phone: Phone number to call
            twiml_url: URL that returns TwiML for the call
            from_phone: Phone number to call from (defaults to configured number)
            
        Returns:
            Call result with SID and status
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not configured",
                "call_sid": None
            }
        
        try:
            from_number = from_phone or self.phone_number
            
            call = self.client.calls.create(
                to=to_phone,
                from_=from_number,
                url=twiml_url,
                method='POST'
            )
            
            logger.info(f"Outbound call initiated: {call.sid} to {to_phone}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "to": to_phone,
                "from": from_number,
                "error": None
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error making outbound call to {to_phone}: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}",
                "call_sid": None
            }
        except Exception as e:
            logger.error(f"Unexpected error making outbound call to {to_phone}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "call_sid": None
            }
    
    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """Get the status of a Twilio call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            Call status information
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not configured"
            }
        
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "to": call.to,
                "from": call.from_,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "duration": call.duration,
                "error": None
            }
            
        except TwilioException as e:
            logger.error(f"Error getting call status for {call_sid}: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error getting call status for {call_sid}: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def hangup_call(self, call_sid: str) -> bool:
        """Hang up a Twilio call.
        
        Args:
            call_sid: Twilio call SID
            
        Returns:
            True if call was hung up successfully
        """
        if not self.client:
            return False
        
        try:
            call = self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} hung up successfully")
            return True
            
        except TwilioException as e:
            logger.error(f"Error hanging up call {call_sid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error hanging up call {call_sid}: {e}")
            return False
    
    def create_sip_trunk_config(self) -> Dict[str, Any]:
        """Create SIP trunk configuration for Twilio.
        
        Returns:
            SIP trunk configuration dictionary
        """
        return {
            "friendly_name": "LiveKit Switchboard SIP Trunk",
            "voice_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/voice",
            "voice_method": "POST",
            "voice_fallback_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/voice-fallback",
            "voice_fallback_method": "POST",
            "status_callback": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/status",
            "status_callback_method": "POST",
            "cnam_lookup_enabled": True,
            "recording": {
                "recording_track": "both",
                "recording_status_callback": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/recording"
            }
        }
    
    def create_phone_number_config(self) -> Dict[str, Any]:
        """Create phone number configuration for Twilio.
        
        Returns:
            Phone number configuration dictionary
        """
        return {
            "voice_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/voice",
            "voice_method": "POST",
            "voice_fallback_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/voice-fallback",
            "voice_fallback_method": "POST",
            "status_callback": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/status",
            "status_callback_method": "POST",
            "sms_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/sms",
            "sms_method": "POST",
            "sms_fallback_url": f"{os.getenv('WEBHOOK_BASE_URL', 'https://your-domain.com')}/twilio/sms-fallback",
            "sms_fallback_method": "POST"
        }

# Global instance
twiml_service = TwiMLService()

