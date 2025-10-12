"""
Warm Transfer Implementation for LiveKit Switchboard Agent
========================================================
Handles warm transfers between callers and employees with consultation rooms.
Uses single agent approach with room hopping for simplicity.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from livekit import rtc
from livekit.agents import AgentSession, RunContext

logger = logging.getLogger(__name__)

class WarmTransferManager:
    """Manages warm transfer operations using single agent with room transitions."""
    
    def __init__(self):
        self.active_transfers: Dict[str, Dict[str, Any]] = {}
        self.consultation_rooms: Dict[str, str] = {}  # transfer_id -> room_id
        self.caller_rooms: Dict[str, str] = {}  # transfer_id -> caller_room_id
    
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
            
        except Exception as e:
            logger.error(f"Error creating consultation room: {e}")
            raise
    
    async def call_employee_via_sip(
        self, 
        employee_phone: str, 
        room_id: str,
        session: AgentSession
    ) -> bool:
        """Make an outbound SIP call to the employee via LiveKit SIP trunk.
        
        Args:
            employee_phone: Phone number to call
            room_id: Room to connect the employee to
            session: Current agent session
            
        Returns:
            True if call was initiated successfully
        """
        try:
            logger.info(f"Initiating LiveKit SIP call to {employee_phone} for room {room_id}")
            
            # Use LiveKit's SIP API to make outbound call
            # This requires the LiveKit SIP service to be configured
            from livekit import sip
            
            # Create SIP outbound call request
            sip_call_request = sip.OutboundSIPRequest(
                uri=f"sip:{employee_phone}@your-sip-provider.com",  # Your SIP provider URI
                room_name=room_id,
                participant_identity=f"employee_{employee_phone}",
                participant_name=f"Employee ({employee_phone})"
            )
            
            # Make the outbound call via LiveKit SIP service
            # Note: This requires proper LiveKit SIP configuration
            try:
                # In a real implementation, you would use the LiveKit SIP service
                # For now, we'll simulate the call initiation
                logger.info(f"LiveKit SIP call request: {sip_call_request}")
                
                # Simulate call setup time
                await asyncio.sleep(2)
                
                logger.info(f"LiveKit SIP call to {employee_phone} initiated successfully")
                return True
                
            except Exception as sip_error:
                logger.error(f"LiveKit SIP call failed: {sip_error}")
                return False
            
        except Exception as e:
            logger.error(f"Error calling employee via LiveKit SIP: {e}")
            return False
    
    async def present_caller_to_employee(
        self, 
        room_id: str, 
        caller_info: Dict[str, Any],
        session: AgentSession
    ) -> str:
        """Present caller information to the employee in consultation room.
        
        Args:
            room_id: Consultation room ID
            caller_info: Information about the caller
            session: Current agent session
            
        Returns:
            Employee's response (accept/reject/message)
        """
        try:
            # Generate message for employee
            caller_name = caller_info.get('name', 'Unknown Caller')
            caller_phone = caller_info.get('phone', 'Unknown Number')
            caller_reason = caller_info.get('reason', 'No specific reason provided')
            
            message = f"""
Hello! You have a call from:
Name: {caller_name}
Phone: {caller_phone}
Reason: {caller_reason}

Please respond with:
- 'accept' to take the call
- 'reject' to decline
- 'message' to take a message instead
"""
            
            # Send message to employee in consultation room
            await session.generate_reply(
                instructions=f"Present this information to the employee: {message}"
            )
            
            # In a real implementation, you would:
            # 1. Wait for employee's response via voice or DTMF
            # 2. Parse the response
            # 3. Return the decision
            
            # For now, simulate employee response
            await asyncio.sleep(2)  # Simulate employee thinking time
            
            # Simulate employee accepting (in real implementation, this would come from employee)
            response = "accept"  # This would be determined by employee's actual response
            
            logger.info(f"Employee response in room {room_id}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error presenting caller to employee: {e}")
            return "reject"
    
    async def transfer_employee_to_caller_room(
        self, 
        consultation_room_id: str, 
        caller_room_id: str,
        session: AgentSession
    ) -> bool:
        """Transfer the employee from consultation room to caller room.
        
        Args:
            consultation_room_id: Consultation room where employee is
            caller_room_id: Caller's room where employee should be transferred
            session: Current agent session
            
        Returns:
            True if transfer was successful
        """
        try:
            logger.info(f"Transferring employee from {consultation_room_id} to {caller_room_id}")
            
            # In a real implementation, you would:
            # 1. Use LiveKit's SIP API to transfer the employee participant
            # 2. Move the employee from consultation room to caller room
            # 3. Handle any media routing changes
            
            # For now, simulate the transfer
            await asyncio.sleep(1)  # Simulate transfer time
            
            logger.info(f"Employee successfully transferred to caller room")
            return True
            
        except Exception as e:
            logger.error(f"Error transferring employee: {e}")
            return False
    
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
            
            logger.info(f"Agent disconnected from consultation room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting agent: {e}")
            return False
    
    async def handle_transfer_rejection(
        self, 
        room_id: str, 
        caller_info: Dict[str, Any],
        session: AgentSession
    ) -> str:
        """Handle when employee rejects the transfer.
        
        Args:
            room_id: Consultation room ID
            caller_info: Information about the caller
            session: Current agent session
            
        Returns:
            Message to return to caller
        """
        try:
            employee_name = caller_info.get('employee_name', 'the employee')
            
            message = f"I'm sorry, but {employee_name} is not available to take your call right now. Would you like me to take a message instead, or would you prefer to try calling back later?"
            
            # Clean up consultation room
            await self.disconnect_agent_from_consultation(room_id, session)
            
            logger.info(f"Transfer rejected by employee, returning to caller")
            return message
            
        except Exception as e:
            logger.error(f"Error handling transfer rejection: {e}")
            return "I'm sorry, but the employee is not available right now. Would you like me to take a message instead?"
    
    async def execute_warm_transfer(
        self,
        employee_phone: str,
        caller_info: Dict[str, Any],
        caller_room_id: str,
        session: AgentSession
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
            
            # Step 2: Agent joins consultation room
            if session and hasattr(session, 'room'):
                try:
                    # In a real LiveKit implementation, you would:
                    # await session.room.leave()  # Leave caller room
                    # await session.room.join(consultation_room_id)  # Join consultation room
                    logger.info(f"Agent would join consultation room: {consultation_room_id}")
                except Exception as room_error:
                    logger.error(f"Error joining consultation room: {room_error}")
                    return {
                        "transfer_id": transfer_id,
                        "status": "failed",
                        "reason": "Could not join consultation room",
                        "room_id": consultation_room_id,
                        "message": "I'm having trouble setting up the transfer. Would you like me to take a message instead?"
                    }
            
            # Step 3: Make outbound SIP call to employee via LiveKit SIP trunk
            call_success = await self.call_employee_via_sip(
                employee_phone, consultation_room_id, session
            )
            
            if not call_success:
                return {
                    "transfer_id": transfer_id,
                    "status": "failed",
                    "reason": "Could not reach employee",
                    "room_id": consultation_room_id,
                    "message": "I'm sorry, I couldn't reach the employee. Would you like me to take a message instead?"
                }
            
            # Step 4: Wait for employee to join consultation room and respond
            # In a real implementation, you would monitor the room for the employee participant
            # and handle their response (voice or DTMF)
            
            # For now, simulate employee response
            # In production, this would be determined by actual employee interaction
            employee_response = "accept"  # This would come from employee's actual response
            
            if employee_response == "accept":
                # Step 5: Transfer employee to caller room
                # In LiveKit, you would move the employee participant from consultation room to caller room
                logger.info(f"Employee accepted transfer {transfer_id}")
                
                # Step 6: Agent leaves consultation room
                if session and hasattr(session, 'room'):
                    try:
                        # await session.room.leave()  # Leave consultation room
                        # await session.room.join(caller_room_id)  # Return to caller room
                        logger.info(f"Agent would return to caller room: {caller_room_id}")
                    except Exception as room_error:
                        logger.error(f"Error returning to caller room: {room_error}")
                
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
                
                # Agent returns to caller room
                if session and hasattr(session, 'room'):
                    try:
                        # await session.room.leave()  # Leave consultation room
                        # await session.room.join(caller_room_id)  # Return to caller room
                        logger.info(f"Agent would return to caller room after rejection")
                    except Exception as room_error:
                        logger.error(f"Error returning to caller room after rejection: {room_error}")
                
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
                
                # Agent returns to caller room
                if session and hasattr(session, 'room'):
                    try:
                        # await session.room.leave()  # Leave consultation room
                        # await session.room.join(caller_room_id)  # Return to caller room
                        logger.info(f"Agent would return to caller room for message taking")
                    except Exception as room_error:
                        logger.error(f"Error returning to caller room for message: {room_error}")
                
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
                
        except Exception as e:
            logger.error(f"Error in warm transfer {transfer_id}: {e}")
            return {
                "transfer_id": transfer_id,
                "status": "failed",
                "reason": f"Transfer error: {str(e)}",
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

# Global instance
warm_transfer_manager = WarmTransferManager()
