"""
Company management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from ..models.company import (
    CompanyInfoUpdate,
    CompanyInfoResponse,
    CompanyHoursRequest,
    CompanyHoursResponse
)
from ..services.company_service import CompanyService
from ..utils.dependencies import get_company_service

router = APIRouter(prefix="/api/company", tags=["company"])

@router.get("/", response_model=CompanyInfoResponse)
async def get_company_info(
    company_service: CompanyService = Depends(get_company_service)
):
    """Get company information and settings."""
    try:
        company_info = await company_service.get_company_info()
        if not company_info:
            raise HTTPException(status_code=404, detail="Company info not found")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/", response_model=CompanyInfoResponse)
async def update_company_info(
    company_data: CompanyInfoUpdate,
    company_service: CompanyService = Depends(get_company_service)
):
    """Update company information and settings."""
    try:
        company_info = await company_service.update_company_info(company_data)
        if not company_info:
            raise HTTPException(status_code=404, detail="Company info not found")
        return company_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hours", response_model=CompanyHoursResponse)
async def check_company_hours(
    request: CompanyHoursRequest,
    company_service: CompanyService = Depends(get_company_service)
):
    """Check if company is currently open."""
    try:
        is_open = await company_service.is_company_open(request.check_time)
        return CompanyHoursResponse(
            is_open=is_open,
            check_time=request.check_time or datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


