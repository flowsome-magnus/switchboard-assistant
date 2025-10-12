"""
FastAPI dependencies for dependency injection.
"""

from functools import lru_cache
from ..services.employee_service import EmployeeService
from ..services.department_service import DepartmentService
from ..services.company_service import CompanyService
from ..services.call_log_service import CallLogService
from ..services.message_service import MessageService
from ..services.twilio_webhook_service import TwilioWebhookService
from ...db.supabase_client import get_db_client

@lru_cache()
def get_employee_service() -> EmployeeService:
    """Get employee service instance."""
    return EmployeeService()

@lru_cache()
def get_department_service() -> DepartmentService:
    """Get department service instance."""
    return DepartmentService()

@lru_cache()
def get_company_service() -> CompanyService:
    """Get company service instance."""
    return CompanyService()

@lru_cache()
def get_call_log_service() -> CallLogService:
    """Get call log service instance."""
    return CallLogService()

@lru_cache()
def get_message_service() -> MessageService:
    """Get message service instance."""
    return MessageService()

@lru_cache()
def get_twilio_webhook_service() -> TwilioWebhookService:
    """Get Twilio webhook service instance."""
    return TwilioWebhookService()

@lru_cache()
def get_db_client():
    """Get database client instance."""
    return get_db_client()

__all__ = [
    "get_employee_service",
    "get_department_service",
    "get_company_service",
    "get_call_log_service",
    "get_message_service",
    "get_twilio_webhook_service",
    "get_db_client"
]
