"""
Department service for handling business logic.
"""

from typing import List, Optional
from datetime import datetime

from ..models.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from ...db.supabase_client import get_db_client

class DepartmentService:
    """Service for department-related operations."""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    async def get_departments(self) -> List[DepartmentResponse]:
        """Get all departments."""
        try:
            departments = await self.db_client.get_departments()
            return [
                DepartmentResponse(
                    id=dept.id,
                    name=dept.name,
                    description=dept.description,
                    available_hours=dept.available_hours,
                    routing_priority=dept.routing_priority,
                    created_at=datetime.utcnow(),  # TODO: Get from DB
                    updated_at=datetime.utcnow()   # TODO: Get from DB
                )
                for dept in departments
            ]
        except Exception as e:
            raise Exception(f"Error getting departments: {e}")
    
    async def get_department(self, department_id: str) -> Optional[DepartmentResponse]:
        """Get department by ID."""
        try:
            departments = await self.get_departments()
            for dept in departments:
                if dept.id == department_id:
                    return dept
            return None
        except Exception as e:
            raise Exception(f"Error getting department: {e}")
    
    async def create_department(self, department_data: DepartmentCreate) -> DepartmentResponse:
        """Create a new department."""
        try:
            # TODO: Implement actual creation
            return DepartmentResponse(
                id="new-dept-id",
                name=department_data.name,
                description=department_data.description,
                available_hours=department_data.available_hours,
                routing_priority=department_data.routing_priority,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        except Exception as e:
            raise Exception(f"Error creating department: {e}")
    
    async def update_department(
        self, 
        department_id: str, 
        department_data: DepartmentUpdate
    ) -> Optional[DepartmentResponse]:
        """Update a department."""
        try:
            # TODO: Implement actual update
            existing = await self.get_department(department_id)
            if not existing:
                return None
            
            updated_data = existing.dict()
            for field, value in department_data.dict(exclude_unset=True).items():
                updated_data[field] = value
            
            return DepartmentResponse(**updated_data)
        except Exception as e:
            raise Exception(f"Error updating department: {e}")
    
    async def delete_department(self, department_id: str) -> bool:
        """Delete a department."""
        try:
            # TODO: Implement actual deletion
            return True
        except Exception as e:
            raise Exception(f"Error deleting department: {e}")


