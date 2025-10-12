"""
Employee service for handling business logic.
"""

from typing import List, Optional
from datetime import datetime

from ..models.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse
)
from ...db.supabase_client import get_db_client, Employee

class EmployeeService:
    """Service for employee-related operations."""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    async def get_employees(
        self,
        department_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EmployeeResponse]:
        """Get employees with filtering."""
        try:
            employees = await self.db_client.search_employees(
                query=search,
                department=department_id,
                status=status
            )
            
            # Apply pagination
            start = offset
            end = offset + limit
            paginated_employees = employees[start:end]
            
            return [
                EmployeeResponse(
                    id=emp.id,
                    name=emp.name,
                    phone=emp.phone,
                    email=emp.email,
                    department_id=emp.department_id,
                    department_name=emp.department_name,
                    office=emp.office,
                    roles=emp.roles,
                    status=emp.status,
                    availability_hours=emp.availability_hours,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for emp in paginated_employees
            ]
        except Exception as e:
            raise Exception(f"Error getting employees: {e}")
    
    async def search_employees(
        self,
        query: Optional[str] = None,
        department: Optional[str] = None,
        status: str = "available"
    ) -> List[EmployeeResponse]:
        """Search employees."""
        try:
            employees = await self.db_client.search_employees(
                query=query,
                department=department,
                status=status
            )
            
            return [
                EmployeeResponse(
                    id=emp.id,
                    name=emp.name,
                    phone=emp.phone,
                    email=emp.email,
                    department_id=emp.department_id,
                    department_name=emp.department_name,
                    office=emp.office,
                    roles=emp.roles,
                    status=emp.status,
                    availability_hours=emp.availability_hours,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for emp in employees
            ]
        except Exception as e:
            raise Exception(f"Error searching employees: {e}")
    
    async def get_available_employees(
        self,
        department: Optional[str] = None,
        check_time: Optional[datetime] = None
    ) -> List[EmployeeResponse]:
        """Get available employees."""
        try:
            employees = await self.db_client.get_available_employees(
                department=department,
                check_time=check_time
            )
            
            return [
                EmployeeResponse(
                    id=emp.id,
                    name=emp.name,
                    phone=emp.phone,
                    email=emp.email,
                    department_id=emp.department_id,
                    department_name=emp.department_name,
                    office=emp.office,
                    roles=emp.roles,
                    status=emp.status,
                    availability_hours=emp.availability_hours,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for emp in employees
            ]
        except Exception as e:
            raise Exception(f"Error getting available employees: {e}")
    
    async def get_employee(self, employee_id: str) -> Optional[EmployeeResponse]:
        """Get employee by ID."""
        try:
            # This would need to be implemented in the database client
            # For now, we'll search and filter by ID
            employees = await self.db_client.search_employees()
            for emp in employees:
                if emp.id == employee_id:
                    return EmployeeResponse(
                        id=emp.id,
                        name=emp.name,
                        phone=emp.phone,
                        email=emp.email,
                        department_id=emp.department_id,
                        department_name=emp.department_name,
                        office=emp.office,
                        roles=emp.roles,
                        status=emp.status,
                        availability_hours=emp.availability_hours,
                        created_at=datetime.utcnow(),  # TODO: Get from DB
                        updated_at=datetime.utcnow()   # TODO: Get from DB
                    )
            return None
        except Exception as e:
            raise Exception(f"Error getting employee: {e}")
    
    async def get_employee_by_phone(self, phone: str) -> Optional[EmployeeResponse]:
        """Get employee by phone number."""
        try:
            employee = await self.db_client.get_employee_by_phone(phone)
            if not employee:
                return None
            
            return EmployeeResponse(
                id=employee.id,
                name=employee.name,
                phone=employee.phone,
                email=employee.email,
                department_id=employee.department_id,
                department_name=employee.department_name,
                office=employee.office,
                roles=employee.roles,
                status=employee.status,
                availability_hours=employee.availability_hours,
                created_at=datetime.utcnow(),  # TODO: Get from DB
                updated_at=datetime.utcnow()   # TODO: Get from DB
            )
        except Exception as e:
            raise Exception(f"Error getting employee by phone: {e}")
    
    async def create_employee(self, employee_data: EmployeeCreate) -> EmployeeResponse:
        """Create a new employee."""
        try:
            # This would need to be implemented in the database client
            # For now, we'll return a mock response
            employee_id = "new-employee-id"  # TODO: Generate actual ID
            
            return EmployeeResponse(
                id=employee_id,
                name=employee_data.name,
                phone=employee_data.phone,
                email=employee_data.email,
                department_id=employee_data.department_id,
                department_name=None,  # TODO: Get from department
                office=employee_data.office,
                roles=employee_data.roles,
                status=employee_data.status,
                availability_hours=employee_data.availability_hours,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        except Exception as e:
            raise Exception(f"Error creating employee: {e}")
    
    async def update_employee(
        self, 
        employee_id: str, 
        employee_data: EmployeeUpdate
    ) -> Optional[EmployeeResponse]:
        """Update an employee."""
        try:
            # This would need to be implemented in the database client
            # For now, we'll return a mock response
            existing_employee = await self.get_employee(employee_id)
            if not existing_employee:
                return None
            
            # Update fields
            updated_data = existing_employee.dict()
            for field, value in employee_data.dict(exclude_unset=True).items():
                updated_data[field] = value
            
            return EmployeeResponse(
                id=employee_id,
                name=updated_data["name"],
                phone=updated_data["phone"],
                email=updated_data["email"],
                department_id=updated_data["department_id"],
                department_name=updated_data["department_name"],
                office=updated_data["office"],
                roles=updated_data["roles"],
                status=updated_data["status"],
                availability_hours=updated_data["availability_hours"],
                created_at=existing_employee.created_at,
                updated_at=datetime.utcnow()
            )
        except Exception as e:
            raise Exception(f"Error updating employee: {e}")
    
    async def delete_employee(self, employee_id: str) -> bool:
        """Delete an employee."""
        try:
            # This would need to be implemented in the database client
            # For now, we'll return True
            return True
        except Exception as e:
            raise Exception(f"Error deleting employee: {e}")
    
    async def is_employee_available(
        self, 
        employee_id: str, 
        check_time: Optional[datetime] = None
    ) -> bool:
        """Check if employee is available."""
        try:
            return await self.db_client.is_employee_available(employee_id, check_time)
        except Exception as e:
            raise Exception(f"Error checking employee availability: {e}")


