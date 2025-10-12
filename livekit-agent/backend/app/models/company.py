"""
Pydantic models for company-related data.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CompanyInfoBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    greeting_message: str = Field(..., min_length=1)
    business_hours: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

class CompanyInfoUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    greeting_message: Optional[str] = Field(None, min_length=1)
    business_hours: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None

class CompanyInfoResponse(CompanyInfoBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyHoursRequest(BaseModel):
    check_time: Optional[datetime] = None

class CompanyHoursResponse(BaseModel):
    is_open: bool
    check_time: datetime


