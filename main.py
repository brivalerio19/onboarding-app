from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field


# -------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------
class ServiceType(str, Enum):
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    OKTA = "OKTA"
    AWS = "AWS"


class ProvisionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class OnboardingStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PARTIALLY_FAILED = "PARTIALLY_FAILED"
    FAILED = "FAILED"


# -------------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------------
class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, example="Jane")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe")
    personal_email: EmailStr = Field(..., example="jane.doe@example.com")
    department: str = Field(..., example="Engineering")
    role_title: str = Field(..., example="Backend Developer")
    start_date: date = Field(..., example="2026-10-01")


class OnboardingRequestCreate(BaseModel):
    employee: EmployeeCreate
    requested_by: EmailStr = Field(..., example="hr.admin@company.com")
    required_services: List[ServiceType] = Field(
        default=[ServiceType.GOOGLE_WORKSPACE, ServiceType.SLACK],
        description="List of SaaS services to provision for this employee."
    )


class ProvisionItemResponse(BaseModel):
    id: UUID
    target_service: ServiceType
    status: ProvisionStatus
    error_message: Optional[str] = None


class OnboardingRequestResponse(BaseModel):
    request_id: UUID
    employee_id: UUID
    status: OnboardingStatus
    requested_by: EmailStr
    services_queued: List[ProvisionItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------------
# Application Setup & In-Memory Database
# -------------------------------------------------------------------
app = FastAPI(
    title="Automated Onboarding Orchestrator API",
    description="REST API for triggering and tracking user access provisioning.",
    version="1.0.0",
)

db_requests = {}


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------
@app.post(
    "/api/v1/onboarding",
    response_model=OnboardingRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create & Queue Onboarding Request",
)
async def create_onboarding_request(payload: OnboardingRequestCreate):
    request_id = uuid4()
    employee_id = uuid4()
    now = datetime.utcnow()

    provision_items = [
        ProvisionItemResponse(
            id=uuid4(),
            target_service=service,
            status=ProvisionStatus.PENDING,
        )
        for service in payload.required_services
    ]

    response_data = OnboardingRequestResponse(
        request_id=request_id,
        employee_id=employee_id,
        status=OnboardingStatus.PENDING,
        requested_by=payload.requested_by,
        services_queued=provision_items,
        created_at=now,
    )

    db_requests[request_id] = response_data
    return response_data


@app.get(
    "/api/v1/onboarding/{request_id}",
    response_model=OnboardingRequestResponse,
    summary="Get Onboarding Request Status",
)
async def get_onboarding_status(request_id: UUID):
    if request_id not in db_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Onboarding request '{request_id}' not found.",
        )
    return db_requests[request_id]