"""
Call log service for handling business logic.
"""

from typing import List, Optional
from datetime import datetime

from ..models.call_log import (
    CallLogCreate,
    CallLogUpdate,
    CallLogResponse
)
from ...db.supabase_client import get_db_client

class CallLogService:
    """Service for call log-related operations."""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    async def get_call_logs(
        self,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CallLogResponse]:
        """Get call logs with filtering."""
        try:
            call_logs = await self.db_client.get_call_logs(
                employee_id=employee_id,
                limit=limit,
                offset=offset
            )
            
            return [
                CallLogResponse(
                    id=log.id,
                    caller_phone=log.caller_phone,
                    caller_name=log.caller_name,
                    employee_id=log.employee_id,
                    timestamp=log.timestamp,
                    duration=log.duration,
                    status=log.status,
                    recording_url=log.recording_url,
                    room_id=log.room_id,
                    notes=log.notes,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for log in call_logs
            ]
        except Exception as e:
            raise Exception(f"Error getting call logs: {e}")
    
    async def get_call_log(self, call_log_id: str) -> Optional[CallLogResponse]:
        """Get call log by ID."""
        try:
            # TODO: Implement actual get by ID
            return None
        except Exception as e:
            raise Exception(f"Error getting call log: {e}")
    
    async def create_call_log(self, call_log_data: CallLogCreate) -> CallLogResponse:
        """Create a new call log."""
        try:
            call_id = await self.db_client.log_call(
                caller_phone=call_log_data.caller_phone,
                caller_name=call_log_data.caller_name,
                employee_id=call_log_data.employee_id,
                duration=call_log_data.duration,
                status=call_log_data.status,
                recording_url=call_log_data.recording_url,
                room_id=call_log_data.room_id,
                notes=call_log_data.notes
            )
            
            return CallLogResponse(
                id=call_id or "new-call-id",
                caller_phone=call_log_data.caller_phone,
                caller_name=call_log_data.caller_name,
                employee_id=call_log_data.employee_id,
                timestamp=datetime.utcnow(),
                duration=call_log_data.duration,
                status=call_log_data.status,
                recording_url=call_log_data.recording_url,
                room_id=call_log_data.room_id,
                notes=call_log_data.notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        except Exception as e:
            raise Exception(f"Error creating call log: {e}")
    
    async def update_call_log(
        self, 
        call_log_id: str, 
        call_log_data: CallLogUpdate
    ) -> Optional[CallLogResponse]:
        """Update a call log."""
        try:
            # TODO: Implement actual update
            return None
        except Exception as e:
            raise Exception(f"Error updating call log: {e}")
    
    async def delete_call_log(self, call_log_id: str) -> bool:
        """Delete a call log."""
        try:
            # TODO: Implement actual deletion
            return True
        except Exception as e:
            raise Exception(f"Error deleting call log: {e}")


