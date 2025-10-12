"""
Pydantic models for message-related data.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class MessageBase(BaseModel):
    from_caller: str = Field(..., min_length=1, max_length=20)
    to_employee_id: str
    message_text: str = Field(..., min_length=1)
    delivered_via: List[str] = Field(default_factory=list)
    delivery_details: Dict[str, Any] = Field(default_factory=dict)

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    status: Optional[str] = Field(None, regex="^(pending|delivered|failed|read)$")
    delivery_details: Optional[Dict[str, Any]] = None

class MessageResponse(MessageBase):
    id: str
    timestamp: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageSearchRequest(BaseModel):
    employee_id: Optional[str] = None
    status: Optional[str] = Field(None, regex="^(pending|delivered|failed|read)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class MessageStatusUpdate(BaseModel):
    status: str = Field(..., regex="^(pending|delivered|failed|read)$")
    delivery_details: Optional[Dict[str, Any]] = None


