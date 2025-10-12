"""
Services for the switchboard assistant backend.
"""

from .employee_service import EmployeeService
from .department_service import DepartmentService
from .company_service import CompanyService
from .call_log_service import CallLogService
from .message_service import MessageService

__all__ = [
    "EmployeeService",
    "DepartmentService",
    "CompanyService", 
    "CallLogService",
    "MessageService"
]


