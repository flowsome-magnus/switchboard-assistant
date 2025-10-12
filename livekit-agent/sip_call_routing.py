"""
SIP Call Routing and Room Management
===================================
Handles SIP call detection, unique room creation, and room lifecycle management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from livekit import rtc
from livekit.agents import AgentSession, RunContext

logger = logging.getLogger(__name__)

class SIPCallRouter:
    """Manages SIP call routing and room lifecycle."""
    
    def __init__(self):
        self.active_rooms: Dict[str, Dict[str, Any]] = {}
        self.room_cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 300  # 5 minutes
    
    def is_sip_participant(self, participant: rtc.RemoteParticipant) -> bool:
        """Check if a participant is from a SIP call.
        
        Args:
            participant: LiveKit participant
            
        Returns:
            True if participant is from SIP
        """
        try:
            # Check participant metadata for SIP indicators
            if participant.metadata:
                metadata_lower = participant.metadata.lower()
                return any(keyword in metadata_lower for keyword in [
                    'sip', 'twilio', 'phone', 'caller', 'call'
                ])
            
            # Check participant identity for SIP patterns
            if participant.identity:
                identity_lower = participant.identity.lower()
                return any(pattern in identity_lower for pattern in [
                    'sip:', 'phone:', 'caller:', 'call-'
                ])
            
            # Check participant name for SIP patterns
            if participant.name:
                name_lower = participant.name.lower()
                return any(pattern in name_lower for pattern in [
                    'sip', 'phone', 'caller', 'call'
                ])
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking SIP participant: {e}")
            return False
    
    def extract_caller_info(self, participant: rtc.RemoteParticipant) -> Dict[str, Any]:
        """Extract caller information from SIP participant.
        
        Args:
            participant: LiveKit participant
            
        Returns:
            Dictionary with caller information
        """
        caller_info = {
            "phone": "Unknown",
            "name": "Unknown Caller",
            "caller_id": "unknown",
            "sip_info": {}
        }
        
        try:
            # Extract from metadata
            if participant.metadata:
                metadata = participant.metadata
                # Parse SIP metadata (format depends on your SIP provider)
                if "sip:" in metadata:
                    # Extract phone number from SIP URI
                    sip_uri = metadata.split("sip:")[1].split("@")[0]
                    caller_info["phone"] = sip_uri
                    caller_info["caller_id"] = sip_uri.replace("+", "").replace("-", "")
            
            # Extract from identity
            if participant.identity:
                identity = participant.identity
                if "caller:" in identity:
                    caller_info["caller_id"] = identity.split("caller:")[1]
                elif "phone:" in identity:
                    caller_info["phone"] = identity.split("phone:")[1]
                    caller_info["caller_id"] = caller_info["phone"].replace("+", "").replace("-", "")
            
            # Extract from name
            if participant.name:
                name = participant.name
                if "caller:" in name:
                    caller_info["name"] = name.split("caller:")[1]
                elif "phone:" in name:
                    caller_info["phone"] = name.split("phone:")[1]
                    caller_info["caller_id"] = caller_info["phone"].replace("+", "").replace("-", "")
            
            # Clean up phone number
            if caller_info["phone"] != "Unknown":
                # Remove any non-digit characters except +
                phone = caller_info["phone"]
                if not phone.startswith("+"):
                    phone = "+" + phone
                caller_info["phone"] = phone
            
            logger.info(f"Extracted caller info: {caller_info}")
            
        except Exception as e:
            logger.error(f"Error extracting caller info: {e}")
        
        return caller_info
    
    def create_unique_room_name(self, caller_info: Dict[str, Any]) -> str:
        """Create a unique room name for a SIP call.
        
        Args:
            caller_info: Information about the caller
            
        Returns:
            Unique room name
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caller_id = caller_info.get("caller_id", "unknown")
            phone = caller_info.get("phone", "").replace("+", "").replace("-", "")
            
            # Create room name with timestamp and caller ID
            room_name = f"call_{timestamp}_{phone}_{caller_id}"
            
            logger.info(f"Created unique room name: {room_name}")
            
            return room_name
            
        except Exception as e:
            logger.error(f"Error creating room name: {e}")
            # Fallback to timestamp-based name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            return f"call_{timestamp}"
    
    async def register_room(self, room_name: str, caller_info: Dict[str, Any], session: AgentSession) -> None:
        """Register a new room for tracking.
        
        Args:
            room_name: Name of the room
            caller_info: Information about the caller
            session: Agent session
        """
        try:
            self.active_rooms[room_name] = {
                "caller_info": caller_info,
                "session": session,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "participants": [],
                "status": "active"
            }
            
            logger.info(f"Registered room: {room_name}")
            
        except Exception as e:
            logger.error(f"Error registering room: {e}")
    
    async def update_room_activity(self, room_name: str) -> None:
        """Update the last activity time for a room.
        
        Args:
            room_name: Name of the room
        """
        try:
            if room_name in self.active_rooms:
                self.active_rooms[room_name]["last_activity"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error updating room activity: {e}")
    
    async def get_room_info(self, room_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a room.
        
        Args:
            room_name: Name of the room
            
        Returns:
            Room information or None if not found
        """
        return self.active_rooms.get(room_name)
    
    async def cleanup_empty_rooms(self) -> None:
        """Clean up empty or inactive rooms."""
        try:
            current_time = datetime.now()
            rooms_to_remove = []
            
            for room_name, room_info in self.active_rooms.items():
                last_activity = room_info["last_activity"]
                time_since_activity = current_time - last_activity
                
                # Remove rooms inactive for more than 5 minutes
                if time_since_activity > timedelta(minutes=5):
                    rooms_to_remove.append(room_name)
            
            for room_name in rooms_to_remove:
                await self.remove_room(room_name)
                logger.info(f"Cleaned up inactive room: {room_name}")
                
        except Exception as e:
            logger.error(f"Error cleaning up rooms: {e}")
    
    async def remove_room(self, room_name: str) -> None:
        """Remove a room from tracking.
        
        Args:
            room_name: Name of the room to remove
        """
        try:
            if room_name in self.active_rooms:
                room_info = self.active_rooms[room_name]
                
                # Mark room as inactive
                room_info["status"] = "inactive"
                room_info["removed_at"] = datetime.now()
                
                # Remove from active rooms
                del self.active_rooms[room_name]
                
                logger.info(f"Removed room: {room_name}")
                
        except Exception as e:
            logger.error(f"Error removing room: {e}")
    
    async def start_cleanup_task(self) -> None:
        """Start the background room cleanup task."""
        if self.room_cleanup_task is None or self.room_cleanup_task.done():
            self.room_cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started room cleanup task")
    
    async def stop_cleanup_task(self) -> None:
        """Stop the background room cleanup task."""
        if self.room_cleanup_task and not self.room_cleanup_task.done():
            self.room_cleanup_task.cancel()
            try:
                await self.room_cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped room cleanup task")
    
    async def _cleanup_loop(self) -> None:
        """Background task to periodically clean up rooms."""
        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_empty_rooms()
        except asyncio.CancelledError:
            logger.info("Room cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in room cleanup loop: {e}")
    
    async def handle_participant_joined(self, room_name: str, participant: rtc.RemoteParticipant) -> None:
        """Handle when a participant joins a room.
        
        Args:
            room_name: Name of the room
            participant: Participant that joined
        """
        try:
            if room_name in self.active_rooms:
                room_info = self.active_rooms[room_name]
                room_info["participants"].append({
                    "identity": participant.identity,
                    "name": participant.name,
                    "joined_at": datetime.now(),
                    "is_sip": self.is_sip_participant(participant)
                })
                
                await self.update_room_activity(room_name)
                
                logger.info(f"Participant joined room {room_name}: {participant.identity}")
                
        except Exception as e:
            logger.error(f"Error handling participant joined: {e}")
    
    async def handle_participant_left(self, room_name: str, participant: rtc.RemoteParticipant) -> None:
        """Handle when a participant leaves a room.
        
        Args:
            room_name: Name of the room
            participant: Participant that left
        """
        try:
            if room_name in self.active_rooms:
                room_info = self.active_rooms[room_name]
                
                # Remove participant from list
                room_info["participants"] = [
                    p for p in room_info["participants"] 
                    if p["identity"] != participant.identity
                ]
                
                await self.update_room_activity(room_name)
                
                logger.info(f"Participant left room {room_name}: {participant.identity}")
                
                # If no participants left, mark room for cleanup
                if not room_info["participants"]:
                    room_info["status"] = "empty"
                    logger.info(f"Room {room_name} is now empty")
                
        except Exception as e:
            logger.error(f"Error handling participant left: {e}")
    
    async def get_active_rooms(self) -> Dict[str, Dict[str, Any]]:
        """Get all active rooms.
        
        Returns:
            Dictionary of active rooms
        """
        return self.active_rooms.copy()
    
    async def get_room_stats(self) -> Dict[str, Any]:
        """Get statistics about active rooms.
        
        Returns:
            Room statistics
        """
        try:
            total_rooms = len(self.active_rooms)
            active_rooms = sum(1 for room in self.active_rooms.values() if room["status"] == "active")
            empty_rooms = sum(1 for room in self.active_rooms.values() if room["status"] == "empty")
            
            total_participants = sum(len(room["participants"]) for room in self.active_rooms.values())
            sip_participants = sum(
                sum(1 for p in room["participants"] if p["is_sip"]) 
                for room in self.active_rooms.values()
            )
            
            return {
                "total_rooms": total_rooms,
                "active_rooms": active_rooms,
                "empty_rooms": empty_rooms,
                "total_participants": total_participants,
                "sip_participants": sip_participants,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting room stats: {e}")
            return {
                "total_rooms": 0,
                "active_rooms": 0,
                "empty_rooms": 0,
                "total_participants": 0,
                "sip_participants": 0,
                "error": str(e)
            }

# Global instance
sip_call_router = SIPCallRouter()


