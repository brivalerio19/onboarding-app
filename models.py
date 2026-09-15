import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class OnboardingStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    PARTIALLY_FAILED = "PARTIALLY_FAILED"
    FAILED = "FAILED"


class ProvisionStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class OnboardingRequestModel(Base):
    __tablename__ = "onboarding_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_first_name = Column(String, nullable=False)
    employee_last_name = Column(String, nullable=False)
    employee_personal_email = Column(String, nullable=False)
    department = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    requested_by = Column(String, nullable=False)
    status = Column(SQLEnum(OnboardingStatusEnum), default=OnboardingStatusEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to provision items
    services = relationship("ProvisionItemModel", back_populates="request", cascade="all, delete-orphan")


class ProvisionItemModel(Base):
    __tablename__ = "provision_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("onboarding_requests.id"), nullable=False)
    target_service = Column(String, nullable=False)
    status = Column(SQLEnum(ProvisionStatusEnum), default=ProvisionStatusEnum.PENDING)
    error_message = Column(String, nullable=True)

    request = relationship("OnboardingRequestModel", back_populates="services")