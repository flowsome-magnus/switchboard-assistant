"""
Pydantic models for call log-related data.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class CallLogBase(BaseModel):
    caller_phone: str = Field(..., min_length=1, max_length=20)
    caller_name: Optional[str] = Field(None, max_length=255)
    employee_id: Optional[str] = None
    duration: Optional[str] = None
    status: str = Field(default="completed", regex="^(completed|missed|transferred|failed)$")
    recording_url: Optional[str] = None
    room_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class CallLogCreate(CallLogBase):
    pass

class CallLogUpdate(BaseModel):
    caller_name: Optional[str] = Field(None, max_length=255)
    employee_id: Optional[str] = None
    duration: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(completed|missed|transferred|failed)$")
    recording_url: Optional[str] = None
    room_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class CallLogResponse(CallLogBase):
    id: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CallLogSearchRequest(BaseModel):
    employee_id: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(completed|missed|transferred|failed)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


