"""
Company service for handling business logic.
"""

from typing import Optional
from datetime import datetime

from ..models.company import (
    CompanyInfoUpdate,
    CompanyInfoResponse
)
from ...db.supabase_client import get_db_client

class CompanyService:
    """Service for company-related operations."""
    
    def __init__(self):
        self.db_client = get_db_client()
    
    async def get_company_info(self) -> Optional[CompanyInfoResponse]:
        """Get company information."""
        try:
            company_info = await self.db_client.get_company_info()
            if not company_info:
                return None
            
            return CompanyInfoResponse(
                id=company_info.id,
                company_name=company_info.company_name,
                greeting_message=company_info.greeting_message,
                business_hours=company_info.business_hours,
                settings=company_info.settings,
                created_at=datetime.utcnow(),  # TODO: Get from DB
                updated_at=datetime.utcnow()   # TODO: Get from DB
            )
        except Exception as e:
            raise Exception(f"Error getting company info: {e}")
    
    async def update_company_info(
        self, 
        company_data: CompanyInfoUpdate
    ) -> Optional[CompanyInfoResponse]:
        """Update company information."""
        try:
            # TODO: Implement actual update
            existing = await self.get_company_info()
            if not existing:
                return None
            
            updated_data = existing.dict()
            for field, value in company_data.dict(exclude_unset=True).items():
                updated_data[field] = value
            
            return CompanyInfoResponse(**updated_data)
        except Exception as e:
            raise Exception(f"Error updating company info: {e}")
    
    async def is_company_open(self, check_time: Optional[datetime] = None) -> bool:
        """Check if company is open."""
        try:
            return await self.db_client.is_company_open(check_time)
        except Exception as e:
            raise Exception(f"Error checking company hours: {e}")


