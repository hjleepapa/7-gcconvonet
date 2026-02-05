"""
Healthcare Payer Models for Convonet
Database models for healthcare payer member services
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Numeric, Integer, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from enum import Enum as PyEnum
import uuid

from convonet.models.base import Base
from convonet.models.mortgage_models import EnumValueType


# ============================================================================
# ENUMS
# ============================================================================

class ClaimStatus(str, PyEnum):
    """Claim processing status"""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    PENDING_INFO = "pending_info"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    DENIED = "denied"
    PAID = "paid"
    APPEALED = "appealed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_DENIED = "appeal_denied"


class DenialReason(str, PyEnum):
    """Claim denial reasons"""
    NOT_COVERED = "not_covered"
    OUT_OF_NETWORK = "out_of_network"
    NO_PRIOR_AUTH = "no_prior_auth"
    NOT_MEDICALLY_NECESSARY = "not_medically_necessary"
    DUPLICATE_CLAIM = "duplicate_claim"
    TIMELY_FILING = "timely_filing"
    COORDINATION_OF_BENEFITS = "coordination_of_benefits"
    MAX_BENEFIT_REACHED = "max_benefit_reached"
    INCOMPLETE_INFO = "incomplete_info"
    EXPERIMENTAL = "experimental"
    PRE_EXISTING_CONDITION = "pre_existing_condition"


class PriorAuthStatus(str, PyEnum):
    """Prior authorization status"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"


class EligibilityStatus(str, PyEnum):
    """Member eligibility status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    TERMINATED = "terminated"
    COBRA = "cobra"
    SUSPENDED = "suspended"


class CoverageType(str, PyEnum):
    """Types of coverage"""
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PHARMACY = "pharmacy"
    MENTAL_HEALTH = "mental_health"
    PREVENTIVE = "preventive"


class NetworkTier(str, PyEnum):
    """Provider network tiers"""
    TIER_1 = "tier_1"  # Preferred/Lowest cost
    TIER_2 = "tier_2"  # Standard in-network
    TIER_3 = "tier_3"  # Out-of-network


class ServiceCategory(str, PyEnum):
    """Healthcare service categories"""
    OFFICE_VISIT = "office_visit"
    SPECIALIST_VISIT = "specialist_visit"
    EMERGENCY = "emergency"
    URGENT_CARE = "urgent_care"
    HOSPITAL_INPATIENT = "hospital_inpatient"
    HOSPITAL_OUTPATIENT = "hospital_outpatient"
    SURGERY = "surgery"
    DIAGNOSTIC_LAB = "diagnostic_lab"
    DIAGNOSTIC_IMAGING = "diagnostic_imaging"
    PREVENTIVE = "preventive"
    MENTAL_HEALTH = "mental_health"
    PHYSICAL_THERAPY = "physical_therapy"
    DURABLE_MEDICAL_EQUIPMENT = "durable_medical_equipment"
    PRESCRIPTION = "prescription"


# ============================================================================
# MODELS
# ============================================================================

class HealthcareMember(Base):
    """Healthcare plan member - extends user with insurance-specific data"""
    __tablename__ = "healthcare_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users_anthropic.id'), nullable=False, unique=True, index=True)
    
    # Member identification
    member_number = Column(String(50), unique=True, nullable=False, index=True)
    group_number = Column(String(50), nullable=True, index=True)
    subscriber_id = Column(UUID(as_uuid=True), nullable=True)  # For dependents, points to subscriber
    
    # Plan information
    plan_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_plans.id'), nullable=False)
    plan_name = Column(String(255), nullable=True)
    
    # Eligibility
    eligibility_status = Column(
        EnumValueType(EligibilityStatus),
        default=EligibilityStatus.ACTIVE,
        nullable=False,
        index=True
    )
    coverage_start_date = Column(DateTime(timezone=True), nullable=False)
    coverage_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Demographics
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    relationship_to_subscriber = Column(String(50), default="self")  # self, spouse, child, domestic_partner
    
    # Contact preferences
    preferred_contact_method = Column(String(50), default="email")  # email, phone, mail
    preferred_language = Column(String(10), default="en")
    
    # Metadata
    member_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    plan = relationship("HealthcarePlan", back_populates="members")
    claims = relationship("HealthcareClaim", back_populates="member", cascade="all, delete-orphan")
    prior_auths = relationship("PriorAuthorization", back_populates="member", cascade="all, delete-orphan")
    accumulations = relationship("MemberAccumulation", back_populates="member", cascade="all, delete-orphan")
    care_programs = relationship("MemberCareProgram", back_populates="member", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthcareMember(id={self.id}, member_number={self.member_number}, status={self.eligibility_status})>"


class HealthcarePlan(Base):
    """Healthcare insurance plan details"""
    __tablename__ = "healthcare_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan identification
    plan_code = Column(String(50), unique=True, nullable=False, index=True)
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(String(50), nullable=False)  # HMO, PPO, EPO, POS, HDHP
    
    # Plan year
    plan_year_start = Column(DateTime(timezone=True), nullable=False)
    plan_year_end = Column(DateTime(timezone=True), nullable=False)
    
    # Deductibles - Individual
    individual_deductible_in_network = Column(Numeric(10, 2), nullable=False)
    individual_deductible_out_of_network = Column(Numeric(10, 2), nullable=True)
    
    # Deductibles - Family
    family_deductible_in_network = Column(Numeric(10, 2), nullable=True)
    family_deductible_out_of_network = Column(Numeric(10, 2), nullable=True)
    
    # Out-of-Pocket Maximum - Individual
    individual_oop_max_in_network = Column(Numeric(10, 2), nullable=False)
    individual_oop_max_out_of_network = Column(Numeric(10, 2), nullable=True)
    
    # Out-of-Pocket Maximum - Family
    family_oop_max_in_network = Column(Numeric(10, 2), nullable=True)
    family_oop_max_out_of_network = Column(Numeric(10, 2), nullable=True)
    
    # Default cost-sharing
    default_copay = Column(Numeric(8, 2), default=30)
    default_coinsurance = Column(Numeric(5, 2), default=20)  # Percentage
    
    # Plan features
    requires_referral = Column(Boolean, default=False)  # HMO typically requires
    has_pharmacy_benefit = Column(Boolean, default=True)
    has_mental_health_parity = Column(Boolean, default=True)
    
    # Metadata
    plan_metadata = Column(JSON, nullable=True)  # Additional plan details, benefits schedule
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    members = relationship("HealthcareMember", back_populates="plan")
    benefits = relationship("PlanBenefit", back_populates="plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthcarePlan(id={self.id}, plan_code={self.plan_code}, type={self.plan_type})>"


class PlanBenefit(Base):
    """Specific benefit coverage for a plan"""
    __tablename__ = "plan_benefits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_plans.id'), nullable=False, index=True)
    
    # Benefit identification
    service_category = Column(
        EnumValueType(ServiceCategory),
        nullable=False,
        index=True
    )
    
    # Coverage details
    is_covered = Column(Boolean, default=True, nullable=False)
    requires_prior_auth = Column(Boolean, default=False)
    requires_referral = Column(Boolean, default=False)
    
    # Cost-sharing - In-Network
    copay_in_network = Column(Numeric(8, 2), nullable=True)
    coinsurance_in_network = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Cost-sharing - Out-of-Network
    copay_out_of_network = Column(Numeric(8, 2), nullable=True)
    coinsurance_out_of_network = Column(Numeric(5, 2), nullable=True)
    
    # Limits
    annual_limit = Column(Integer, nullable=True)  # Number of visits/services
    lifetime_limit = Column(Numeric(12, 2), nullable=True)  # Dollar amount
    
    # Notes
    coverage_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    plan = relationship("HealthcarePlan", back_populates="benefits")
    
    def __repr__(self):
        return f"<PlanBenefit(id={self.id}, category={self.service_category}, covered={self.is_covered})>"


class HealthcareClaim(Base):
    """Healthcare claim submitted for payment"""
    __tablename__ = "healthcare_claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_members.id'), nullable=False, index=True)
    
    # Claim identification
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Service information
    service_date = Column(DateTime(timezone=True), nullable=False)
    service_date_end = Column(DateTime(timezone=True), nullable=True)  # For date ranges
    place_of_service = Column(String(100), nullable=True)
    
    # Provider information
    provider_npi = Column(String(10), nullable=True, index=True)
    provider_name = Column(String(255), nullable=True)
    provider_network_tier = Column(
        EnumValueType(NetworkTier),
        nullable=True
    )
    
    # Diagnosis and procedure codes
    diagnosis_codes = Column(JSON, nullable=True)  # ICD-10 codes
    procedure_codes = Column(JSON, nullable=True)  # CPT/HCPCS codes
    
    # Financial - Billed
    billed_amount = Column(Numeric(12, 2), nullable=False)
    
    # Financial - Adjudicated
    allowed_amount = Column(Numeric(12, 2), nullable=True)
    paid_amount = Column(Numeric(12, 2), nullable=True)
    member_responsibility = Column(Numeric(12, 2), nullable=True)
    
    # Member cost breakdown
    deductible_applied = Column(Numeric(10, 2), default=0)
    copay_applied = Column(Numeric(10, 2), default=0)
    coinsurance_applied = Column(Numeric(10, 2), default=0)
    
    # Claim status
    status = Column(
        EnumValueType(ClaimStatus),
        default=ClaimStatus.SUBMITTED,
        nullable=False,
        index=True
    )
    
    # Denial information
    denial_reason = Column(
        EnumValueType(DenialReason),
        nullable=True
    )
    denial_details = Column(Text, nullable=True)
    
    # Prior authorization reference
    prior_auth_id = Column(UUID(as_uuid=True), ForeignKey('prior_authorizations.id'), nullable=True)
    
    # Processing dates
    received_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_date = Column(DateTime(timezone=True), nullable=True)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    
    # Appeal tracking
    is_appealed = Column(Boolean, default=False)
    appeal_date = Column(DateTime(timezone=True), nullable=True)
    appeal_reason = Column(Text, nullable=True)
    appeal_decision = Column(String(50), nullable=True)
    appeal_decision_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    claim_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    member = relationship("HealthcareMember", back_populates="claims")
    prior_auth = relationship("PriorAuthorization", back_populates="claims")
    line_items = relationship("ClaimLineItem", back_populates="claim", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_claims_member_date', 'member_id', 'service_date'),
        Index('ix_claims_member_status', 'member_id', 'status'),
    )
    
    def __repr__(self):
        return f"<HealthcareClaim(id={self.id}, claim_number={self.claim_number}, status={self.status})>"


class ClaimLineItem(Base):
    """Individual line items within a claim"""
    __tablename__ = "claim_line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_claims.id'), nullable=False, index=True)
    
    # Line item details
    line_number = Column(Integer, nullable=False)
    procedure_code = Column(String(20), nullable=False)
    procedure_description = Column(String(500), nullable=True)
    modifier_codes = Column(JSON, nullable=True)
    
    # Diagnosis link
    diagnosis_pointer = Column(Integer, nullable=True)  # Points to diagnosis in claim
    
    # Quantity and amounts
    units = Column(Integer, default=1)
    billed_amount = Column(Numeric(10, 2), nullable=False)
    allowed_amount = Column(Numeric(10, 2), nullable=True)
    paid_amount = Column(Numeric(10, 2), nullable=True)
    
    # Adjudication
    is_covered = Column(Boolean, default=True)
    denial_reason = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    claim = relationship("HealthcareClaim", back_populates="line_items")
    
    def __repr__(self):
        return f"<ClaimLineItem(id={self.id}, line={self.line_number}, code={self.procedure_code})>"


class PriorAuthorization(Base):
    """Prior authorization requests"""
    __tablename__ = "prior_authorizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_members.id'), nullable=False, index=True)
    
    # Authorization identification
    auth_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Request details
    procedure_code = Column(String(20), nullable=False)
    procedure_description = Column(String(500), nullable=True)
    diagnosis_codes = Column(JSON, nullable=True)
    
    # Provider information
    requesting_provider_npi = Column(String(10), nullable=True)
    requesting_provider_name = Column(String(255), nullable=True)
    servicing_provider_npi = Column(String(10), nullable=True)
    servicing_provider_name = Column(String(255), nullable=True)
    
    # Clinical information
    clinical_notes = Column(Text, nullable=True)
    supporting_documents = Column(JSON, nullable=True)
    
    # Authorization status
    status = Column(
        EnumValueType(PriorAuthStatus),
        default=PriorAuthStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Decision details
    decision_reason = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    # Approved details
    approved_units = Column(Integer, nullable=True)
    approved_from_date = Column(DateTime(timezone=True), nullable=True)
    approved_to_date = Column(DateTime(timezone=True), nullable=True)
    
    # Dates
    requested_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    decision_date = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Urgency
    is_urgent = Column(Boolean, default=False)
    
    # Metadata
    auth_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    member = relationship("HealthcareMember", back_populates="prior_auths")
    claims = relationship("HealthcareClaim", back_populates="prior_auth")
    
    def __repr__(self):
        return f"<PriorAuthorization(id={self.id}, auth_number={self.auth_number}, status={self.status})>"


class MemberAccumulation(Base):
    """Tracks member deductible and out-of-pocket accumulations"""
    __tablename__ = "member_accumulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_members.id'), nullable=False, index=True)
    
    # Plan year
    plan_year = Column(Integer, nullable=False)
    
    # Deductible accumulation
    individual_deductible_met_in_network = Column(Numeric(10, 2), default=0)
    individual_deductible_met_out_of_network = Column(Numeric(10, 2), default=0)
    family_deductible_met_in_network = Column(Numeric(10, 2), default=0)
    family_deductible_met_out_of_network = Column(Numeric(10, 2), default=0)
    
    # Out-of-pocket accumulation
    individual_oop_met_in_network = Column(Numeric(10, 2), default=0)
    individual_oop_met_out_of_network = Column(Numeric(10, 2), default=0)
    family_oop_met_in_network = Column(Numeric(10, 2), default=0)
    family_oop_met_out_of_network = Column(Numeric(10, 2), default=0)
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    member = relationship("HealthcareMember", back_populates="accumulations")
    
    # Unique constraint
    __table_args__ = (
        Index('ix_accumulations_member_year', 'member_id', 'plan_year', unique=True),
    )
    
    def __repr__(self):
        return f"<MemberAccumulation(id={self.id}, member_id={self.member_id}, year={self.plan_year})>"


class HealthcareProvider(Base):
    """Healthcare provider directory"""
    __tablename__ = "healthcare_providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Provider identification
    npi = Column(String(10), unique=True, nullable=False, index=True)
    tax_id = Column(String(20), nullable=True)
    
    # Provider information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    organization_name = Column(String(255), nullable=True)
    
    # Specialty
    primary_specialty = Column(String(100), nullable=True)
    secondary_specialties = Column(JSON, nullable=True)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    fax = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address
    address_line_1 = Column(String(255), nullable=True)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Network status
    network_tier = Column(
        EnumValueType(NetworkTier),
        default=NetworkTier.TIER_2,
        nullable=False,
        index=True
    )
    is_accepting_patients = Column(Boolean, default=True)
    
    # Quality metrics
    quality_rating = Column(Numeric(3, 2), nullable=True)  # 0-5 scale
    patient_reviews_count = Column(Integer, default=0)
    
    # Languages spoken
    languages = Column(JSON, nullable=True)
    
    # Hospital affiliations
    hospital_affiliations = Column(JSON, nullable=True)
    
    # Metadata
    provider_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_provider_specialty_zip', 'primary_specialty', 'zip_code'),
        Index('ix_provider_network_zip', 'network_tier', 'zip_code'),
    )
    
    def __repr__(self):
        return f"<HealthcareProvider(id={self.id}, npi={self.npi}, name={self.last_name or self.organization_name})>"


class CareProgram(Base):
    """Care management programs available"""
    __tablename__ = "care_programs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Program identification
    program_code = Column(String(50), unique=True, nullable=False, index=True)
    program_name = Column(String(255), nullable=False)
    program_type = Column(String(100), nullable=False)  # disease_management, wellness, chronic_care
    
    # Program details
    description = Column(Text, nullable=True)
    eligibility_criteria = Column(Text, nullable=True)
    
    # Target conditions
    target_conditions = Column(JSON, nullable=True)  # List of condition codes/names
    
    # Program features
    includes_coaching = Column(Boolean, default=False)
    includes_monitoring = Column(Boolean, default=False)
    includes_rewards = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    enrolled_members = relationship("MemberCareProgram", back_populates="program")
    
    def __repr__(self):
        return f"<CareProgram(id={self.id}, code={self.program_code}, name={self.program_name})>"


class MemberCareProgram(Base):
    """Member enrollment in care programs"""
    __tablename__ = "member_care_programs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey('healthcare_members.id'), nullable=False, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey('care_programs.id'), nullable=False, index=True)
    
    # Enrollment status
    enrolled_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    disenrolled_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Progress tracking
    completion_percentage = Column(Numeric(5, 2), default=0)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    enrollment_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    member = relationship("HealthcareMember", back_populates="care_programs")
    program = relationship("CareProgram", back_populates="enrolled_members")
    
    # Unique constraint - member can only be enrolled once in a program
    __table_args__ = (
        Index('ix_member_program', 'member_id', 'program_id', unique=True),
    )
    
    def __repr__(self):
        return f"<MemberCareProgram(id={self.id}, member_id={self.member_id}, program_id={self.program_id})>"
