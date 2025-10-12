"""
Supabase client for Switchboard Assistant
Handles all database operations for the agent
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)

@dataclass
class Employee:
    id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    department_id: Optional[str]
    department_name: Optional[str]
    office: Optional[str]
    roles: List[str]
    status: str
    
    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def phone(self) -> str:
        return self.phone_number

@dataclass
class Department:
    id: str
    name: str
    description: Optional[str]
    routing_priority: int

@dataclass
class CompanyInfo:
    id: str
    company_name: str
    greeting_message: str
    business_hours: Dict[str, Any]
    settings: Dict[str, Any]

@dataclass
class CallLog:
    id: str
    caller_phone: str
    caller_name: Optional[str]
    employee_id: Optional[str]
    room_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    status: str
    outcome: Optional[str]
    transcript: Optional[str]

@dataclass
class Message:
    id: str
    from_caller: str
    to_employee_id: str
    message_text: str
    delivered_via: List[str]
    status: str
    created_at: datetime

class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        # Use service role key for backend operations
        key_to_use = self.service_role_key if self.service_role_key else self.key
        self.client: Client = create_client(self.url, key_to_use)
        
        logger.info("Supabase client initialized successfully")
    
    async def search_employees(self, query: str = "", department: str = "") -> List[Employee]:
        """Search for employees by name, department, or role"""
        try:
            # Handle full name searches by doing multiple searches and combining results
            all_employees = []
            
            if query and ' ' in query.strip():
                # If it's a full name, search for each part separately and combine results
                name_parts = query.strip().split()
                for part in name_parts:
                    result = self.client.rpc('search_employees', {
                        'p_query': part,
                        'p_department': department
                    }).execute()
                    
                    for row in result.data:
                        # Check if this employee matches the full name
                        full_name = f"{row['first_name']} {row['last_name']}".lower()
                        if query.lower() in full_name:
                            all_employees.append(row)
                
                # Remove duplicates based on employee ID
                seen_ids = set()
                unique_employees = []
                for emp in all_employees:
                    if emp['id'] not in seen_ids:
                        seen_ids.add(emp['id'])
                        unique_employees.append(emp)
                
                result_data = unique_employees
            else:
                # Use the regular database function for single word searches or empty queries
                result = self.client.rpc('search_employees', {
                    'p_query': query,
                    'p_department': department
                }).execute()
                result_data = result.data
            
            employees = []
            for row in result_data:
                employee = Employee(
                    id=row['id'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    phone_number=row['phone_number'],
                    department_id=row['department_id'],
                    department_name=row['department_name'],
                    office=row['office'],
                    roles=row['roles'] or [],
                    status=row['status']
                )
                employees.append(employee)
            
            logger.info(f"Found {len(employees)} employees for query: '{query}', department: '{department}'")
            return employees
            
        except Exception as e:
            logger.error(f"Error searching employees: {e}")
            return []
    
    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            result = self.client.table('employees').select('*, departments(name)').eq('id', employee_id).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            return Employee(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone_number=row['phone_number'],
                department_id=row['department_id'],
                department_name=row['departments']['name'] if row['departments'] else None,
                office=row['office'],
                roles=row['roles'] or [],
                status=row['status']
            )
            
        except Exception as e:
            logger.error(f"Error getting employee by ID: {e}")
            return None
    
    async def get_employee_by_phone(self, phone_number: str) -> Optional[Employee]:
        """Get employee by phone number"""
        try:
            result = self.client.table('employees').select('*, departments(name)').eq('phone_number', phone_number).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            return Employee(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone_number=row['phone_number'],
                department_id=row['department_id'],
                department_name=row['departments']['name'] if row['departments'] else None,
                office=row['office'],
                roles=row['roles'] or [],
                status=row['status']
            )
            
        except Exception as e:
            logger.error(f"Error getting employee by phone: {e}")
            return None
    
    async def is_employee_available(self, employee_id: str) -> bool:
        """Check if employee is available"""
        try:
            result = self.client.rpc('is_employee_available', {'p_employee_id': employee_id}).execute()
            return result.data if result.data is not None else False
            
        except Exception as e:
            logger.error(f"Error checking employee availability: {e}")
            return False
    
    async def get_departments(self) -> List[Department]:
        """Get all departments"""
        try:
            result = self.client.table('departments').select('*').order('routing_priority').execute()
            
            departments = []
            for row in result.data:
                department = Department(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    routing_priority=row['routing_priority']
                )
                departments.append(department)
            
            return departments
            
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            return []
    
    async def get_company_info(self) -> Optional[CompanyInfo]:
        """Get company information"""
        try:
            result = self.client.table('company_info').select('*').limit(1).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            return CompanyInfo(
                id=row['id'],
                company_name=row['company_name'],
                greeting_message=row['greeting_message'],
                business_hours=row['business_hours'] or {},
                settings=row['settings'] or {}
            )
            
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return None
    
    async def is_company_open(self) -> bool:
        """Check if company is currently open"""
        try:
            result = self.client.rpc('is_company_open').execute()
            return result.data if result.data is not None else True
            
        except Exception as e:
            logger.error(f"Error checking company hours: {e}")
            return True  # Default to open if error
    
    async def log_call(self, caller_phone: str, caller_name: str = None, employee_id: str = None, 
                      room_name: str = None, status: str = "active", outcome: str = None) -> str:
        """Log a call to the database"""
        try:
            call_data = {
                'caller_phone': caller_phone,
                'caller_name': caller_name,
                'employee_id': employee_id,
                'room_name': room_name,
                'status': status,
                'outcome': outcome
            }
            
            result = self.client.table('call_logs').insert(call_data).execute()
            
            if result.data:
                call_id = result.data[0]['id']
                logger.info(f"Call logged with ID: {call_id}")
                return call_id
            else:
                logger.error("Failed to log call - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error logging call: {e}")
            return None
    
    async def update_call_log(self, call_id: str, **kwargs) -> bool:
        """Update a call log"""
        try:
            result = self.client.table('call_logs').update(kwargs).eq('id', call_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating call log: {e}")
            return False
    
    async def save_message(self, from_caller: str, to_employee_id: str, message_text: str, 
                          delivered_via: List[str] = None) -> str:
        """Save a message to the database"""
        try:
            message_data = {
                'from_caller': from_caller,
                'to_employee_id': to_employee_id,
                'message_text': message_text,
                'delivered_via': delivered_via or [],
                'status': 'pending'
            }
            
            result = self.client.table('messages').insert(message_data).execute()
            
            if result.data:
                message_id = result.data[0]['id']
                logger.info(f"Message saved with ID: {message_id}")
                return message_id
            else:
                logger.error("Failed to save message - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None
    
    async def update_message_status(self, message_id: str, status: str, delivery_details: Dict[str, Any] = None) -> bool:
        """Update message delivery status"""
        try:
            update_data = {'status': status}
            if delivery_details:
                update_data['delivery_details'] = delivery_details
            
            result = self.client.table('messages').update(update_data).eq('id', message_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating message status: {e}")
            return False
    
    async def get_employee_messages(self, employee_id: str) -> List[Message]:
        """Get messages for an employee"""
        try:
            result = self.client.table('messages').select('*').eq('to_employee_id', employee_id).order('created_at', desc=True).execute()
            
            messages = []
            for row in result.data:
                message = Message(
                    id=row['id'],
                    from_caller=row['from_caller'],
                    to_employee_id=row['to_employee_id'],
                    message_text=row['message_text'],
                    delivered_via=row['delivered_via'] or [],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting employee messages: {e}")
            return []

# Global instance
_db_client = None

def get_db_client() -> SupabaseClient:
    """Get the global database client instance"""
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client