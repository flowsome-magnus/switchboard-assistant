"""
Pydantic models for the switchboard assistant API.
"""

from .employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeSearchRequest,
    EmployeeAvailabilityRequest,
    EmployeeAvailabilityResponse
)

from .department import (
    DepartmentBase,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)

from .company import (
    CompanyInfoBase,
    CompanyInfoUpdate,
    CompanyInfoResponse,
    CompanyHoursRequest,
    CompanyHoursResponse
)

from .call_log import (
    CallLogBase,
    CallLogCreate,
    CallLogUpdate,
    CallLogResponse,
    CallLogSearchRequest
)

from .message import (
    MessageBase,
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageSearchRequest,
    MessageStatusUpdate
)

__all__ = [
    # Employee models
    "EmployeeBase",
    "EmployeeCreate", 
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeSearchRequest",
    "EmployeeAvailabilityRequest",
    "EmployeeAvailabilityResponse",
    
    # Department models
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate", 
    "DepartmentResponse",
    
    # Company models
    "CompanyInfoBase",
    "CompanyInfoUpdate",
    "CompanyInfoResponse",
    "CompanyHoursRequest",
    "CompanyHoursResponse",
    
    # Call log models
    "CallLogBase",
    "CallLogCreate",
    "CallLogUpdate",
    "CallLogResponse",
    "CallLogSearchRequest",
    
    # Message models
    "MessageBase",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",
    "MessageSearchRequest",
    "MessageStatusUpdate"
]


