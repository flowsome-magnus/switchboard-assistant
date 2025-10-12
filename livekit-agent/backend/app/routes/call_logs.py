"""
Call log management API routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models.call_log import (
    CallLogCreate,
    CallLogUpdate,
    CallLogResponse,
    CallLogSearchRequest
)
from ..services.call_log_service import CallLogService
from ..utils.dependencies import get_call_log_service

router = APIRouter(prefix="/api/call-logs", tags=["call-logs"])

@router.get("/", response_model=List[CallLogResponse])
async def get_call_logs(
    employee_id: str = Query(None, description="Filter by employee ID"),
    status: str = Query(None, description="Filter by call status"),
    date_from: str = Query(None, description="Start date (ISO format)"),
    date_to: str = Query(None, description="End date (ISO format)"),
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    call_log_service: CallLogService = Depends(get_call_log_service)
):
    """Get call logs with filtering and pagination."""
    try:
        call_logs = await call_log_service.get_call_logs(
            employee_id=employee_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        return call_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{call_log_id}", response_model=CallLogResponse)
async def get_call_log(
    call_log_id: str,
    call_log_service: CallLogService = Depends(get_call_log_service)
):
    """Get a specific call log by ID."""
    try:
        call_log = await call_log_service.get_call_log(call_log_id)
        if not call_log:
            raise HTTPException(status_code=404, detail="Call log not found")
        return call_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CallLogResponse)
async def create_call_log(
    call_log_data: CallLogCreate,
    call_log_service: CallLogService = Depends(get_call_log_service)
):
    """Create a new call log entry."""
    try:
        call_log = await call_log_service.create_call_log(call_log_data)
        return call_log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{call_log_id}", response_model=CallLogResponse)
async def update_call_log(
    call_log_id: str,
    call_log_data: CallLogUpdate,
    call_log_service: CallLogService = Depends(get_call_log_service)
):
    """Update an existing call log."""
    try:
        call_log = await call_log_service.update_call_log(call_log_id, call_log_data)
        if not call_log:
            raise HTTPException(status_code=404, detail="Call log not found")
        return call_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{call_log_id}")
async def delete_call_log(
    call_log_id: str,
    call_log_service: CallLogService = Depends(get_call_log_service)
):
    """Delete a call log."""
    try:
        success = await call_log_service.delete_call_log(call_log_id)
        if not success:
            raise HTTPException(status_code=404, detail="Call log not found")
        return {"message": "Call log deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


