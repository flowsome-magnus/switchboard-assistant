"""
Warm Transfer Implementation for LiveKit Switchboard Agent
========================================================
Handles warm transfers between callers and employees with consultation rooms.
Uses single agent approach with room hopping for simplicity.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Optional, Any
from livekit import rtc, api
from livekit.agents import AgentSession, RunContext, Agent
from livekit.agents.llm import function_tool
from sip_call_routing import sip_call_router

logger = logging.getLogger(__name__)

class WarmTransferManager:
    """Manages warm transfer operations following LiveKit's official warm transfer pattern.
    
    This implementation follows the LiveKit documentation for agent-assisted warm transfers:
    https://docs.livekit.io/sip/transfer-warm/
    """
    
    def __init__(self):
        self.active_transfers: Dict[str, Dict[str, Any]] = {}
        self.consultation_rooms: Dict[str, str] = {}  # transfer_id -> room_id
        self.caller_rooms: Dict[str, str] = {}  # transfer_id -> caller_room_id
        self.sip_trunk_id: Optional[str] = os.getenv("LIVEKIT_SIP_TRUNK_ID")
    
    async def create_consultation_room(
        self, 
        employee_phone: str, 
        caller_info: Dict[str, Any],
        caller_room_id: str
    ) -> str:
        """Create a consultation room for the employee.
        
        Args:
            employee_phone: Phone number of the employee to call
            caller_info: Information about the caller
            caller_room_id: ID of the caller's current room
            
        Returns:
            Room ID for the consultation
        """
        try:
            # Generate unique room ID for consultation
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            employee_id = employee_phone.replace('+', '').replace('-', '')
            room_id = f"consultation_{timestamp}_{employee_id}"
            
            # Store consultation room info
            self.consultation_rooms[room_id] = room_id
            self.caller_rooms[room_id] = caller_room_id
            
            logger.info(f"Created consultation room: {room_id} for employee {employee_phone}")
            
            return room_id
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error creating consultation room: {e}")
            raise
    
    async def call_employee_via_sip(
        self, 
        employee_phone: str, 
        room_id: str,
        session: AgentSession,
        ctx: Optional[RunContext] = None
    ) -> bool:
        """Make an outbound SIP call to the employee using LiveKit's CreateSIPParticipant API.
        
        This follows the official LiveKit warm transfer documentation:
        https://docs.livekit.io/sip/transfer-warm/
        
        Args:
            employee_phone: Phone number to call
            room_id: Room to connect the employee to
            session: Current agent session
            ctx: RunContext for accessing LiveKit API
            
        Returns:
            True if call was initiated successfully
        """
        try:
            logger.info(f"Initiating LiveKit SIP call to {employee_phone} for room {room_id}")

            if not self.sip_trunk_id:
                logger.error("LIVEKIT_SIP_TRUNK_ID not configured - cannot make SIP calls")
                return False

            # Create LiveKit API client with proper resource management
            lkapi = api.LiveKitAPI(
                url=os.getenv("LIVEKIT_URL"),
                api_key=os.getenv("LIVEKIT_API_KEY"),
                api_secret=os.getenv("LIVEKIT_API_SECRET"),
            )

            try:
                # Use LiveKit's CreateSIPParticipant API as per documentation
                sip_request = api.CreateSIPParticipantRequest(
                    sip_trunk_id=self.sip_trunk_id,
                    sip_call_to=employee_phone,
                    room_name=room_id,
                    participant_identity="Supervisor",
                    wait_until_answered=True,
                )

                logger.info(f"Creating SIP participant with request: {sip_request}")

                # Make the SIP call using LiveKit API
                sip_participant = await lkapi.sip.create_sip_participant(sip_request)

                logger.info(f"LiveKit SIP call to {employee_phone} initiated successfully: {sip_participant}")
                return True

            except (api.TwirpError, api.RpcError) as sip_error:
                logger.error(f"LiveKit SIP call failed: {sip_error}")
                return False
            finally:
                # Always close the API client
                await lkapi.aclose()

        except (ValueError, KeyError) as e:
            logger.error(f"Error calling employee via LiveKit SIP: {e}")
            return False
    

    async def stop_supervisor_session(self) -> bool:
        """Stop the supervisor session and clean up.
        
        Returns:
            True if session stopped successfully
        """
        try:
            logger.info("Stopping supervisor session...")
            
            # Stop the supervisor session if it exists
            if hasattr(self, 'supervisor_session') and self.supervisor_session:
                await self.supervisor_session.aclose()
                logger.info("Supervisor session closed")
            
            # Disconnect from supervisor room if it exists
            if hasattr(self, 'supervisor_room') and self.supervisor_room:
                await self.supervisor_room.disconnect()
                logger.info("Supervisor room disconnected")
            
            logger.info("Supervisor session stopped successfully")
            return True
            
        except (AttributeError, RuntimeError) as e:
            logger.error(f"Error stopping supervisor session: {e}")
            return False

    async def generate_consultation_room_token(self, room_name: str) -> str:
        """Generate a token for joining the consultation room.
        
        Args:
            room_name: Name of the consultation room
            
        Returns:
            JWT token for room access
        """
        try:
            from livekit import api
            
            # Create token for consultation room
            token = api.AccessToken(
                api_key=os.getenv("LIVEKIT_API_KEY"),
                api_secret=os.getenv("LIVEKIT_API_SECRET"),
            )
            
            # Grant room join permissions
            token.with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))
            
            # Set identity for the transfer agent
            token.with_identity("transfer-agent")
            token.with_name("Transfer Agent")
            
            # Set token expiration (5 minutes)
            from datetime import timedelta
            token.with_ttl(timedelta(seconds=300))
            
            return token.to_jwt()
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error generating consultation room token: {e}")
            raise

    async def disconnect_agent_from_consultation(
        self, 
        room_id: str,
        session: AgentSession
    ) -> bool:
        """Remove the agent from the consultation room after transfer.
        
        Args:
            room_id: Consultation room ID
            session: Current agent session
            
        Returns:
            True if agent was disconnected successfully
        """
        try:
            logger.info(f"Disconnecting agent from consultation room {room_id}")
            
            # Remove agent from the consultation room
            # In a real implementation, you would:
            # 1. Leave the consultation room
            # 2. Clean up any resources
            # 3. Update room state
            
            # Clean up consultation room reference
            if room_id in self.consultation_rooms:
                del self.consultation_rooms[room_id]
            if room_id in self.caller_rooms:
                del self.caller_rooms[room_id]
            
            logger.info(f"Agent disconnected from consultation room {room_id}")
            return True
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error disconnecting agent: {e}")
            return False
    
    async def execute_warm_transfer(
        self,
        employee_phone: str,
        caller_info: Dict[str, Any],
        caller_room_id: str,
        session: AgentSession,
        ctx: Optional[RunContext] = None,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """Execute a warm transfer flow using LiveKit rooms and SIP trunks.
        
        LiveKit Flow:
        1. Create consultation room
        2. Agent joins consultation room
        3. Make outbound SIP call to employee via LiveKit SIP trunk
        4. Employee joins consultation room
        5. Employee consultation (accept/reject/message)
        6. If accept: Transfer employee to caller room
        7. Agent leaves consultation room
        
        Args:
            employee_phone: Phone number of the employee
            caller_info: Information about the caller
            caller_room_id: ID of the caller's current room
            session: Current agent session
            
        Returns:
            Transfer result with status and details
        """
        transfer_id = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Starting LiveKit warm transfer {transfer_id} to {employee_phone}")
            
            # Step 1: Create consultation room
            consultation_room_id = await self.create_consultation_room(
                employee_phone, caller_info, caller_room_id
            )
            
            # Step 2: Create a simple consultation message for the supervisor
            consultation_message = f"""
Hello! I'm facilitating a warm transfer for you. Here's what the caller needs:

{conversation_history}

The caller is currently on hold and waiting to be connected to you. 
Please let me know if you're ready to take this call by saying 'yes' or 'no'.
"""
            
            logger.info(f"Consultation message prepared for supervisor in room: {consultation_room_id}")
            
            # Step 3: Make outbound SIP call to employee via LiveKit SIP trunk
            call_success = await self.call_employee_via_sip(
                employee_phone, consultation_room_id, session, ctx
            )
            
            # Step 3.5: Create supervisor room and connect directly
            try:
                # Create supervisor room connection (following LiveKit example pattern)
                supervisor_room = rtc.Room()
                token = await self.generate_consultation_room_token(consultation_room_id)
                
                logger.info(f"Connecting to supervisor room: {consultation_room_id}")
                await supervisor_room.connect(os.getenv("LIVEKIT_URL"), token)
                
                # Create supervisor session
                from livekit.agents import AgentSession
                from livekit.plugins import openai
                
                supervisor_session = AgentSession(
                    llm=openai.realtime.RealtimeModel(voice="alloy", temperature=0.3),
                )
                
                # Create supervisor agent with conversation history
                supervisor_agent = SupervisorAgent(conversation_history=conversation_history)
                supervisor_agent.consultation_room_id = consultation_room_id
                supervisor_agent.caller_room_id = caller_room_id
                supervisor_agent.session_manager = self
                
                # Start supervisor session
                await supervisor_session.start(
                    agent=supervisor_agent,
                    room=supervisor_room
                )
                
                # Store references for later use
                self.supervisor_room = supervisor_room
                self.supervisor_session = supervisor_session
                self.supervisor_agent = supervisor_agent
                
            except (api.TwirpError, api.RpcError, ValueError) as agent_error:
                logger.error(f"Error starting supervisor session: {agent_error}")
            
            if not call_success:
                return {
                    "transfer_id": transfer_id,
                    "status": "failed",
                    "reason": "Could not reach employee",
                    "room_id": consultation_room_id,
                    "message": "I'm sorry, I couldn't reach the employee. Would you like me to take a message instead?"
                }
            
            # Step 4: Wait for employee to join consultation room and respond
            # Wait for SupervisorAgent to get employee's decision using asyncio.Event
            employee_response = None
            max_wait_time = 60  # 60 seconds timeout

            try:
                # Wait for the decision event with timeout
                await asyncio.wait_for(self.supervisor_agent.decision_event.wait(), timeout=max_wait_time)
                employee_response = self.supervisor_agent.employee_decision
                logger.info(f"Employee decision received: {employee_response}")
            except asyncio.TimeoutError:
                employee_response = "reject"  # Timeout - treat as rejection
                logger.warning(f"Employee decision timeout after {max_wait_time} seconds")
            
            if employee_response == "accept":
                # Step 5: Transfer employee to caller room using MoveParticipant API
                logger.info(f"Employee accepted transfer {transfer_id}")
                
                # Move supervisor from consultation room to caller room
                lkapi = api.LiveKitAPI(
                    url=os.getenv("LIVEKIT_URL"),
                    api_key=os.getenv("LIVEKIT_API_KEY"),
                    api_secret=os.getenv("LIVEKIT_API_SECRET"),
                )

                try:
                    # Get employee identity from consultation room
                    employee_identity = await sip_call_router.get_employee_identity(consultation_room_id)
                    if not employee_identity:
                        employee_identity = "Supervisor"  # fallback

                    move_request = api.MoveParticipantRequest(
                        room=consultation_room_id,
                        identity=employee_identity,
                        destination_room=caller_room_id,
                    )

                    # Move the supervisor to the caller room
                    await lkapi.room.move_participant(move_request)
                    logger.info(f"Moved {employee_identity} from {consultation_room_id} to {caller_room_id}")

                except (api.TwirpError, api.RpcError) as move_error:
                    logger.error(f"Error moving supervisor: {move_error}")
                finally:
                    # Always close the API client
                    await lkapi.aclose()
                
                # Step 6: Stop supervisor session and cleanup
                await self.stop_supervisor_session()
                await self.disconnect_agent_from_consultation(consultation_room_id, session)
                
                # Clean up participant identities
                await sip_call_router.cleanup_participant_identities(consultation_room_id)
                
                return {
                    "transfer_id": transfer_id,
                    "status": "completed",
                    "reason": "Employee accepted the call - transfer completed",
                    "room_id": consultation_room_id,
                    "message": "I'm connecting you to the employee now. Please hold on."
                }
            
            elif employee_response == "reject":
                # Handle rejection
                logger.info(f"Employee rejected transfer {transfer_id}")
                
                # Stop supervisor session and cleanup
                await self.stop_supervisor_session()
                await self.disconnect_agent_from_consultation(consultation_room_id, session)
                await sip_call_router.cleanup_participant_identities(consultation_room_id)
                
                return {
                    "transfer_id": transfer_id,
                    "status": "rejected",
                    "reason": "Employee declined the call",
                    "room_id": consultation_room_id,
                    "message": "I'm sorry, but the employee is not available to take your call right now. Would you like me to take a message instead?"
                }
            
            elif employee_response == "message":
                # Handle message taking
                logger.info(f"Employee wants to take message for transfer {transfer_id}")
                
                # Agent returns to caller room and cleanup
                await self.disconnect_agent_from_consultation(consultation_room_id, session)
                await sip_call_router.cleanup_participant_identities(consultation_room_id)
                
                return {
                    "transfer_id": transfer_id,
                    "status": "message",
                    "reason": "Employee wants to take a message",
                    "room_id": consultation_room_id,
                    "message": "The employee would prefer to take a message. Would you like me to take a message for them instead?"
                }
            
            else:
                # Unknown response
                return {
                    "transfer_id": transfer_id,
                    "status": "failed",
                    "reason": f"Unknown employee response: {employee_response}",
                    "room_id": consultation_room_id,
                    "message": "I'm having trouble connecting you right now. Would you like me to take a message instead?"
                }
                
        except (api.TwirpError, api.RpcError, ValueError, KeyError) as e:
            logger.error(f"Error in warm transfer {transfer_id}: {e}")
            return {
                "transfer_id": transfer_id,
                "status": "failed",
                "reason": f"Transfer error: {str(e)}",
                "room_id": None,
                "message": "I'm having trouble with the transfer right now. Would you like me to take a message instead?"
            }
        except Exception as e:
            # Catch any unexpected errors
            logger.exception(f"Unexpected error in warm transfer {transfer_id}: {e}")
            return {
                "transfer_id": transfer_id,
                "status": "failed",
                "reason": f"Unexpected transfer error: {str(e)}",
                "room_id": None,
                "message": "I'm having trouble with the transfer right now. Would you like me to take a message instead?"
            }
    
    async def cleanup_expired_transfers(self):
        """Clean up expired or abandoned transfers."""
        try:
            current_time = datetime.now()
            expired_transfers = []
            
            for transfer_id, transfer_info in self.active_transfers.items():
                # Remove transfers older than 10 minutes
                if (current_time - transfer_info['timestamp']).seconds > 600:
                    expired_transfers.append(transfer_id)
            
            for transfer_id in expired_transfers:
                del self.active_transfers[transfer_id]
                logger.info(f"Cleaned up expired transfer: {transfer_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired transfers: {e}")

class SupervisorAgent(Agent):
    """Agent that handles the consultation conversation with the supervisor/employee."""

    def __init__(self, conversation_history: str = ""):
        super().__init__(
            instructions=f"""You are facilitating a warm transfer in English. Here's the information about the caller and conversation:

{conversation_history}

The caller is currently on hold and waiting to be connected to you.

IMPORTANT: You must start the conversation by greeting the employee and explaining the situation clearly. Include the caller's name and reason for calling. Then ask them to respond with 'accept' to take the call, 'decline' to reject it, or 'message' to take a message instead.

Start with: "Hello! I'm facilitating a warm transfer for you. A caller named [CALLER NAME] is on hold and would like to speak with you. They're calling about [REASON]. The conversation so far has been: [summarize the conversation history briefly]. Are you available to take this call? Please say 'accept' if you can take the call, 'decline' if you're not available, or 'message' if you'd prefer to take a message instead."

Make sure to use the actual caller name and reason from the information provided above."""
        )
        self.conversation_history = conversation_history
        self.consultation_room_id: Optional[str] = None
        self.caller_room_id: Optional[str] = None
        self.employee_decision: Optional[str] = None
        self.decision_event = asyncio.Event()  # Event for signaling decision
        self.session_manager = None
    
    async def on_enter(self):
        """Called when the agent enters the consultation room."""
        logger.info("SupervisorAgent entered consultation room")
        
        # Explicitly start the conversation
        await self.session.generate_reply(
            instructions="Start the conversation by greeting the employee and explaining the warm transfer situation. Ask them to respond with 'accept', 'decline', or 'message'."
        )
    
    @function_tool
    async def record_employee_decision(self, context: RunContext, decision: str) -> str:
        """Employee accepts or declines transfer.

        Args:
            decision: "accept", "decline", or "message"
        """
        self.employee_decision = decision
        self.decision_event.set()  # Signal that decision has been made
        logger.info(f"Employee decision recorded: {decision}")

        if decision == "accept":
            return "Great! I'll connect you to the caller now."
        elif decision == "decline":
            return "I understand. I'll let the caller know you're not available."
        elif decision == "message":
            return "I'll take a message for you instead."
        else:
            return "I didn't understand your response. Please say 'accept', 'decline', or 'message'."

# Global instance
warm_transfer_manager = WarmTransferManager()
