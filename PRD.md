# Product Requirements Document (PRD)
## NABU Registry AI Platform - Automated Person Profile Analysis

**Project:** nabu_llm_service
**Version:** 1.0 MVP
**Timeline:** 4 days
**Date:** 2026-01-12
**Author:** AI-Generated PRD based on stakeholder requirements

---

## 1. Executive Summary

### 1.1 Project Overview
Development of an AI-powered platform that automatically processes multi-format data from Ukrainian government registries (NABU data) to create unified person profiles, detect financial anomalies, build relationship networks, and generate comprehensive PDF reports for anti-corruption analysis.

### 1.2 Business Objectives
- **Automate** manual data consolidation from 10+ different registry formats
- **Unify** fragmented person records into single comprehensive profiles
- **Detect** financial discrepancies between declared income and owned assets
- **Visualize** hidden relationships between persons, companies, and assets
- **Generate** professional PDF reports matching institutional standards

### 1.3 Success Criteria
- Successfully parse 100% of 207 existing case files (JSON/XML formats)
- Consolidate duplicate person records with >90% accuracy
- Detect at least 5 categories of financial anomalies
- Generate PDF reports matching the provided sample format
- Process entire dataset within 30 minutes on standard hardware

---

## 2. Current State Analysis

### 2.1 Available Data
**Location:** `/nabu_data/` directory containing 207 case directories

**Registry Types** (27 identified):
1. **EDR** (Єдиний державний реєстр) - Business registry
2. **EIS** (Єдина інформаційна система) - Vehicle registrations
3. **DRRP** (Державний реєстр речових прав) - Real estate ownership
4. **DRFO** (Державна фіскальна служба) - Tax and income data
5. **DRACS** (Державний реєстр актів цивільного стану) - Civil status acts (birth, marriage, divorce, death, name changes)
6. **DZK** (Державний земельний кадастр) - Land cadastre
7. **DSR** (Державний спадковий реєстр) - Inheritance information
8. **ARKAN** - Border crossing records
9. **ERD** - Power of attorney registry
10. Court records, archives, and more

**Data Statistics:**
- **Case directories:** 207 (890-ТМ-Д: 96, 891-ТМ-Д: 7, 995-ІБ-Д: 104)
- **File formats:** JSON (32 files), XML (176 files)
- **File sizes:** 121 bytes to 4.6 MB
- **Request types:** 995-ІБ-Д contains queries (З-2025-*), 890/891-ТМ-Д contains responses (В-2025-*)

### 2.2 Sample Output
Reference: `nabu_data/Профіль-зразок.pdf`

**Profile Structure:**
- Personal data (name, DOB, RNOKPП, УНЗР, photo placeholder)
- Name history (former names with date ranges)
- Identification documents (passports, ID cards)
- Contact information (phones, emails, social media)
- Address history (registration, residence, usage addresses)
- Employment history (chronological)
- Related persons (family relationships)
- Related legal entities (companies founded/managed)
- Asset ownership (vehicles, real estate) - *not in sample but required*
- Financial anomalies - *not in sample but required*

---

## 3. Functional Requirements

### 3.1 Core Features (MVP - Must Have)

#### FR-1: Multi-Format Data Parsing (HYBRID APPROACH)
**Priority:** CRITICAL
**Description:** Convert all data formats to clean JSON WITHOUT semantic understanding

**Acceptance Criteria:**
- **XML files:** Parse using lxml with SOAP envelope unwrapping (NO registry-specific logic)
- **JSON files:** Validate and clean JSON structure (NO schema-specific validation)
- **HTML files:** Extract tables and forms using BeautifulSoup (NO semantic interpretation)
- **Excel files (.xls, .xlsx):** Parse to DataFrame using openpyxl/pandas (NO domain logic)
- **CSV files:** Parse with encoding detection (UTF-8, Windows-1251)
- **Plain text files (.txt):** Extract using regex patterns (NO NLP at this stage)
- Handle malformed data gracefully (log errors, continue processing)
- Auto-detect file format and encoding
- Preserve ALL fields without interpretation
- Track data provenance (source file, registry type from filename, timestamp)

**Implementation Notes (HYBRID PHILOSOPHY):**
- **NO registry-specific parsers** - generic format handlers only
- **NO semantic extraction** - just format conversion (XML/HTML/CSV → JSON)
- **NO entity recognition** - preserve raw data structure
- **Stage 2 LLM does ALL semantic work** - extraction, normalization, classification
- Use Pydantic for data validation
- Implement format detector with factory pattern

---

#### FR-2: Unified Person Profile Formation (LLM-POWERED)
**Priority:** CRITICAL
**Description:** Extract and consolidate all information about persons using LLM batch processing

**Acceptance Criteria:**
- **Stage 2 (LLM):** Extract person entities from normalized JSON (all registry types)
- **Stage 2 (LLM):** Normalize name variations (Cyrillic, Latin, transliterations)
- **Stage 2 (LLM):** Parse and normalize dates to ISO 8601
- **Stage 2 (LLM):** Classify address types (registration, residence, etc.)
- **Stage 3 (Rule-based):** Deduplicate persons using RNOKPP, УНЗР, DOB, and name matching
- **Stage 3 (Rule-based):** Merge records with confidence scoring
- Track all name changes chronologically
- Consolidate all addresses with type classification
- Aggregate employment history
- Collect all identification documents
- Preserve data source attribution for each field
- Generate unique person_id for each consolidated profile

**Data Fields Required:**
```
Person Profile:
  ├── Personal Data
  │   ├── Current name (Ukrainian + Latin)
  │   ├── Birth date
  │   ├── RNOKPP (tax ID)
  │   ├── УНЗР (civil registry number)
  │   └── Photo placeholder
  ├── Name History
  │   └── Previous names with validity periods
  ├── Identification
  │   └── Documents (type, number, issuer, dates)
  ├── Contacts
  │   └── Phones, emails, social media
  ├── Addresses
  │   └── Registration, residence, usage, other
  ├── Employment
  │   └── Job history with dates
  ├── Related Persons
  │   └── Family relationships
  └── Related Companies
      └── Founded, managed, employed
```

**Deduplication Logic:**
1. **Exact match** (confidence = 1.0): Same RNOKPP or УНЗР
2. **High confidence** (0.8-0.95): Same DOB + fuzzy name match + address overlap
3. **Medium confidence** (0.6-0.79): Same DOB + fuzzy name match
4. **Low confidence** (<0.6): Require manual review or additional signals

---

#### FR-3: Relationship Graph Construction
**Priority:** CRITICAL
**Description:** Build network of connections between persons, companies, and assets

**Acceptance Criteria:**
- Create nodes for persons, companies, vehicles, real estate
- Extract relationships from all registries:
  - Family: parent_of, child_of, spouse_of, divorced_from
  - Business: founder_of, head_of, employee_of
  - Assets: owns_vehicle, owns_real_estate, owns_land
  - Financial: income_from
- Store relationships with temporal validity (start/end dates)
- Support bidirectional traversal
- Track relationship provenance (data source)
- Enable path finding between any two entities

**Graph Schema:**
```
Nodes:
  - Person {person_id, name, rnokpp, birth_date}
  - Company {company_id, edrpou, name, state}
  - Vehicle {vehicle_id, vin, brand, model}
  - RealEstate {property_id, address, area, cadastral_number}

Edges:
  - Relationship {rel_id, subject_id, object_id, type, start_date, end_date}

Relationship Types:
  - parent_of, child_of, spouse_of, divorced_from
  - founder_of, head_of, employee_of
  - owns_vehicle, owns_real_estate
  - income_from
```

**Implementation:**
- File-based adjacency lists in `/data/graph/`
- Indices for fast lookup by person_id, rnokpp, company_edrpou
- JSON files for easy inspection and debugging

---

#### FR-4: Financial Anomaly Detection
**Priority:** CRITICAL
**Description:** Identify discrepancies between income and assets

**Acceptance Criteria:**
- Detect income vs asset value mismatches (ratio > 10x)
- Identify undeclared or suspiciously acquired assets
- Flag rapid wealth accumulation patterns
- Detect shell company indicators:
  - Offshore founders (Cyprus, BVI, etc.)
  - Short operational lifespan (<1 year)
  - High capital with quick termination
- Identify circular ownership structures
- Flag related-party transactions
- Generate anomaly reports with:
  - Severity level (low/medium/high/critical)
  - Confidence score (0.0-1.0)
  - Evidence list with sources
  - Plain language explanation

**Anomaly Types:**
```
1. INCOME_ASSET_MISMATCH
   - Total assets > 10x declared income
   - Example: 5M UAH in property, 200K UAH declared income

2. UNDECLARED_ASSET
   - Asset owned but no corresponding income source
   - Example: Luxury vehicle with no employment history

3. RAPID_WEALTH_ACCUMULATION
   - Multiple high-value assets acquired in short period
   - Example: 3 properties purchased in 6 months

4. SHELL_COMPANY
   - Company with offshore founders, short lifespan, no real activity
   - Example: Cyprus-founded company terminated after 3 months

5. CIRCULAR_OWNERSHIP
   - Company A owns Company B, Company B owns Company A
   - Detected via cycle detection in ownership graph

6. RELATED_PARTY_TRANSACTION
   - Person sells asset to related person (family/business)
   - Example: Spouse sells property to spouse
```

**Asset Valuation Logic:**
```python
# Vehicle valuation (simplified)
vehicle_value = base_value_by_brand_model[brand][model] * depreciation_by_year[make_year]

# Real estate valuation (simplified)
property_value = area_sqm * avg_price_per_sqm_by_region[region]

# Total assets
total_assets = sum(vehicle_values) + sum(property_values)

# Income calculation
total_declared_income = sum(income_records over all years)

# Anomaly threshold
if total_assets / total_declared_income > 10:
    flag_anomaly(INCOME_ASSET_MISMATCH)
```

---

#### FR-5: PDF Report Generation
**Priority:** CRITICAL
**Description:** Generate professional PDF reports matching the sample format

**Acceptance Criteria:**
- Match exact layout from `Профіль-зразок.pdf`
- Include all sections with proper Ukrainian labels
- Use tables for structured data
- Support UTF-8 Ukrainian text
- Include photo placeholder
- Generate within 5 seconds per report
- Output file size < 5 MB per report

**Report Sections:**
1. **Header:** Name, photo, RNOKPP, УНЗР, generation date
2. **Колишні ПІБ:** Previous names table
3. **Інші ідентифікаційні дані:** Other IDs
4. **Контактні дані:** Contact information
5. **Документи:** Documents table
6. **Пов'язані адреси:** Addresses table
7. **Додаткова інформація:** Current position and employer
8. **Додаток: Трудова діяльність:** Employment history
9. **Додаток: Пов'язані особи:** Related persons and companies
10. **Додаток: Майно:** Assets (vehicles, real estate) *[NEW]*
11. **Додаток: Фінансові аномалії:** Detected anomalies *[NEW]*

**Technical Implementation:**
- Use ReportLab or WeasyPrint for PDF generation
- HTML template → PDF conversion
- Support table pagination for long lists
- Ukrainian font support (DejaVu Sans or similar)

---

### 3.2 Non-Functional Requirements

#### NFR-1: Performance
- **Stage 1 (Format normalization):** Process 207 files in < 5 minutes
- **Stage 2 (LLM batch extraction):** Complete in < 15 minutes (limited by API)
- **Stage 3 (Entity resolution):** Deduplicate in < 5 minutes
- **Stage 4 (Graph construction):** Build complete graph in < 5 minutes
- **Stage 5 (Anomaly detection):** Analyze all persons in < 5 minutes
- **Stage 6 (PDF generation):** Generate 1 report in < 5 seconds
- **Total pipeline:** Complete run in < 30 minutes

#### NFR-2: Scalability
- Support up to 1,000 person profiles in MVP
- Design for easy migration to database (PostgreSQL/Neo4j)
- Modular architecture with swappable storage backends
- Parallel processing where possible (multiprocessing)

#### NFR-3: Reliability
- Checkpoint system to resume after failures
- Robust error handling with detailed logging
- Data validation at each pipeline stage
- Idempotent operations (can re-run safely)

#### NFR-4: Maintainability
- Clear separation of concerns (parsers, extractors, analyzers, reporters)
- Comprehensive logging with loguru
- Type hints throughout codebase
- Pydantic models for all data structures
- CLI interface for all operations

#### NFR-5: Efficiency
- Minimize LLM API calls through aggressive batching
- Batch size: 50 files per request
- Total LLM calls: ~5 batched requests for entire dataset
- NO LLM usage in Stages 1, 3, 4, 5, 6 (only Stage 2)
- Function calling for guaranteed structured output (99%+ JSON validity)

---

## 4. Technical Architecture

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NABU AI PLATFORM                          │
└─────────────────────────────────────────────────────────────┘

Data Flow (HYBRID APPROACH):

nabu_data/           Stage 1              Stage 2
(Multi-format)  ──>  FORMAT          ──>  LLM BATCH
207 files            NORMALIZER           EXTRACTOR
XML/JSON/HTML        - lxml (XML)         - Batch 50 records
Excel/CSV/TXT        - json (JSON)        - Extract persons,
                     - BeautifulSoup        companies, assets,
                     - pandas (CSV)         relationships
                     - regex (text)       - Normalize names
                     ↓                    - Classify entities
                     Clean JSON           - Infer relationships

                     Stage 3          Stage 4          Stage 5
              ──>   RESOLUTION  ──>  GRAPH      ──>   ANOMALY
                    Entity            Builder          DETECTION
                    deduplication     Relationship     Financial
                    Matching          graph            analysis
                    Merging

                     Stage 6
              ──>   REPORTING
                    Profile
                    aggregation
                    PDF generation
```

### 4.2 Technology Stack

**Core:**
- Python 3.13
- Pydantic 2.x for data validation
- OpenAI client for LapaLLM integration

**Data Parsing (Format Normalization):**
- lxml for XML/SOAP parsing (deterministic)
- orjson for fast JSON serialization (deterministic)
- beautifulsoup4 for HTML parsing (deterministic)
- openpyxl for Excel files (.xlsx) (deterministic)
- xlrd for legacy Excel files (.xls) (deterministic)
- pandas for CSV with automatic encoding detection (deterministic)
- chardet for encoding detection (UTF-8, Windows-1251, KOI8-U)
- regex for structured text extraction (deterministic)

**String Processing:**
- fuzzywuzzy + python-Levenshtein for fuzzy name matching
- python-dateutil for date parsing

**PDF Generation:**
- reportlab for PDF creation
- pillow for image handling

**Utilities:**
- loguru for logging
- click for CLI
- tqdm for progress bars

### 4.3 Project Structure

```
nabu_llm_service/
├── main.py                      # Existing entry point
├── requirements.txt             # Dependencies
├── .env                         # Environment config
├── README.md
│
├── nabu_data/                   # Raw data (existing)
│   ├── 890-ТМ-Д/
│   ├── 891-ТМ-Д/
│   └── 995-ІБ-Д/
│
├── src/                         # Source code (NEW)
│   ├── models/                  # Data models
│   │   └── entities.py          # Person, Company, Vehicle, etc.
│   │
│   ├── parsers/                 # Stage 1: Format Normalization (NO LLM)
│   │   ├── base_parser.py       # Base parser with format detection
│   │   ├── format_detector.py   # Auto-detect file format
│   │   ├── xml_parser.py        # XML/SOAP → dict
│   │   ├── json_parser.py       # JSON → dict
│   │   ├── html_parser.py       # HTML tables/forms → dict
│   │   ├── excel_parser.py      # XLS/XLSX → dict
│   │   ├── csv_parser.py        # CSV → dict
│   │   └── text_parser.py       # Plain text → dict (regex-based)
│   │
│   ├── extractors/              # Stage 2: LLM Batch Extraction
│   │   ├── llm_batch_processor.py    # Main LLM integration
│   │   ├── entity_extractor.py       # Extract all entity types
│   │   └── prompt_builder.py         # Build extraction prompts
│   │
│   ├── resolution/              # Stage 3: Deduplication
│   │   ├── person_matcher.py
│   │   ├── company_matcher.py
│   │   └── entity_merger.py
│   │
│   ├── graph/                   # Stage 4: Graph
│   │   ├── graph_builder.py
│   │   ├── graph_analyzer.py
│   │   └── path_finder.py
│   │
│   ├── analysis/                # Stage 5: Anomalies
│   │   ├── anomaly_detector.py
│   │   ├── income_analyzer.py
│   │   └── asset_valuator.py
│   │
│   ├── reporting/               # Stage 6: Reports
│   │   ├── profile_aggregator.py
│   │   ├── pdf_generator.py
│   │   └── templates/
│   │       └── person_profile.html
│   │
│   ├── utils/                   # Utilities
│   │   ├── file_io.py
│   │   ├── id_generator.py
│   │   ├── date_utils.py
│   │   └── logging_config.py
│   │
│   └── pipeline/                # Pipeline orchestration
│       ├── orchestrator.py
│       └── stage_runner.py
│
├── data/                        # Processed data (gitignored)
│   ├── normalized/              # Stage 1 output (format-normalized JSON)
│   ├── entities/                # Stage 2 output (LLM-extracted entities)
│   ├── resolved/                # Stage 3 output (deduplicated)
│   ├── graph/                   # Stage 4 output (relationship graph)
│   ├── anomalies/               # Stage 5 output (detected anomalies)
│   └── reports/                 # Stage 6 output (PDF reports)
│
├── tests/                       # Unit tests
│   ├── test_parsers.py
│   ├── test_extractors.py
│   └── test_anomaly_detection.py
│
└── scripts/                     # CLI scripts
    ├── run_pipeline.py          # Main pipeline runner
    ├── generate_report.py       # Generate single report
    └── stats.py                 # Show statistics
```

### 4.4 Data Models (Core Entities)

**Person:**
```python
class Person(BaseModel):
    person_id: str                              # UUID
    rnokpp: Optional[str]                       # Tax ID
    unzr: Optional[str]                         # Civil registry number
    birth_date: Optional[date]
    current_name: PersonName                    # Current official name
    all_names: List[PersonName]                 # Name history
    documents: List[IdentificationDocument]
    contacts: List[ContactInfo]
    addresses: List[Address]
    employment_history: List[Employment]
    additional_info: Dict[str, Any]
    data_sources: List[DataSource]
    created_at: datetime
    updated_at: datetime
```

**Company:**
```python
class Company(BaseModel):
    company_id: str
    edrpou: str                                 # Business registry code
    name: str
    state: str                                  # "зареєстровано", "припинено"
    founders: List[CompanyFounder]
    heads: List[CompanyHead]
    authorized_capital: Optional[float]
    registration_date: Optional[date]
    termination_date: Optional[date]
    activity_kinds: List[ActivityKind]
    address: Optional[str]
```

**Vehicle:**
```python
class Vehicle(BaseModel):
    vehicle_id: str
    vin: str
    registration_number: str
    brand: str
    model: str
    make_year: Optional[int]
    color: str
    fuel_type: Optional[str]
    current_owner: VehicleOwner
    operation_date: Optional[datetime]
    purchase_amount: Optional[float]
```

**RealEstate:**
```python
class RealEstate(BaseModel):
    property_id: str
    property_type: str                          # "квартира", "будинок", etc.
    registration_number: str
    full_address: str
    total_area: Optional[float]
    cadastral_number: Optional[str]
    owners: List[RealEstateOwner]
    ownership_type: str
    acquisition_document_type: Optional[str]
```

**Relationship:**
```python
class Relationship(BaseModel):
    relationship_id: str
    subject_id: str                             # Entity ID
    subject_type: str                           # "person", "company", etc.
    object_id: str
    object_type: str
    relationship_type: RelationshipType         # Enum
    start_date: Optional[date]
    end_date: Optional[date]
    properties: Dict[str, Any]
    source: DataSource
```

**AnomalyDetection:**
```python
class AnomalyDetection(BaseModel):
    anomaly_id: str
    anomaly_type: AnomalyType                   # Enum
    person_id: Optional[str]
    company_id: Optional[str]
    severity: str                               # "low", "medium", "high", "critical"
    confidence: float                           # 0.0 to 1.0
    description: str
    evidence: List[Dict[str, Any]]
    detected_at: datetime
```

### 4.5 Processing Pipeline

#### Stage 1: Format Normalization (NO LLM, Deterministic)
**Input:** `/nabu_data/**/*.{json,xml,html,xls,xlsx,csv,txt}`
**Output:** `/data/normalized/**/*.json`
**Processing Time:** ~5 minutes
**Cost:** $0 (no LLM usage)

**Goal:** Convert all file formats into clean, structured JSON without semantic understanding.

**Operations:**
1. Scan all case directories
2. Auto-detect file format by extension and content
3. Auto-detect encoding (UTF-8, Windows-1251, KOI8-U)
4. Route to format-specific parser
5. Extract raw structure (no semantic interpretation)
6. Preserve all fields and metadata
7. Save as clean JSON with source attribution

**Format-Specific Parsing (All Deterministic):**
- **XML/SOAP:** lxml → unwrap SOAP envelope → dict → JSON
- **JSON:** json.loads → validate → clean JSON
- **HTML:** BeautifulSoup → extract tables/forms → dict → JSON
- **Excel:** openpyxl/pandas → DataFrame → dict → JSON
- **CSV:** pandas (auto-encoding) → DataFrame → dict → JSON
- **Plain Text (structured):** Regex patterns → key-value pairs → JSON
- **Plain Text (unstructured):** Raw text → JSON wrapper

**Key Design Principle:**
- **NO semantic understanding** - just convert formats
- **NO registry-specific logic** - generic format handling
- **NO entity extraction** - preserve raw data
- Stage 2 (LLM) handles ALL semantic work

**Key Files:**
- `src/parsers/base_parser.py` - Base parser with format detection
- `src/parsers/format_detector.py` - Auto-detect file format
- `src/parsers/xml_parser.py` - Generic XML/SOAP unwrapping
- `src/parsers/json_parser.py` - Generic JSON validation
- `src/parsers/html_parser.py` - Generic HTML table/form extraction
- `src/parsers/excel_parser.py` - Generic Excel/CSV parsing
- `src/parsers/text_parser.py` - Generic text pattern extraction

#### Stage 2: LLM Batch Extraction with Function Calling (Semantic Understanding)
**Input:** `/data/normalized/` (clean JSON files)
**Output:** `/data/entities/{persons,companies,vehicles,real_estate,relationships}/`
**Processing Time:** ~10-15 minutes (API-limited)

**Goal:** Extract ALL entities and relationships from normalized data using LLM with function calling.

**Operations:**
1. Load 50 normalized JSON files at a time
2. Define structured function calling schema for entities
3. Send batch to LLM (model: "lapa-function-calling") with function call
4. LLM extracts with guaranteed structured output:
   - Persons (with all name variations, DOB, RNOKPP, УНЗР)
   - Companies (with EDRPOU, founders, heads, status)
   - Vehicles (with VIN, owner, registration)
   - Real estate (with cadastral number, owners, address)
   - Relationships (family, business, asset ownership)
5. LLM normalizes:
   - Name variations (Cyrillic/Latin)
   - Date formats (various → ISO 8601)
   - Address formats (structured)
6. LLM classifies:
   - Entity types
   - Relationship types
   - Document types
7. Assign unique IDs (UUID v4)
8. Save extracted entities with source attribution

**LLM Batching Strategy:**
```
Total files: 207
Batch size: 50 files/request
Total batches: ~5 batches
Model: lapa-function-calling (temperature=0)
```

**Function Calling Schema:**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "extract_entities",
        "description": "Extract entities from Ukrainian registry data",
        "parameters": {
            "type": "object",
            "properties": {
                "persons": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "full_name": {"type": "string"},
                            "rnokpp": {"type": "string"},
                            "birth_date": {"type": "string", "format": "date"}
                        }
                    }
                },
                "companies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "edrpou": {"type": "string"},
                            "status": {"type": "string"}
                        }
                    }
                },
                "relationships": {"type": "array", "items": {"type": "object"}}
            }
        }
    }
}]
```

**Key Advantages of Function Calling:**
- **99%+ JSON validity** (no parsing errors)
- **Deterministic output** (temperature=0)
- **Schema enforcement** (guaranteed structure)
- **Faster processing** (optimized for structured extraction)

**Key Files:**
- `src/extractors/llm_batch_processor.py` - Main LLM integration
- `src/extractors/entity_extractor.py` - Entity extraction orchestrator
- `src/extractors/prompt_builder.py` - Build extraction prompts

#### Stage 3: Entity Resolution (Deduplication)
**Input:** `/data/entities/`
**Output:** `/data/resolved/`
**Processing Time:** ~5 minutes

**Operations:**
1. Match duplicate persons using RNOKPP, DOB, name, address
2. Score match confidence
3. Merge entities above threshold (0.8)
4. Preserve all source data
5. Track merge provenance

**Matching Algorithm:**
```python
# Exact match (100% confidence)
if p1.rnokpp == p2.rnokpp and p1.rnokpp is not None:
    merge(p1, p2, confidence=1.0)

# High confidence (80-95%)
if p1.birth_date == p2.birth_date and fuzzy_name_match(p1, p2) > 0.85:
    merge(p1, p2, confidence=0.9)
```

**Key Files:**
- `src/resolution/person_matcher.py` - Person deduplication logic

#### Stage 4: Graph Construction
**Input:** `/data/resolved/`
**Output:** `/data/graph/{nodes,edges,indices}/`
**Processing Time:** ~5 minutes

**Operations:**
1. Create nodes for all entities
2. Create edges for all relationships
3. Build indices for fast lookup
4. Validate graph consistency

**Graph Storage:**
```
/data/graph/
  nodes/
    persons/{person_id}.json
    companies/{company_id}.json
    assets/{asset_id}.json
  edges/
    {relationship_id}.json
  indices/
    by_person/{person_id}.json       # → [related_node_ids]
    by_rnokpp/{rnokpp}.json          # → person_id
    by_edrpou/{edrpou}.json          # → company_id
```

**Key Files:**
- `src/graph/graph_builder.py` - Build adjacency lists

#### Stage 5: Anomaly Detection
**Input:** `/data/graph/`, `/data/resolved/`
**Output:** `/data/anomalies/`
**Processing Time:** ~5 minutes

**Operations:**
1. For each person:
   - Calculate total declared income
   - Calculate total asset value
   - Detect income/asset mismatch
2. For each company:
   - Check shell company indicators
   - Detect circular ownership
3. Generate anomaly reports

**Algorithms:**
- Income vs Asset Mismatch: `ratio = total_assets / total_income > 10`
- Shell Company Detection: offshore founder + short lifespan + high capital
- Circular Ownership: DFS cycle detection in ownership graph

**Key Files:**
- `src/analysis/anomaly_detector.py` - Main detection engine
- `src/analysis/income_analyzer.py` - Income/asset analysis
- `src/analysis/asset_valuator.py` - Asset valuation

#### Stage 6: Report Generation
**Input:** `/data/graph/`, `/data/anomalies/`
**Output:** `/data/reports/{person_id}.pdf`
**Processing Time:** ~5 seconds per report

**Operations:**
1. Aggregate person profile from graph
2. Collect all related entities
3. Format data for template
4. Render HTML template
5. Convert to PDF

**Key Files:**
- `src/reporting/profile_aggregator.py` - Aggregate profile data
- `src/reporting/pdf_generator.py` - Generate PDF

### 4.6 CLI Interface

```bash
# Run full pipeline
python scripts/run_pipeline.py run

# Run specific stage
python scripts/run_pipeline.py run --stage 1  # Normalize formats (NO LLM)
python scripts/run_pipeline.py run --stage 2  # LLM batch extraction
python scripts/run_pipeline.py run --stage 3  # Entity resolution
python scripts/run_pipeline.py run --stage 4  # Build graph
python scripts/run_pipeline.py run --stage 5  # Detect anomalies
python scripts/run_pipeline.py run --stage 6  # Generate reports

# Resume from checkpoint
python scripts/run_pipeline.py run --resume

# Generate single report
python scripts/run_pipeline.py report <person_id> --output report.pdf

# Show statistics
python scripts/run_pipeline.py stats
```

---

## 5. Implementation Roadmap (4 Days)

### Day 1: Format Normalization (6 hours)
**Goal:** Convert all 207 files to clean JSON (NO LLM needed)

**Morning (3 hours):**
- [ ] Set up project structure
- [ ] Define core data models (`src/models/entities.py`)
- [ ] Implement format detector (`src/parsers/format_detector.py`)
- [ ] Implement base parser (`src/parsers/base_parser.py`)

**Afternoon (3 hours):**
- [ ] Implement XML/SOAP parser (`src/parsers/xml_parser.py`)
  - Unwrap SOAP envelopes, handle namespaces, extract body
- [ ] Implement JSON parser (`src/parsers/json_parser.py`)
  - Validate and clean JSON
- [ ] Implement HTML parser (`src/parsers/html_parser.py`)
  - Extract tables and forms with BeautifulSoup
- [ ] Implement Excel/CSV parser (`src/parsers/excel_parser.py`)
  - Parse with pandas, handle encoding
- [ ] Implement text parser (`src/parsers/text_parser.py`)
  - Regex-based pattern extraction

**Testing & Validation (2 hours):**
- [ ] Test each parser on sample files
- [ ] Run Stage 1 on full 207 files
- [ ] Validate all files converted to JSON

**Deliverable:** `/data/normalized/` with 207 clean JSON files

**Key Insight:** NO registry-specific logic needed! Generic format handling only.

---

### Day 2: LLM Batch Extraction (8 hours)
**Goal:** Extract ALL entities using LLM batching

**Morning (4 hours):**
- [ ] Implement LLM batch processor (`src/extractors/llm_batch_processor.py`)
  - OpenAI client with LapaLLM endpoint
  - Batch 50 files per request
  - Handle rate limits and retries
- [ ] Design extraction prompt (`src/extractors/prompt_builder.py`)
  - Extract persons, companies, vehicles, real estate, relationships
  - Normalize names, dates, addresses
  - Classify entity and relationship types
- [ ] Test with 1 batch (50 files)

**Afternoon (3 hours):**
- [ ] Implement entity extractor (`src/extractors/entity_extractor.py`)
  - Parse LLM JSON output
  - Validate extracted entities
  - Assign UUIDs
  - Save to `/data/entities/`
- [ ] Run Stage 2 on full dataset (5 batches × 3 min = 15 min)

**Testing & Validation (1 hour):**
- [ ] Validate extracted entities
- [ ] Check entity counts (persons, companies, vehicles, etc.)
- [ ] Review LLM output quality
- [ ] Adjust prompt if needed

**Deliverable:** `/data/entities/` with extracted entities from all 207 files

**Cost:** ~$15-20 for full run

---

### Day 3: Deduplication, Graph & Anomaly Detection (8 hours)
**Goal:** Deduplicate entities, build graph, detect anomalies

**Morning (3 hours):**
- [ ] Implement person matcher (`src/resolution/person_matcher.py`)
  - RNOKPP exact match
  - DOB + name fuzzy match
  - Confidence scoring
- [ ] Implement company matcher (`src/resolution/company_matcher.py`)
- [ ] Implement entity merger (`src/resolution/entity_merger.py`)
- [ ] Run Stage 3 (entity resolution) on full dataset

**Afternoon (3 hours):**
- [ ] Implement graph builder (`src/graph/graph_builder.py`)
  - Create nodes (persons, companies, assets)
  - Create edges (relationships)
  - Build indices (by person_id, rnokpp, edrpou)
- [ ] Implement graph analyzer (`src/graph/graph_analyzer.py`)
- [ ] Run Stage 4 (graph construction) on full dataset
- [ ] Validate graph structure

**Evening (2 hours):**
- [ ] Implement anomaly detector (`src/analysis/anomaly_detector.py`)
  - Income vs asset mismatch
  - Shell company indicators
  - Circular ownership detection
- [ ] Implement income analyzer (`src/analysis/income_analyzer.py`)
- [ ] Implement asset valuator (`src/analysis/asset_valuator.py`)
- [ ] Run Stage 5 (anomaly detection) on full dataset

**Deliverable:** `/data/resolved/`, `/data/graph/`, and `/data/anomalies/` with complete knowledge graph and detected anomalies

---

### Day 4: Reporting & Polish (8 hours)
**Goal:** Generate PDF reports and finalize system

**Morning (4 hours):**
- [ ] Implement profile aggregator (`src/reporting/profile_aggregator.py`)
- [ ] Implement PDF generator (`src/reporting/pdf_generator.py`)
- [ ] Create HTML template (`src/reporting/templates/person_profile.html`)
- [ ] Test PDF generation on sample person

**Afternoon (3 hours):**
- [ ] Run Stage 6 (report generation) on all persons
- [ ] Validate PDF output matches sample format
- [ ] Fix formatting issues
- [ ] Add missing sections (assets, anomalies)

**Evening (1 hour):**
- [ ] Implement pipeline orchestrator (`src/pipeline/orchestrator.py`)
- [ ] Implement CLI (`scripts/run_pipeline.py`)
- [ ] Write README with usage instructions
- [ ] Final end-to-end test

**Deliverable:** `/data/reports/` with PDF reports for all persons, complete CLI tool, documentation

---

## 6. Risk Management

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex XML parsing fails | Medium | High | Build robust error handling, skip malformed files, log errors |
| LLM API rate limits | High | Medium | Aggressive batching (50+ items), implement retry logic, cache responses |
| Entity deduplication low accuracy | Medium | High | Multiple matching signals (RNOKPP + DOB + name + address), confidence scoring |
| PDF generation formatting issues | Medium | Medium | Use proven library (ReportLab), start with HTML template, iterate on styling |
| Performance issues with 200+ files | Low | Medium | Parallel processing (multiprocessing), streaming parsers, optimize file I/O |

### 6.2 Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Underestimated parser complexity | Medium | High | Prioritize top 5 registries (EDR, EIS, DRRP, DRFO, DRACS), stub others |
| LLM enrichment takes too long | Medium | Medium | Make LLM optional, can skip if time-constrained |
| PDF formatting takes too long | Low | Low | Generate simple text reports as fallback |

### 6.3 Data Quality Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Missing RNOKPP in many records | High | Medium | Fallback to DOB + name matching, accept lower confidence |
| Inconsistent date formats | Medium | Low | Use python-dateutil for flexible parsing |
| Incomplete address data | Medium | Low | Store partial addresses, normalize what's available |

---

## 7. Success Metrics

### 7.1 Technical Metrics
- **Parsing success rate:** >95% of files parsed without errors
- **Entity extraction recall:** >90% of persons/companies/assets extracted
- **Deduplication accuracy:** >90% of duplicate persons correctly merged
- **Processing time:** Complete pipeline in <30 minutes
- **PDF generation success:** 100% of persons get valid PDF

### 7.2 Business Metrics
- **Anomalies detected:** At least 5 different anomaly types identified
- **Relationship coverage:** >80% of persons have at least 1 relationship
- **Data completeness:** >70% of person profiles have employment history
- **Report quality:** PDF reports match sample format in structure and content

---

## 8. Future Enhancements (Post-MVP)

### 8.1 Database Migration
**Priority:** High
**Timeline:** 1-2 weeks post-MVP

**Options:**
1. **PostgreSQL with JSONB** - Recommended for general use
   - Structured + unstructured data
   - Proven reliability
   - Easy migration from JSON files

2. **Neo4j** - For graph-heavy analysis
   - Native graph queries (Cypher)
   - Complex relationship traversal
   - Better for network analysis

3. **Hybrid (PostgreSQL + Neo4j)** - Best of both worlds
   - PostgreSQL for primary data storage
   - Neo4j for graph queries

**Migration Path:**
```bash
# 1. Install database
# 2. Run migration script
python scripts/migrate_to_database.py --db postgres

# 3. Update storage layer
# Replace FileStorage with PostgreSQLStorage in code

# 4. Verify migration
python scripts/verify_migration.py
```

### 8.2 Web Interface
**Priority:** Medium
**Timeline:** 2-3 weeks

**Features:**
- Search persons by name, RNOKPP
- Interactive relationship graph visualization
- Filter by anomaly type
- Export reports in multiple formats (PDF, Excel, JSON)
- Comparison view for multiple persons

**Stack:**
- Backend: FastAPI
- Frontend: React + D3.js for graph visualization
- Database: PostgreSQL + Neo4j

### 8.3 Real-time Processing
**Priority:** Low
**Timeline:** 1-2 months

**Features:**
- Watch `/nabu_data/` for new files
- Automatically process new cases
- Incremental updates to existing profiles
- Notifications for new anomalies

### 8.4 Advanced Analytics
**Priority:** Low
**Timeline:** 2-3 months

**Features:**
- Machine learning for anomaly scoring
- Predictive risk modeling
- Temporal analysis (wealth trajectory over time)
- Geographic analysis (property concentration maps)
- Network centrality metrics (key persons in networks)

---

## 9. Testing Strategy

### 9.1 Unit Tests
**Files:** `/tests/test_*.py`

**Coverage:**
- Parsers: Test each registry parser with sample data
- Extractors: Test entity extraction logic
- Matchers: Test person/company matching algorithms
- Anomaly Detectors: Test detection logic with synthetic data
- PDF Generator: Test template rendering

**Run:**
```bash
pytest tests/ -v --cov=src
```

### 9.2 Integration Tests
**Scenarios:**
1. End-to-end pipeline on sample dataset (10 files)
2. Stage-by-stage validation of output
3. PDF generation for known person

### 9.3 Manual Testing
**Checklist:**
- [ ] Parse all 207 files without crashes
- [ ] Verify person deduplication (check known duplicates)
- [ ] Inspect generated PDFs for formatting
- [ ] Validate anomaly detections (spot check 5 cases)
- [ ] Test CLI commands

---

## 10. Documentation Requirements

### 10.1 README.md
**Sections:**
1. Project overview
2. Installation instructions
3. Usage examples
4. Pipeline stages explanation
5. Troubleshooting

### 10.2 Code Documentation
- Docstrings for all classes and functions
- Type hints throughout
- Inline comments for complex logic

### 10.3 Data Documentation
- Field descriptions for all models
- Registry type mapping
- Anomaly type definitions

---

## 11. Critical Files Priority (HYBRID APPROACH)

These files must be implemented first for the system to work:

### Tier 1 (Critical - Day 1, Stage 1):
1. **src/models/entities.py** - All data models
2. **src/parsers/format_detector.py** - Auto-detect file format
3. **src/parsers/base_parser.py** - Base parser with format routing
4. **src/parsers/xml_parser.py** - Generic XML/SOAP unwrapping (handles most files)
5. **src/parsers/json_parser.py** - Generic JSON validation
6. **src/parsers/html_parser.py** - Generic HTML table/form extraction
7. **src/parsers/excel_parser.py** - Generic Excel/CSV parsing
8. **src/parsers/text_parser.py** - Generic text pattern extraction

**Key Insight:** NO registry-specific parsers needed! Just 8 files for all formats.

### Tier 2 (High Priority - Day 2, Stage 2):
9. **src/extractors/llm_batch_processor.py** - Core LLM integration (MOST CRITICAL)
10. **src/extractors/prompt_builder.py** - Build extraction prompts
11. **src/extractors/entity_extractor.py** - Parse LLM output, validate, save

**Key Insight:** LLM does ALL semantic work (extraction, normalization, classification)

### Tier 3 (Medium Priority - Day 3, Stages 3-5):
12. **src/resolution/person_matcher.py** - Person deduplication
13. **src/resolution/entity_merger.py** - Entity merging
14. **src/graph/graph_builder.py** - Graph construction
15. **src/analysis/anomaly_detector.py** - Anomaly detection

### Tier 4 (Delivery - Day 4, Stage 6):
16. **src/reporting/profile_aggregator.py** - Aggregate person profile
17. **src/reporting/pdf_generator.py** - PDF generation
18. **src/pipeline/orchestrator.py** - Pipeline orchestration

**Total Critical Files: 18** (down from 27+ in custom parser approach)

---

## 12. Dependencies Installation

```bash
# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip

# Core
pip install openai httpx pydantic python-dotenv tqdm

# Data parsing (format normalization)
pip install lxml beautifulsoup4

# Excel and CSV
pip install openpyxl xlrd pandas

# Encoding detection
pip install chardet

# NOTE: NO spaCy needed for hybrid approach!
# LLM handles all NLP tasks (entity extraction, normalization)

# Data processing
pip install python-dateutil

# Fuzzy matching
pip install fuzzywuzzy python-Levenshtein

# PDF generation
pip install reportlab pillow

# File storage
pip install orjson

# Utilities
pip install loguru click

# Testing
pip install pytest pytest-cov

# Save requirements
pip freeze > requirements.txt
```

---

## 13. Environment Configuration

```bash
# .env file
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=http://146.59.127.106:4000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pipeline.log

# Processing
MAX_WORKERS=4
BATCH_SIZE=50
LLM_MAX_TOKENS=4000
LLM_TEMPERATURE=0.3

# Paths
DATA_DIR=data
REPORTS_DIR=data/reports
```

---

## 14. Verification Checklist

After completing implementation, verify:

- [ ] All 207 case files parsed successfully
- [ ] At least 50 unique person profiles created
- [ ] At least 100 relationships extracted
- [ ] At least 10 financial anomalies detected
- [ ] All persons have PDF reports generated
- [ ] PDF reports match sample format structure
- [ ] CLI commands work as documented
- [ ] Pipeline can run end-to-end without errors
- [ ] Processing completes in <30 minutes
- [ ] All critical files implemented and tested

---

## 15. Appendix

### A. Registry Type Codes
```
REQ_EDR_*        - Business registry by code/name
REQ_EIS_TZ_*     - Vehicle information
REQ_DRRP         - Real estate registry (code: 011)
REQ_DRFO_INCOME  - Tax/income information (code: 062)
REQ_DRACS_*      - Civil status acts (marriage, divorce, birth, death, name change)
REQ_DZK_*        - Land cadastre (code: 225)
REQ_ARC_*        - Border crossings, archives
REQ_DSR_*        - Inheritance information
REQ_ERD_*        - Power of attorney
```

### B. Key Registry Fields Mapping
```
Person Fields:
  RNOKPP / CODE / sbjCode         → person.rnokpp
  LNAME / last_name               → person.current_name.last_name
  FNAME / first_name              → person.current_name.first_name
  PNAME / middle_name             → person.current_name.middle_name
  BIRTHDAY / date_birth           → person.birth_date

Address Fields:
  addressDetail / ADDRESS_NAME    → address.full_address
  regionName / regionId           → address.region
  cityName / cityId               → address.city

Vehicle Fields:
  VIN                             → vehicle.vin
  BRAND_NAME / MODEL_NAME         → vehicle.brand / vehicle.model
  N_REG                           → vehicle.registration_number
  MAKE_YEAR                       → vehicle.make_year

Real Estate Fields:
  regNum                          → real_estate.registration_number
  totalArea                       → real_estate.total_area
  cadNum                          → real_estate.cadastral_number
```

### C. Data Source Codes
```
ДМС    - State Migration Service (documents, addresses)
НАЗК   - National Anti-Corruption Agency (declarations)
ДРАЦС  - Civil Status Acts Registry (birth, marriage, divorce)
ЄДР    - Unified State Registry (companies)
ДРРП   - Real Estate Registry (property ownership)
ЄІС    - Unified Information System (vehicles)
ДРФО   - State Tax Service (income)
ДЗК    - Land Cadastre (land parcels)
```

---

## 16. Hybrid Approach Summary

### **Why Hybrid Beats Custom Parsers**

| Aspect | Custom Parsers | Hybrid + Function Calling | Improvement |
|--------|----------------|---------------------------|-------------|
| **Development Time** | ~16 hours | ~8 hours | **50% faster** |
| **Files to Implement** | 27+ parsers | 11 core files | **60% less code** |
| **Handles Schema Changes** | ❌ Breaks | ✅ Flexible | **Resilient** |
| **JSON Validity** | N/A | 99%+ (function calling) | **Guaranteed structure** |
| **Processing Time** | ~10 min | ~15 min | Slightly slower but acceptable |
| **Maintainability** | ❌ High | ✅ Low | **Less tech debt** |
| **Risk of Missing Deadline** | 🔴 High | 🟢 Low | **Can finish in 3 days** |

### **Key Design Decisions**

1. **Stage 1 (NO LLM):** Simple format conversion only
   - XML → JSON, HTML → JSON, Excel → JSON
   - NO semantic understanding needed
   - Fast, deterministic

2. **Stage 2 (YES LLM with Function Calling):** All semantic work
   - Model: "lapa-function-calling" (temperature=0)
   - Entity extraction (persons, companies, vehicles, real estate)
   - Normalization (names, dates, addresses)
   - Classification (entity types, relationship types)
   - Batching (50 files/request) for efficiency
   - **Function calling guarantees valid JSON output (99%+)**

3. **Stages 3-6 (NO LLM):** Deterministic logic
   - Deduplication, graph building, anomaly detection, PDF generation
   - All rule-based, no AI needed

### **Success Factors**

✅ **Pragmatic:** 80% quality with 40% effort
✅ **Achievable:** Can finish in 3 days
✅ **Reliable:** Function calling ensures 99%+ JSON validity
✅ **Flexible:** LLM handles edge cases automatically
✅ **Maintainable:** Less code, less complexity
✅ **Deterministic:** Temperature=0 for consistent results

---

**END OF PRD**

**Document Version:** 3.0 (HYBRID APPROACH + FUNCTION CALLING)
**Last Updated:** 2026-01-13
**Status:** Ready for Implementation
**Estimated Effort:** 24 hours (3 days × 8 hours)
**Risk Level:** Low (simplified architecture, proven approach, guaranteed structured output)
**Approach:** Hybrid (format normalization + LLM function calling batch extraction)

---

This PRD provides a complete specification for implementing the NABU Registry AI Platform using a **HYBRID APPROACH WITH FUNCTION CALLING** that combines deterministic format parsing with LLM-powered semantic extraction using the "lapa-function-calling" model for guaranteed structured output. Focus on the Day 1-3 roadmap and prioritize Tier 1-2 critical files first. The hybrid approach reduces implementation time by 50% while ensuring 99%+ JSON validity through function calling.
