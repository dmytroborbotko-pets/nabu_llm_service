"""
Test data models to ensure they validate correctly.
"""

from datetime import date, datetime
from uuid import uuid4

from src.models.entities import (
    Address,
    AnomalyDetection,
    AnomalyType,
    Company,
    CompanyFounder,
    CompanyHead,
    ContactInfo,
    DataSource,
    Employment,
    FinancialRecord,
    IdentificationDocument,
    Person,
    PersonName,
    RealEstate,
    RealEstateOwner,
    Relationship,
    RelationshipType,
    Vehicle,
    VehicleOwner,
)


def test_person_model():
    """Test Person model creation and validation."""
    person = Person(
        person_id=str(uuid4()),
        rnokpp="3347367890",
        unzr="19910824-12345",
        birth_date=date(1991, 8, 24),
        current_name=PersonName(
            last_name="Дія",
            first_name="Надія",
            middle_name="Володимирівна",
            last_name_latin="Diia",
            first_name_latin="Nadiia",
            middle_name_latin="Volodymyrivna"
        ),
        all_names=[],
        documents=[
            IdentificationDocument(
                document_type="passport",
                document_number="ЕН123456",
                issuer="ДМС України",
                issue_date=date(2015, 5, 10),
                expiry_date=date(2025, 5, 10)
            )
        ],
        contacts=[
            ContactInfo(
                contact_type="phone",
                value="+380501234567",
                is_primary=True
            )
        ],
        addresses=[
            Address(
                address_type="registration",
                full_address="м. Київ, вул. Хрещатик, буд. 1, кв. 10",
                region="Київська область",
                city="Київ",
                street="Хрещатик",
                building="1",
                apartment="10"
            )
        ],
        employment_history=[
            Employment(
                employer_name="ТОВ \"Тестова Компанія\"",
                employer_edrpou="12345678",
                position="Головний спеціаліст",
                start_date=date(2020, 1, 15),
                income=500000.0
            )
        ],
        data_sources=[DataSource.DMS, DataSource.DRFO]
    )

    # Validate model
    assert person.person_id is not None
    assert person.rnokpp == "3347367890"
    assert person.current_name.full_name() == "Дія Надія Володимирівна"
    assert person.current_name.full_name_latin() == "Diia Nadiia Volodymyrivna"
    assert len(person.documents) == 1
    assert len(person.contacts) == 1
    assert len(person.addresses) == 1
    assert len(person.employment_history) == 1

    print("✓ Person model test passed")
    return person


def test_company_model():
    """Test Company model creation and validation."""
    company = Company(
        company_id=str(uuid4()),
        edrpou="12345678",
        name="ТОВ \"Тестова Компанія\"",
        state="зареєстровано",
        founders=[
            CompanyFounder(
                founder_type="person",
                name="Іванов Іван Іванович",
                share=100.0,
                capital_contribution=100000.0,
                entry_date=date(2020, 1, 1)
            )
        ],
        heads=[
            CompanyHead(
                name="Іванов Іван Іванович",
                position="Директор",
                start_date=date(2020, 1, 1)
            )
        ],
        authorized_capital=100000.0,
        registration_date=date(2020, 1, 1),
        address="м. Київ, вул. Тестова, буд. 1",
        data_sources=[DataSource.EDR]
    )

    assert company.company_id is not None
    assert company.edrpou == "12345678"
    assert len(company.founders) == 1
    assert len(company.heads) == 1

    print("✓ Company model test passed")
    return company


def test_vehicle_model():
    """Test Vehicle model creation and validation."""
    vehicle = Vehicle(
        vehicle_id=str(uuid4()),
        vin="WBADT43452G123456",
        registration_number="АА1234ВВ",
        brand="BMW",
        model="X5",
        make_year=2020,
        color="чорний",
        fuel_type="бензин",
        current_owner=VehicleOwner(
            owner_type="person",
            name="Іванов Іван Іванович",
            ownership_start=date(2021, 3, 15)
        ),
        purchase_amount=1500000.0,
        data_sources=[DataSource.EIS]
    )

    assert vehicle.vehicle_id is not None
    assert vehicle.vin == "WBADT43452G123456"
    assert vehicle.current_owner.owner_type == "person"

    print("✓ Vehicle model test passed")
    return vehicle


def test_real_estate_model():
    """Test RealEstate model creation and validation."""
    real_estate = RealEstate(
        property_id=str(uuid4()),
        property_type="квартира",
        registration_number="12345678",
        full_address="м. Київ, вул. Тестова, буд. 10, кв. 5",
        total_area=85.5,
        cadastral_number="8000000000:01:001:0001",
        owners=[
            RealEstateOwner(
                owner_type="person",
                name="Іванов Іван Іванович",
                ownership_share=100.0,
                ownership_type="власність",
                registration_date=date(2019, 5, 20)
            )
        ],
        ownership_type="власність",
        data_sources=[DataSource.DRRP]
    )

    assert real_estate.property_id is not None
    assert real_estate.property_type == "квартира"
    assert len(real_estate.owners) == 1

    print("✓ RealEstate model test passed")
    return real_estate


def test_relationship_model():
    """Test Relationship model creation and validation."""
    person_id = str(uuid4())
    company_id = str(uuid4())

    relationship = Relationship(
        relationship_id=str(uuid4()),
        subject_id=person_id,
        subject_type="person",
        object_id=company_id,
        object_type="company",
        relationship_type=RelationshipType.FOUNDER,
        start_date=date(2020, 1, 1),
        properties={"share": 100.0},
        source=DataSource.EDR
    )

    assert relationship.relationship_id is not None
    assert relationship.relationship_type == RelationshipType.FOUNDER
    assert relationship.properties["share"] == 100.0

    print("✓ Relationship model test passed")
    return relationship


def test_anomaly_detection_model():
    """Test AnomalyDetection model creation and validation."""
    person_id = str(uuid4())

    anomaly = AnomalyDetection(
        anomaly_id=str(uuid4()),
        anomaly_type=AnomalyType.INCOME_ASSET_MISMATCH,
        person_id=person_id,
        severity="high",
        confidence=0.85,
        description="Total assets (5,000,000 UAH) exceed 25x declared income (200,000 UAH)",
        evidence=[
            {"type": "income", "amount": 200000, "years": 1},
            {"type": "vehicles", "count": 2, "value": 3000000},
            {"type": "real_estate", "count": 1, "value": 2000000}
        ]
    )

    assert anomaly.anomaly_id is not None
    assert anomaly.anomaly_type == AnomalyType.INCOME_ASSET_MISMATCH
    assert anomaly.severity == "high"
    assert anomaly.confidence == 0.85
    assert len(anomaly.evidence) == 3

    print("✓ AnomalyDetection model test passed")
    return anomaly


def test_financial_record_model():
    """Test FinancialRecord model creation and validation."""
    person_id = str(uuid4())

    record = FinancialRecord(
        record_id=str(uuid4()),
        person_id=person_id,
        record_type="income",
        year=2023,
        amount=500000.0,
        currency="UAH",
        description="Заробітна плата",
        source=DataSource.DRFO
    )

    assert record.record_id is not None
    assert record.record_type == "income"
    assert record.year == 2023
    assert record.amount == 500000.0

    print("✓ FinancialRecord model test passed")
    return record


def test_all_enums():
    """Test all enum values are accessible."""
    # Test DataSource enum
    assert DataSource.DMS == "ДМС"
    assert DataSource.NAZK == "НАЗК"
    assert DataSource.DRACS == "ДРАЦС"
    assert DataSource.EDR == "ЄДР"
    assert DataSource.DRRP == "ДРРП"
    assert DataSource.EIS == "ЄІС"
    assert DataSource.DRFO == "ДРФО"
    assert DataSource.DZK == "ДЗК"

    # Test RelationshipType enum
    assert RelationshipType.SPOUSE == "SPOUSE"
    assert RelationshipType.PARENT == "PARENT"
    assert RelationshipType.FOUNDER == "FOUNDER"
    assert RelationshipType.ASSET_OWNER == "ASSET_OWNER"

    # Test AnomalyType enum
    assert AnomalyType.INCOME_ASSET_MISMATCH == "INCOME_ASSET_MISMATCH"
    assert AnomalyType.UNDECLARED_ASSET == "UNDECLARED_ASSET"
    assert AnomalyType.RAPID_WEALTH_ACCUMULATION == "RAPID_WEALTH_ACCUMULATION"
    assert AnomalyType.SHELL_COMPANY == "SHELL_COMPANY"
    assert AnomalyType.CIRCULAR_OWNERSHIP == "CIRCULAR_OWNERSHIP"
    assert AnomalyType.RELATED_PARTY_TRANSACTION == "RELATED_PARTY_TRANSACTION"

    print("✓ All enums test passed")


def test_json_serialization():
    """Test models can be serialized to JSON."""
    person = test_person_model()

    # Test model_dump (Pydantic v2)
    person_dict = person.model_dump()
    assert person_dict["rnokpp"] == "3347367890"
    assert person_dict["current_name"]["last_name"] == "Дія"

    # Test model_dump_json (Pydantic v2)
    person_json = person.model_dump_json()
    assert "3347367890" in person_json
    assert "Дія" in person_json

    print("✓ JSON serialization test passed")


if __name__ == "__main__":
    print("\n=== Testing Data Models ===\n")

    test_all_enums()
    test_person_model()
    test_company_model()
    test_vehicle_model()
    test_real_estate_model()
    test_relationship_model()
    test_anomaly_detection_model()
    test_financial_record_model()
    test_json_serialization()

    print("\n=== All tests passed! ===\n")
