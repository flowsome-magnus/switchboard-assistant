"""
Message management API routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageSearchRequest,
    MessageStatusUpdate
)
from ..services.message_service import MessageService
from ..utils.dependencies import get_message_service

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    employee_id: str = Query(None, description="Filter by employee ID"),
    status: str = Query(None, description="Filter by message status"),
    date_from: str = Query(None, description="Start date (ISO format)"),
    date_to: str = Query(None, description="End date (ISO format)"),
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    message_service: MessageService = Depends(get_message_service)
):
    """Get messages with filtering and pagination."""
    try:
        messages = await message_service.get_messages(
            employee_id=employee_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    message_service: MessageService = Depends(get_message_service)
):
    """Get a specific message by ID."""
    try:
        message = await message_service.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    message_service: MessageService = Depends(get_message_service)
):
    """Create a new message."""
    try:
        message = await message_service.create_message(message_data)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_data: MessageUpdate,
    message_service: MessageService = Depends(get_message_service)
):
    """Update an existing message."""
    try:
        message = await message_service.update_message(message_id, message_data)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{message_id}/status")
async def update_message_status(
    message_id: str,
    status_data: MessageStatusUpdate,
    message_service: MessageService = Depends(get_message_service)
):
    """Update message delivery status."""
    try:
        success = await message_service.update_message_status(
            message_id, 
            status_data.status, 
            status_data.delivery_details
        )
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"message": "Message status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    message_service: MessageService = Depends(get_message_service)
):
    """Delete a message."""
    try:
        success = await message_service.delete_message(message_id)
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


