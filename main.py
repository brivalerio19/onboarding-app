from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

# Create SQLite tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Onboarding Orchestrator API",
    description="REST API with SQLite persistence via SQLAlchemy.",
    version="1.1.0",
)


# -------------------------------------------------------------------
# Enums & Pydantic Schemas
# -------------------------------------------------------------------
class ServiceType(str, Enum):
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    OKTA = "OKTA"
    AWS = "AWS"


class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    personal_email: EmailStr
    department: str
    role_title: str
    start_date: date


class OnboardingRequestCreate(BaseModel):
    employee: EmployeeCreate
    requested_by: EmailStr
    required_services: List[ServiceType] = Field(
        default=[ServiceType.GOOGLE_WORKSPACE, ServiceType.SLACK]
    )


class ProvisionItemResponse(BaseModel):
    id: UUID
    target_service: str
    status: str
    error_message: Optional[str] = None


class OnboardingRequestResponse(BaseModel):
    request_id: UUID
    status: str
    requested_by: EmailStr
    created_at: datetime
    services_queued: List[ProvisionItemResponse]


# -------------------------------------------------------------------
# Endpoints with Database Integration
# -------------------------------------------------------------------
@app.post(
    "/api/v1/onboarding",
    response_model=OnboardingRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_onboarding_request(
    payload: OnboardingRequestCreate, db: Session = Depends(get_db)
):
    request_id = str(uuid4())

    # 1. Create parent request record
    db_request = models.OnboardingRequestModel(
        id=request_id,
        employee_first_name=payload.employee.first_name,
        employee_last_name=payload.employee.last_name,
        employee_personal_email=payload.employee.personal_email,
        department=payload.employee.department,
        role_title=payload.employee.role_title,
        start_date=str(payload.employee.start_date),
        requested_by=payload.requested_by,
        status=models.OnboardingStatusEnum.PENDING,
    )
    db.add(db_request)

    # 2. Create child provision items
    provision_items = []
    for service in payload.required_services:
        item = models.ProvisionItemModel(
            id=str(uuid4()),
            request_id=request_id,
            target_service=service.value,
            status=models.ProvisionStatusEnum.PENDING,
        )
        db.add(item)
        provision_items.append(
            ProvisionItemResponse(
                id=UUID(item.id),
                target_service=item.target_service,
                status=item.status.value,
            )
        )

    # Commit transaction to SQLite
    db.commit()
    db.refresh(db_request)

    return OnboardingRequestResponse(
        request_id=UUID(db_request.id),
        status=db_request.status.value,
        requested_by=db_request.requested_by,
        created_at=db_request.created_at,
        services_queued=provision_items,
    )


@app.get(
    "/api/v1/onboarding/{request_id}",
    response_model=OnboardingRequestResponse,
)
def get_onboarding_status(request_id: UUID, db: Session = Depends(get_db)):
    db_request = (
        db.query(models.OnboardingRequestModel)
        .filter(models.OnboardingRequestModel.id == str(request_id))
        .first()
    )

    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Onboarding request '{request_id}' not found.",
        )

    services_queued = [
        ProvisionItemResponse(
            id=UUID(item.id),
            target_service=item.target_service,
            status=item.status.value,
            error_message=item.error_message,
        )
        for item in db_request.services
    ]

    return OnboardingRequestResponse(
        request_id=UUID(db_request.id),
        status=db_request.status.value,
        requested_by=db_request.requested_by,
        created_at=db_request.created_at,
        services_queued=services_queued,
    )