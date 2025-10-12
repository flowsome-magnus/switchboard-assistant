"""
Database module for Switchboard Assistant
"""

from .supabase_client import get_db_client, SupabaseClient, Employee, Department, CompanyInfo, CallLog, Message

__all__ = [
    'get_db_client',
    'SupabaseClient', 
    'Employee',
    'Department',
    'CompanyInfo',
    'CallLog',
    'Message'
]