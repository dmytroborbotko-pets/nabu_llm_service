"""
Data models for NABU AI Platform entities.

This module defines all Pydantic models for persons, companies, vehicles,
real estate, relationships, and anomaly detection.
"""

from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


# ============================================================================
# ENUMS
# ============================================================================

class DataSource(str, Enum):
    """Data sources for entity information."""
    DMS = "ДМС"  # State Migration Service (documents, addresses)
    NAZK = "НАЗК"  # National Anti-Corruption Agency (declarations)
    DRACS = "ДРАЦС"  # Civil Status Acts Registry (birth, marriage, divorce)
    EDR = "ЄДР"  # Unified State Registry (companies)
    DRRP = "ДРРП"  # Real Estate Registry (property ownership)
    EIS = "ЄІС"  # Unified Information System (vehicles)
    DRFO = "ДРФО"  # State Tax Service (income)
    DZK = "ДЗК"  # Land Cadastre (land parcels)
    COURT = "СУД"  # Court registries
    OTHER = "ІНШЕ"  # Other sources


class RelationshipType(str, Enum):
    """Types of relationships between entities."""
    # Family relationships
    SPOUSE = "SPOUSE"
    PARENT = "PARENT"
    CHILD = "CHILD"
    SIBLING = "SIBLING"

    # Business relationships
    FOUNDER = "FOUNDER"
    HEAD = "HEAD"
    EMPLOYEE = "EMPLOYEE"
    SHAREHOLDER = "SHAREHOLDER"
    BENEFICIARY = "BENEFICIARY"

    # Asset ownership
    ASSET_OWNER = "ASSET_OWNER"
    VEHICLE_OWNER = "VEHICLE_OWNER"
    PROPERTY_OWNER = "PROPERTY_OWNER"

    # Other
    RELATED_PARTY = "RELATED_PARTY"
    UNKNOWN = "UNKNOWN"


class AnomalyType(str, Enum):
    """Types of detected anomalies."""
    INCOME_ASSET_MISMATCH = "INCOME_ASSET_MISMATCH"  # Assets > 10x income
    UNDECLARED_ASSET = "UNDECLARED_ASSET"  # Asset without income source
    RAPID_WEALTH_ACCUMULATION = "RAPID_WEALTH_ACCUMULATION"  # Multiple assets in short period
    SHELL_COMPANY = "SHELL_COMPANY"  # Offshore founders, short lifespan
    CIRCULAR_OWNERSHIP = "CIRCULAR_OWNERSHIP"  # Cycle in ownership graph
    RELATED_PARTY_TRANSACTION = "RELATED_PARTY_TRANSACTION"  # Transaction between related persons


# ============================================================================
# NESTED MODELS
# ============================================================================

class PersonName(BaseModel):
    """Person name with Ukrainian and Latin transliterations."""
    last_name: str = Field(description="Прізвище / Surname")
    first_name: str = Field(description="Ім'я / First name")
    middle_name: Optional[str] = Field(None, description="По батькові / Patronymic")
    last_name_latin: Optional[str] = Field(None, description="Surname in Latin")
    first_name_latin: Optional[str] = Field(None, description="First name in Latin")
    middle_name_latin: Optional[str] = Field(None, description="Patronymic in Latin")
    valid_from: Optional[date] = Field(None, description="Name valid from date")
    valid_to: Optional[date] = Field(None, description="Name valid to date")
    source: Optional[str] = Field(None, description="Data source for this name")

    def full_name(self) -> str:
        """Get full name in Ukrainian."""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    def full_name_latin(self) -> Optional[str]:
        """Get full name in Latin."""
        if not self.last_name_latin:
            return None
        parts = [self.last_name_latin, self.first_name_latin or ""]
        if self.middle_name_latin:
            parts.append(self.middle_name_latin)
        return " ".join(parts).strip()


class IdentificationDocument(BaseModel):
    """Identification document information."""
    document_type: str = Field(description="Document type (passport, ID card, etc.)")
    document_number: str = Field(description="Document number")
    series: Optional[str] = Field(None, description="Document series")
    issuer: Optional[str] = Field(None, description="Issuing authority")
    issue_date: Optional[date] = Field(None, description="Issue date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    source: Optional[str] = Field(None, description="Data source")


class ContactInfo(BaseModel):
    """Contact information."""
    contact_type: str = Field(description="Type (phone, email, social_media, etc.)")
    value: str = Field(description="Contact value")
    is_primary: bool = Field(False, description="Is primary contact")
    valid_from: Optional[date] = Field(None, description="Valid from date")
    valid_to: Optional[date] = Field(None, description="Valid to date")
    source: Optional[str] = Field(None, description="Data source")


class Address(BaseModel):
    """Address information with structured fields."""
    address_type: str = Field(description="Type (registration, residence, usage, other)")
    full_address: str = Field(description="Full address string")
    region: Optional[str] = Field(None, description="Region/Oblast")
    city: Optional[str] = Field(None, description="City/Town")
    street: Optional[str] = Field(None, description="Street name")
    building: Optional[str] = Field(None, description="Building number")
    apartment: Optional[str] = Field(None, description="Apartment number")
    postal_code: Optional[str] = Field(None, description="Postal code")
    valid_from: Optional[date] = Field(None, description="Valid from date")
    valid_to: Optional[date] = Field(None, description="Valid to date")
    source: Optional[str] = Field(None, description="Data source")


class Employment(BaseModel):
    """Employment history entry."""
    employer_name: str = Field(description="Employer name")
    employer_edrpou: Optional[str] = Field(None, description="Employer business code")
    position: str = Field(description="Job position/title")
    department: Optional[str] = Field(None, description="Department/division")
    start_date: Optional[date] = Field(None, description="Employment start date")
    end_date: Optional[date] = Field(None, description="Employment end date (None if current)")
    income: Optional[float] = Field(None, description="Declared income amount")
    source: Optional[str] = Field(None, description="Data source")


class CompanyFounder(BaseModel):
    """Company founder information."""
    founder_type: str = Field(description="Type (person, company)")
    founder_id: Optional[str] = Field(None, description="Person or company ID")
    name: str = Field(description="Founder name")
    edrpou: Optional[str] = Field(None, description="EDRPOU if legal entity")
    share: Optional[float] = Field(None, description="Ownership share percentage")
    capital_contribution: Optional[float] = Field(None, description="Capital contribution amount")
    entry_date: Optional[date] = Field(None, description="Date entered as founder")
    exit_date: Optional[date] = Field(None, description="Date exited as founder")


class CompanyHead(BaseModel):
    """Company head/director information."""
    person_id: Optional[str] = Field(None, description="Person ID if known")
    name: str = Field(description="Full name")
    position: str = Field(description="Position title")
    start_date: Optional[date] = Field(None, description="Position start date")
    end_date: Optional[date] = Field(None, description="Position end date (None if current)")


class ActivityKind(BaseModel):
    """Company activity kind (KVED code)."""
    code: str = Field(description="KVED activity code")
    name: str = Field(description="Activity description")
    is_primary: bool = Field(False, description="Is primary activity")


class VehicleOwner(BaseModel):
    """Vehicle owner information."""
    owner_type: str = Field(description="Type (person, company)")
    owner_id: Optional[str] = Field(None, description="Person or company ID")
    name: str = Field(description="Owner name")
    ownership_start: Optional[date] = Field(None, description="Ownership start date")
    ownership_end: Optional[date] = Field(None, description="Ownership end date (None if current)")


class RealEstateOwner(BaseModel):
    """Real estate owner information."""
    owner_type: str = Field(description="Type (person, company)")
    owner_id: Optional[str] = Field(None, description="Person or company ID")
    name: str = Field(description="Owner name")
    ownership_share: Optional[float] = Field(None, description="Ownership share percentage")
    ownership_type: str = Field(description="Ownership type (full, shared, etc.)")
    registration_date: Optional[date] = Field(None, description="Ownership registration date")


# ============================================================================
# MAIN ENTITY MODELS
# ============================================================================

class Person(BaseModel):
    """Person entity with all associated data."""
    person_id: str = Field(description="Unique person identifier (UUID)")
    rnokpp: Optional[str] = Field(None, description="Tax identification number (РНОКПП)")
    unzr: Optional[str] = Field(None, description="Civil registry number (УНЗР)")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    current_name: PersonName = Field(description="Current official name")
    all_names: List[PersonName] = Field(default_factory=list, description="Name history including former names")
    documents: List[IdentificationDocument] = Field(default_factory=list, description="Identification documents")
    contacts: List[ContactInfo] = Field(default_factory=list, description="Contact information")
    addresses: List[Address] = Field(default_factory=list, description="Address history")
    employment_history: List[Employment] = Field(default_factory=list, description="Employment history")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Additional information")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Record update timestamp")


class Company(BaseModel):
    """Company/legal entity information."""
    company_id: str = Field(description="Unique company identifier (UUID)")
    edrpou: str = Field(description="Business registry code (ЄДРПОУ)")
    name: str = Field(description="Company name")
    state: str = Field(description="Company state (зареєстровано, припинено, etc.)")
    founders: List[CompanyFounder] = Field(default_factory=list, description="Company founders")
    heads: List[CompanyHead] = Field(default_factory=list, description="Company heads/directors")
    authorized_capital: Optional[float] = Field(None, description="Authorized capital amount")
    registration_date: Optional[date] = Field(None, description="Registration date")
    termination_date: Optional[date] = Field(None, description="Termination date (if terminated)")
    activity_kinds: List[ActivityKind] = Field(default_factory=list, description="Activity kinds (KVED codes)")
    address: Optional[str] = Field(None, description="Registered address")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Record update timestamp")


class Vehicle(BaseModel):
    """Vehicle information."""
    vehicle_id: str = Field(description="Unique vehicle identifier (UUID)")
    vin: str = Field(description="Vehicle identification number")
    registration_number: str = Field(description="Registration plate number")
    brand: str = Field(description="Vehicle brand")
    model: str = Field(description="Vehicle model")
    make_year: Optional[int] = Field(None, description="Manufacturing year")
    color: str = Field(description="Vehicle color")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    current_owner: VehicleOwner = Field(description="Current owner information")
    operation_date: Optional[datetime] = Field(None, description="Last operation date")
    purchase_amount: Optional[float] = Field(None, description="Purchase amount if known")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Record update timestamp")


class RealEstate(BaseModel):
    """Real estate property information."""
    property_id: str = Field(description="Unique property identifier (UUID)")
    property_type: str = Field(description="Property type (квартира, будинок, земельна ділянка, etc.)")
    registration_number: str = Field(description="Registry number")
    full_address: str = Field(description="Full property address")
    total_area: Optional[float] = Field(None, description="Total area in square meters")
    cadastral_number: Optional[str] = Field(None, description="Cadastral number")
    owners: List[RealEstateOwner] = Field(default_factory=list, description="Property owners")
    ownership_type: str = Field(description="Ownership type (власність, оренда, etc.)")
    acquisition_document_type: Optional[str] = Field(None, description="Acquisition document type")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now, description="Record update timestamp")


class FinancialRecord(BaseModel):
    """Financial record (income/tax data)."""
    record_id: str = Field(description="Unique record identifier (UUID)")
    person_id: Optional[str] = Field(None, description="Associated person ID")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    record_type: str = Field(description="Record type (income, tax, declaration, etc.)")
    year: int = Field(description="Tax/reporting year")
    amount: float = Field(description="Amount in UAH")
    currency: str = Field(default="UAH", description="Currency code")
    description: Optional[str] = Field(None, description="Description")
    source: DataSource = Field(description="Data source")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")


class Relationship(BaseModel):
    """Relationship between entities."""
    relationship_id: str = Field(description="Unique relationship identifier (UUID)")
    subject_id: str = Field(description="Subject entity ID")
    subject_type: str = Field(description="Subject entity type (person, company, vehicle, real_estate)")
    object_id: str = Field(description="Object entity ID")
    object_type: str = Field(description="Object entity type (person, company, vehicle, real_estate)")
    relationship_type: RelationshipType = Field(description="Type of relationship")
    start_date: Optional[date] = Field(None, description="Relationship start date")
    end_date: Optional[date] = Field(None, description="Relationship end date (None if current)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional relationship properties")
    source: DataSource = Field(description="Data source")
    created_at: datetime = Field(default_factory=utc_now, description="Record creation timestamp")


class AnomalyDetection(BaseModel):
    """Detected anomaly information."""
    anomaly_id: str = Field(description="Unique anomaly identifier (UUID)")
    anomaly_type: AnomalyType = Field(description="Type of anomaly")
    person_id: Optional[str] = Field(None, description="Associated person ID")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)", ge=0.0, le=1.0)
    description: str = Field(description="Human-readable description")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Evidence supporting the anomaly")
    detected_at: datetime = Field(default_factory=utc_now, description="Detection timestamp")
