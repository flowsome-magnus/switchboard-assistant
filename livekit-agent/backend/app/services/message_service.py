"""
Message service for handling business logic.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse
)
from ...db.supabase_client import get_db_client

class MessageService:
    """Service for message-related operations."""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    async def get_messages(
        self,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MessageResponse]:
        """Get messages with filtering."""
        try:
            messages = await self.db_client.get_messages(
                employee_id=employee_id,
                status=status,
                limit=limit,
                offset=offset
            )
            
            return [
                MessageResponse(
                    id=msg.id,
                    from_caller=msg.from_caller,
                    to_employee_id=msg.to_employee_id,
                    message_text=msg.message_text,
                    delivered_via=msg.delivered_via,
                    timestamp=msg.timestamp,
                    status=msg.status,
                    delivery_details=msg.delivery_details,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for msg in messages
            ]
        except Exception as e:
            raise Exception(f"Error getting messages: {e}")
    
    async def get_message(self, message_id: str) -> Optional[MessageResponse]:
        """Get message by ID."""
        try:
            # TODO: Implement actual get by ID
            return None
        except Exception as e:
            raise Exception(f"Error getting message: {e}")
    
    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message."""
        try:
            message_id = await self.db_client.save_message(
                from_caller=message_data.from_caller,
                to_employee_id=message_data.to_employee_id,
                message_text=message_data.message_text,
                delivered_via=message_data.delivered_via,
                delivery_details=message_data.delivery_details
            )
            
            return MessageResponse(
                id=message_id or "new-message-id",
                from_caller=message_data.from_caller,
                to_employee_id=message_data.to_employee_id,
                message_text=message_data.message_text,
                delivered_via=message_data.delivered_via,
                timestamp=datetime.utcnow(),
                status="pending",
                delivery_details=message_data.delivery_details,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        except Exception as e:
            raise Exception(f"Error creating message: {e}")
    
    async def update_message(
        self, 
        message_id: str, 
        message_data: MessageUpdate
    ) -> Optional[MessageResponse]:
        """Update a message."""
        try:
            # TODO: Implement actual update
            return None
        except Exception as e:
            raise Exception(f"Error updating message: {e}")
    
    async def update_message_status(
        self, 
        message_id: str, 
        status: str, 
        delivery_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update message delivery status."""
        try:
            return await self.db_client.update_message_status(
                message_id, 
                status, 
                delivery_details
            )
        except Exception as e:
            raise Exception(f"Error updating message status: {e}")
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        try:
            # TODO: Implement actual deletion
            return True
        except Exception as e:
            raise Exception(f"Error deleting message: {e}")


