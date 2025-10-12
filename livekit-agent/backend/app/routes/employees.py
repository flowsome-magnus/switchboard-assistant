"""
Employee management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime

from ..models.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeSearchRequest,
    EmployeeAvailabilityRequest,
    EmployeeAvailabilityResponse
)
from ..services.employee_service import EmployeeService
from ..utils.dependencies import get_employee_service

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Get all employees with optional filtering."""
    try:
        employees = await employee_service.get_employees(
            department_id=department_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset
        )
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[EmployeeResponse])
async def search_employees(
    request: EmployeeSearchRequest,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Search employees by query, department, or status."""
    try:
        employees = await employee_service.search_employees(
            query=request.query,
            department=request.department,
            status=request.status
        )
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available", response_model=List[EmployeeResponse])
async def get_available_employees(
    department: Optional[str] = Query(None, description="Filter by department name"),
    check_time: Optional[datetime] = Query(None, description="Check availability at specific time"),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Get available employees for a department."""
    try:
        employees = await employee_service.get_available_employees(
            department=department,
            check_time=check_time
        )
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: str,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Get a specific employee by ID."""
    try:
        employee = await employee_service.get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phone/{phone}", response_model=EmployeeResponse)
async def get_employee_by_phone(
    phone: str,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Get employee by phone number."""
    try:
        employee = await employee_service.get_employee_by_phone(phone)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Create a new employee."""
    try:
        employee = await employee_service.create_employee(employee_data)
        return employee
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Update an existing employee."""
    try:
        employee = await employee_service.update_employee(employee_id, employee_data)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: str,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Delete an employee."""
    try:
        success = await employee_service.delete_employee(employee_id)
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"message": "Employee deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/availability", response_model=EmployeeAvailabilityResponse)
async def check_employee_availability(
    request: EmployeeAvailabilityRequest,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """Check if an employee is available at a specific time."""
    try:
        is_available = await employee_service.is_employee_available(
            request.employee_id,
            request.check_time
        )
        return EmployeeAvailabilityResponse(
            employee_id=request.employee_id,
            is_available=is_available,
            check_time=request.check_time or datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


