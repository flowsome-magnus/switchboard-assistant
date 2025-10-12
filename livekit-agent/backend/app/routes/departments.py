"""
Department management API routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends

from ..models.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from ..services.department_service import DepartmentService
from ..utils.dependencies import get_department_service

router = APIRouter(prefix="/api/departments", tags=["departments"])

@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get all departments."""
    try:
        departments = await department_service.get_departments()
        return departments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Get a specific department by ID."""
    try:
        department = await department_service.get_department(department_id)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        return department
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Create a new department."""
    try:
        department = await department_service.create_department(department_data)
        return department
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Update an existing department."""
    try:
        department = await department_service.update_department(department_id, department_data)
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        return department
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{department_id}")
async def delete_department(
    department_id: str,
    department_service: DepartmentService = Depends(get_department_service)
):
    """Delete a department."""
    try:
        success = await department_service.delete_department(department_id)
        if not success:
            raise HTTPException(status_code=404, detail="Department not found")
        return {"message": "Department deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


