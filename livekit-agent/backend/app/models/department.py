"""
Pydantic models for department-related data.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    available_hours: Dict[str, Any] = Field(default_factory=dict)
    routing_priority: int = Field(default=1, ge=1)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    available_hours: Optional[Dict[str, Any]] = None
    routing_priority: Optional[int] = Field(None, ge=1)

class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


