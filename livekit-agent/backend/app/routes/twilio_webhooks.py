"""
Twilio webhook handlers for SIP call routing.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import Response
from typing import Dict, Any
from datetime import datetime
import os

from ..services.twilio_webhook_service import TwilioWebhookService
from ..utils.dependencies import get_twilio_webhook_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["twilio-webhooks"])

@router.post("/voice")
async def handle_voice_webhook(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle incoming voice calls from Twilio."""
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        # Extract call information
        call_info = {
            "call_sid": form_data.get("CallSid"),
            "from": form_data.get("From"),
            "to": form_data.get("To"),
            "call_status": form_data.get("CallStatus"),
            "direction": form_data.get("Direction"),
            "account_sid": form_data.get("AccountSid")
        }
        
        logger.info(f"Incoming voice call: {call_info}")
        
        # Generate TwiML response
        twiml_response = await webhook_service.handle_inbound_call(call_info)
        
        return Response(
            content=twiml_response,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling voice webhook: {e}")
        # Return error TwiML
        from twilio.twiml import VoiceResponse
        response = VoiceResponse()
        response.say("I'm sorry, there was an error processing your call. Please try again later.")
        return Response(
            content=str(response),
            media_type="application/xml"
        )

@router.post("/voice-fallback")
async def handle_voice_fallback(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle voice webhook fallback."""
    try:
        form_data = await request.form()
        call_info = {
            "call_sid": form_data.get("CallSid"),
            "from": form_data.get("From"),
            "to": form_data.get("To"),
            "call_status": form_data.get("CallStatus"),
            "direction": form_data.get("Direction")
        }
        
        logger.warning(f"Voice webhook fallback triggered: {call_info}")
        
        # Generate fallback TwiML
        twiml_response = await webhook_service.handle_voice_fallback(call_info)
        
        return Response(
            content=twiml_response,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling voice fallback: {e}")
        from twilio.twiml import VoiceResponse
        response = VoiceResponse()
        response.say("I'm sorry, I'm having trouble connecting you right now. Please try again later.")
        return Response(
            content=str(response),
            media_type="application/xml"
        )

@router.post("/status")
async def handle_status_webhook(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle call status updates from Twilio."""
    try:
        form_data = await request.form()
        
        status_info = {
            "call_sid": form_data.get("CallSid"),
            "call_status": form_data.get("CallStatus"),
            "from": form_data.get("From"),
            "to": form_data.get("To"),
            "direction": form_data.get("Direction"),
            "duration": form_data.get("Duration"),
            "start_time": form_data.get("StartTime"),
            "end_time": form_data.get("EndTime")
        }
        
        logger.info(f"Call status update: {status_info}")
        
        # Process status update
        await webhook_service.handle_status_update(status_info)
        
        return Response(content="OK", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error handling status webhook: {e}")
        return Response(content="ERROR", media_type="text/plain", status_code=500)

@router.post("/sms")
async def handle_sms_webhook(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle incoming SMS messages from Twilio."""
    try:
        form_data = await request.form()
        
        sms_info = {
            "message_sid": form_data.get("MessageSid"),
            "from": form_data.get("From"),
            "to": form_data.get("To"),
            "body": form_data.get("Body"),
            "num_media": form_data.get("NumMedia")
        }
        
        logger.info(f"Incoming SMS: {sms_info}")
        
        # Process SMS
        response = await webhook_service.handle_sms(sms_info)
        
        return Response(
            content=response,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling SMS webhook: {e}")
        from twilio.twiml import MessagingResponse
        response = MessagingResponse()
        response.message("I'm sorry, there was an error processing your message.")
        return Response(
            content=str(response),
            media_type="application/xml"
        )

@router.post("/sms-fallback")
async def handle_sms_fallback(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle SMS webhook fallback."""
    try:
        form_data = await request.form()
        sms_info = {
            "message_sid": form_data.get("MessageSid"),
            "from": form_data.get("From"),
            "to": form_data.get("To"),
            "body": form_data.get("Body")
        }
        
        logger.warning(f"SMS webhook fallback triggered: {sms_info}")
        
        # Generate fallback response
        response = await webhook_service.handle_sms_fallback(sms_info)
        
        return Response(
            content=response,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling SMS fallback: {e}")
        from twilio.twiml import MessagingResponse
        response = MessagingResponse()
        response.message("I'm sorry, I'm having trouble processing your message right now.")
        return Response(
            content=str(response),
            media_type="application/xml"
        )

@router.post("/recording")
async def handle_recording_webhook(
    request: Request,
    webhook_service: TwilioWebhookService = get_twilio_webhook_service()
):
    """Handle call recording webhooks from Twilio."""
    try:
        form_data = await request.form()
        
        recording_info = {
            "call_sid": form_data.get("CallSid"),
            "recording_sid": form_data.get("RecordingSid"),
            "recording_url": form_data.get("RecordingUrl"),
            "recording_status": form_data.get("RecordingStatus"),
            "recording_duration": form_data.get("RecordingDuration"),
            "recording_channels": form_data.get("RecordingChannels")
        }
        
        logger.info(f"Recording webhook: {recording_info}")
        
        # Process recording
        await webhook_service.handle_recording(recording_info)
        
        return Response(content="OK", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error handling recording webhook: {e}")
        return Response(content="ERROR", media_type="text/plain", status_code=500)

@router.get("/health")
async def twilio_health_check():
    """Health check endpoint for Twilio webhooks."""
    return {
        "status": "healthy",
        "service": "twilio-webhooks",
        "timestamp": datetime.utcnow().isoformat()
    }


