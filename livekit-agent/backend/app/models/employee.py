"""
Pydantic models for employee-related data.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=20)
    email: str = Field(..., min_length=1, max_length=255)
    department_id: Optional[str] = None
    office: Optional[str] = Field(None, max_length=255)
    roles: List[str] = Field(default_factory=list)
    status: str = Field(default="available", regex="^(available|busy|offline|unavailable)$")
    availability_hours: Dict[str, Any] = Field(default_factory=dict)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    department_id: Optional[str] = None
    office: Optional[str] = Field(None, max_length=255)
    roles: Optional[List[str]] = None
    status: Optional[str] = Field(None, regex="^(available|busy|offline|unavailable)$")
    availability_hours: Optional[Dict[str, Any]] = None

class EmployeeResponse(EmployeeBase):
    id: str
    department_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmployeeSearchRequest(BaseModel):
    query: Optional[str] = None
    department: Optional[str] = None
    status: str = Field(default="available", regex="^(available|busy|offline|unavailable)$")

class EmployeeAvailabilityRequest(BaseModel):
    employee_id: str
    check_time: Optional[datetime] = None

class EmployeeAvailabilityResponse(BaseModel):
    employee_id: str
    is_available: bool
    check_time: datetime


