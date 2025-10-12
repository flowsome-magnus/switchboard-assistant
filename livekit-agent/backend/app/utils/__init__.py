"""
Utilities for the switchboard assistant backend.
"""

from .dependencies import (
    get_employee_service,
    get_department_service,
    get_company_service,
    get_call_log_service,
    get_message_service,
    get_db_client
)

__all__ = [
    "get_employee_service",
    "get_department_service",
    "get_company_service",
    "get_call_log_service",
    "get_message_service",
    "get_db_client"
]


