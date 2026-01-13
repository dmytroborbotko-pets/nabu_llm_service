# NABU AI Platform - Implementation Task List (HYBRID + FUNCTION CALLING)
## 3-Day Development Sprint with Story Points

**Project:** nabu_llm_service
**Sprint Duration:** 3 days (24 hours)
**Total Story Points:** 95 SP
**Story Point Scale:** Fibonacci (1, 2, 3, 5, 8, 13, 21)
**Approach:** Hybrid (Format Normalization + LLM Function Calling Batch Extraction)
**Model:** lapa-function-calling (temperature=0)

---

## Story Point Reference Guide

- **1 SP** = 0.5-1 hour (trivial task, clear implementation)
- **2 SP** = 1-2 hours (simple task, minimal complexity)
- **3 SP** = 2-3 hours (moderate task, some complexity)
- **5 SP** = 3-5 hours (complex task, requires research)
- **8 SP** = 5-8 hours (very complex, multiple components)
- **13 SP** = 8+ hours (epic task, should be split if possible)

---

# DAY 1: Format Normalization (26 SP)
**Goal:** Convert all 207 files to clean JSON (NO LLM)
**Duration:** 6 hours

---

## Morning Session (4 hours) - 18 SP

### TASK-1.1: Project Structure Setup
**Story Points:** 2 SP
**Priority:** CRITICAL
**Dependencies:** None
**Assigned To:** Developer

**Description:**
Set up complete project directory structure, initialize git, configure Python environment.

**Acceptance Criteria:**
- [ ] Directory structure matches PRD Section 4.3
- [ ] Virtual environment created with Python 3.13
- [ ] Git repository initialized with .gitignore
- [ ] `src/`, `data/`, `tests/`, `scripts/` directories created
- [ ] Empty `__init__.py` files in all Python packages
- [ ] `.env.example` file created
- [ ] `data/` directory added to .gitignore

**Implementation Checklist:**
```bash
mkdir -p src/{models,parsers/registry_parsers,extractors,enrichment,resolution,graph,analysis,reporting/templates,utils,pipeline}
mkdir -p data/{normalized,entities,enriched,resolved,graph,anomalies,reports}
mkdir -p tests scripts logs
touch src/__init__.py src/models/__init__.py src/parsers/__init__.py
# ... create all __init__.py files
```

---

### TASK-1.2: Core Data Models Implementation
**Story Points:** 8 SP
**Priority:** CRITICAL
**Dependencies:** TASK-1.1
**Assigned To:** Developer

**Description:**
Implement all Pydantic data models for entities (Person, Company, Vehicle, RealEstate, Relationship, Anomaly) as defined in PRD Section 4.4.

**Acceptance Criteria:**
- [ ] `DataSource` enum with all registry types (ДМС, НАЗК, ДРАЦС, etc.)
- [ ] `PersonName` model with Ukrainian and Latin fields
- [ ] `IdentificationDocument` model with all document types
- [ ] `ContactInfo`, `Address`, `Employment` models
- [ ] `Person` model with all fields and nested models
- [ ] `Company` model with founders, heads, activity kinds
- [ ] `Vehicle` model with owner and technical specs
- [ ] `RealEstate` model with owners and property details
- [ ] `FinancialRecord` model for income/tax data
- [ ] `RelationshipType` enum with all relationship types
- [ ] `Relationship` model with temporal validity
- [ ] `AnomalyType` enum with 6 anomaly types
- [ ] `AnomalyDetection` model with evidence tracking
- [ ] All models have proper type hints and docstrings
- [ ] Models validate correctly with sample data

**File:** `src/models/entities.py`

**Implementation Notes:**
- Use `Optional` for nullable fields
- Use `List` for collections
- Use `datetime` and `date` from Python standard library
- Add `Field(...)` with descriptions for key fields
- Use `model_dump_json()` for serialization

**Test Data:**
```python
# Test that Person model works
person = Person(
    person_id="test-123",
    rnokpp="3347367890",
    birth_date=date(1991, 8, 24),
    current_name=PersonName(
        last_name="Дія",
        first_name="Надія",
        middle_name="Володимирівна"
    ),
    all_names=[],
    documents=[],
    contacts=[],
    addresses=[],
    employment_history=[],
    data_sources=[DataSource.DMS]
)
assert person.person_id == "test-123"
```

---

### TASK-1.3: Format Detector Implementation
**Story Points:** 3 SP
**Priority:** CRITICAL
**Dependencies:** TASK-1.2
**Assigned To:** Developer

**Description:**
Implement format detector that auto-detects file format and routes to appropriate parser (HYBRID APPROACH: NO registry-specific logic).

**Acceptance Criteria:**
- [ ] `detect_format(file_path)` detects JSON, XML, HTML, Excel, CSV, TXT by extension and content
- [ ] `detect_encoding(file_path)` detects UTF-8, Windows-1251, KOI8-U using chardet
- [ ] `extract_metadata(file_path)` extracts case number, registry code from filename
- [ ] Returns format enum for routing
- [ ] Error handling for unknown formats
- [ ] Logging with loguru

**File:** `src/parsers/format_detector.py`

**Key Design Principle:** NO semantic understanding, just format detection!

---

### TASK-1.4: Base Parser Implementation
**Story Points:** 2 SP
**Priority:** CRITICAL
**Dependencies:** TASK-1.3
**Assigned To:** Developer

**Description:**
Implement abstract base parser class that all format-specific parsers inherit from.

**Acceptance Criteria:**
- [ ] `BaseParser` abstract class
- [ ] `parse()` abstract method
- [ ] `save_normalized()` method to save JSON output
- [ ] Error handling and logging
- [ ] Metadata tracking (source file, format, timestamp)

**File:** `src/parsers/base_parser.py`

---

### TASK-1.5: JSON Parser Implementation (Generic)
**Story Points:** 2 SP
**Priority:** HIGH
**Dependencies:** TASK-1.3
**Assigned To:** Developer

**Description:**
Implement GENERIC JSON parser (NO registry-specific logic, just validate and clean JSON).

**Acceptance Criteria:**
- [ ] Inherits from `BaseParser`
- [ ] Handles various JSON structures (flat, nested, arrays)
- [ ] Validates JSON syntax
- [ ] Handles malformed JSON gracefully
- [ ] **NO semantic interpretation** - preserves all fields as-is
- [ ] Returns normalized dict structure with metadata
- [ ] Logs parsing errors
- [ ] Tested with sample NABU JSON files

**File:** `src/parsers/json_parser.py`

**Key Design:** Just json.loads() + validation, NO domain logic!

---

### TASK-1.6: HTML Parser Implementation (Generic)
**Story Points:** 3 SP
**Priority:** HIGH
**Dependencies:** TASK-1.3
**Assigned To:** Developer

**Description:**
Implement GENERIC HTML parser using BeautifulSoup (NO semantic interpretation, just extract structure).

**Acceptance Criteria:**
- [ ] Inherits from `BaseParser`
- [ ] Extracts all HTML tables to list of lists
- [ ] Extracts all form fields to dict
- [ ] Handles nested tables
- [ ] **NO semantic interpretation** - just structure extraction
- [ ] Returns normalized dict structure
- [ ] Handles encoding issues
- [ ] Tested with sample HTML files (if any)

**File:** `src/parsers/html_parser.py`

**Key Design:** BeautifulSoup extraction only, NO domain logic!

---

### TASK-1.7: XML/SOAP Parser Implementation (Generic)
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-1.4
**Assigned To:** Developer

**Description:**
Implement GENERIC XML/SOAP parser using lxml (NO registry-specific logic, just unwrap SOAP envelopes and convert to dict).

**Acceptance Criteria:**
- [ ] Inherits from `BaseParser`
- [ ] Unwraps SOAP envelopes (removes envelope, keeps body)
- [ ] Handles XML namespaces
- [ ] Converts XML to normalized dict using lxml
- [ ] **NO semantic interpretation** - preserves all XML structure
- [ ] Handles malformed XML gracefully
- [ ] Tested with sample NABU XML files (DRFO, DRACS, etc.)

**File:** `src/parsers/xml_parser.py`

**Key Design:** Generic SOAP unwrapping + XML→dict conversion only!

---

### TASK-1.8: Excel/CSV Parser Implementation (Generic)
**Story Points:** 3 SP
**Priority:** MEDIUM
**Dependencies:** TASK-1.3
**Assigned To:** Developer

**Description:**
Implement GENERIC Excel/CSV parser using pandas (NO semantic interpretation, just tabular data extraction).

**Acceptance Criteria:**
- [ ] Inherits from `BaseParser`
- [ ] **Excel:** Supports .xlsx (openpyxl) and .xls (xlrd)
- [ ] **Excel:** Extracts all sheets to separate tables
- [ ] **CSV:** Auto-detects encoding (chardet)
- [ ] **CSV:** Auto-detects delimiter (comma, semicolon, tab)
- [ ] **NO semantic interpretation** - just DataFrame → dict conversion
- [ ] Returns list of dicts (rows) with metadata
- [ ] Handles Ukrainian text correctly
- [ ] Tested with sample files

**File:** `src/parsers/excel_parser.py`

**Key Design:** pandas to_dict() only, NO domain logic!

---

### TASK-1.9: Text Parser Implementation (Generic)
**Story Points:** 3 SP
**Priority:** LOW
**Dependencies:** TASK-1.3
**Assigned To:** Developer

**Description:**
Implement GENERIC text parser using regex (NO semantic interpretation, just pattern extraction for structured text).

**Acceptance Criteria:**
- [ ] Inherits from `BaseParser`
- [ ] Regex patterns for key-value pairs (e.g., "ПІБ: value")
- [ ] Handles encoding correctly
- [ ] **NO semantic interpretation** - just pattern matching
- [ ] Returns dict of extracted patterns
- [ ] Falls back to raw text if no patterns found

**File:** `src/parsers/text_parser.py`

**Key Design:** Regex extraction only for structured text, wrap raw text if unstructured!

---

## Testing & Validation (2 hours) - 8 SP

### TASK-1.10: Parser Testing & Stage 1 Execution
**Story Points:** 5 SP
**Priority:** HIGH
**Dependencies:** All Day 1 parser tasks
**Assigned To:** Developer

**Description:**
Test all format parsers with real NABU data, validate normalized JSON output, and run Stage 1 on full dataset.

**Acceptance Criteria:**
- [ ] Unit tests for each format parser
- [ ] Integration test for format detection and routing
- [ ] All 207 files attempted to parse
- [ ] **Parsing success rate >95%**
- [ ] All errors logged to logs/parsing_errors.log
- [ ] **Normalized JSON saved to `data/normalized/`**
- [ ] Parsing statistics generated
- [ ] **Verify NO semantic interpretation** - just format conversion

**Test Script:** `tests/test_parsers.py`

**Run Stage 1:**
```bash
python scripts/run_pipeline.py run --stage 1
```

**Expected Output:**
```
Stage 1: Format Normalization (NO LLM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 207/207 files
✓ Parsed: 197 files (95.2%)
✗ Failed: 10 files (4.8%)
⏱ Time: 4m 32s
📁 Output: data/normalized/
```

**Key Verification:** All files should be clean JSON, NO entity extraction yet!

---

# DAY 2: LLM Batch Extraction (35 SP)
**Goal:** Extract ALL entities using LLM batching (HYBRID APPROACH)
**Duration:** 8 hours

---

## Morning Session (4 hours) - 20 SP

### TASK-2.1: Prompt Builder Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-1.10
**Assigned To:** Developer

**Description:**
Implement prompt builder that creates extraction prompts for LLM batch processing (HYBRID APPROACH).

**Acceptance Criteria:**
- [ ] Builds prompts for entity extraction from 50 normalized JSON files
- [ ] Prompt includes clear instructions in Ukrainian
- [ ] Prompt specifies output format (structured JSON)
- [ ] Prompt covers ALL entity types:
  - Persons (with name variations, RNOKPP, УНЗР, birth date)
  - Companies (with EDRPOU, founders, heads, status)
  - Vehicles (with VIN, owner, registration)
  - Real estate (with cadastral number, owners, address)
  - Relationships (family, business, asset ownership)
- [ ] Prompt includes normalization instructions:
  - Names (Cyrillic/Latin)
  - Dates (various → ISO 8601)
  - Addresses (structured format)
- [ ] Tested with sample batches

**File:** `src/extractors/prompt_builder.py`

**Sample Prompt Structure:**
```
You are a data extraction specialist for Ukrainian government registries.

INPUT: 50 JSON files containing registry responses (DRFO, EDR, EIS, DRRP, DRACS, etc.)

TASK: Extract ALL entities and relationships:

1. PERSONS: Extract full name (Ukrainian + Latin), birth date, RNOKPP, УНЗР, all name variations
2. COMPANIES: Extract EDRPOU, name, founders, heads, registration dates, status
3. VEHICLES: Extract VIN, brand, model, owner, registration number
4. REAL ESTATE: Extract cadastral number, address, area, owners
5. RELATIONSHIPS: Identify family (spouse, parent, child), business (founder, head), asset ownership

NORMALIZATION:
- Dates: Convert to YYYY-MM-DD format
- Names: Provide both Cyrillic and Latin transliterations if possible
- Addresses: Structure as {region, city, street, building, apartment}

OUTPUT: Structured JSON with entities array
```

---

### TASK-2.2: LLM Batch Processor with Function Calling
**Story Points:** 8 SP
**Priority:** CRITICAL
**Dependencies:** TASK-2.1
**Assigned To:** Developer

**Description:**
Implement LLM batch processor using "lapa-function-calling" model with OpenAI function calling API for guaranteed structured output (HYBRID APPROACH - does ALL semantic extraction).

**Acceptance Criteria:**
- [ ] OpenAI client configured for LapaLLM endpoint
- [ ] **Model: "lapa-function-calling" with temperature=0**
- [ ] **Batch size: 50 normalized JSON files per request**
- [ ] Define function calling schema (tools) for entity extraction
- [ ] `extract_entities_batch()` method using function calling
- [ ] **99%+ JSON validity** (guaranteed by function calling)
- [ ] Response caching to disk (avoid re-processing)
- [ ] Retry logic with exponential backoff
- [ ] Rate limiting support
- [ ] Progress bar with tqdm
- [ ] Minimal error handling (function calling rarely fails)
- [ ] Tested with 1 batch (50 files)

**File:** `src/extractors/llm_batch_processor.py`

**Key Design:** Function calling guarantees structured output, temperature=0 for deterministic results!

---

## Afternoon Session (4 hours) - 15 SP

### TASK-2.3: Entity Extractor Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-2.2
**Assigned To:** Developer

**Description:**
Implement entity extractor that parses LLM JSON output, validates entities, and saves them (HYBRID APPROACH).

**Acceptance Criteria:**
- [ ] Parses LLM JSON response
- [ ] Validates entities against Pydantic models
- [ ] Assigns UUIDs to all entities
- [ ] Saves entities to `data/entities/{persons,companies,vehicles,real_estate,relationships}/`
- [ ] Creates indices (by person_id, rnokpp, edrpou)
- [ ] Handles malformed LLM output gracefully
- [ ] Logs extraction statistics
- [ ] Tested with sample LLM output

**File:** `src/extractors/entity_extractor.py`

**Key Design:** Parse LLM JSON → validate → save, NO additional logic!

---

### TASK-2.4: Run Stage 2 with Function Calling on Full Dataset
**Story Points:** 10 SP
**Priority:** CRITICAL
**Dependencies:** TASK-2.3
**Assigned To:** Developer

**Description:**
Execute Stage 2 (LLM function calling batch extraction) on full NABU dataset - THE KEY HYBRID STAGE!

**Acceptance Criteria:**
- [ ] Load all 207 normalized JSON files
- [ ] Create ~5 batches (50 files each)
- [ ] Send each batch to "lapa-function-calling" model with function schema
- [ ] **LLM extracts ALL entities + relationships + normalizations**
- [ ] **99%+ JSON validity** (function calling guarantees structure)
- [ ] Save extracted entities
- [ ] **Total LLM calls: ~5 batched requests**
- [ ] **At least 200 person entities extracted**
- [ ] At least 100 company entities extracted
- [ ] At least 50 vehicle entities extracted
- [ ] At least 500 relationships extracted
- [ ] Processing time: <20 minutes
- [ ] Quality report generated

**Commands:**
```bash
python scripts/run_pipeline.py run --stage 2
python scripts/generate_stats.py --stage 2
```

**Expected Output:**
```
Stage 2: LLM Function Calling Batch Extraction (HYBRID)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
Batch 1/5: Processing 50 files... ✓ (2m 45s)
Batch 2/5: Processing 50 files... ✓ (2m 38s)
Batch 3/5: Processing 50 files... ✓ (2m 52s)
Batch 4/5: Processing 50 files... ✓ (2m 41s)
Batch 5/5: Processing 7 files... ✓ (0m 35s)

✓ Persons extracted: 243
✓ Companies extracted: 158
✓ Vehicles extracted: 67
✓ Real estate extracted: 89
✓ Relationships extracted: 523
✓ Total LLM calls: 5
✓ JSON validity: 100% (function calling)
⏱ Time: 11m 31s
📁 Output: data/entities/
```

**Key Verification:** Function calling ensures ALL extraction is structured and valid!

---

# DAY 3: Deduplication, Graph & Anomaly Detection (34 SP)
**Goal:** Build relationship graph and detect anomalies
**Duration:** 8 hours

---

## Morning Session (4 hours) - 18 SP

### TASK-3.1: Person Matcher Implementation
**Story Points:** 8 SP
**Priority:** CRITICAL
**Dependencies:** TASK-2.8
**Assigned To:** Developer

**Description:**
Implement person matching algorithm with confidence scoring using multiple signals (RNOKPP, DOB, name, address).

**Acceptance Criteria:**
- [ ] Exact match on RNOKPP (confidence = 1.0)
- [ ] Exact match on УНЗР (confidence = 1.0)
- [ ] High confidence match: DOB + fuzzy name (confidence = 0.85-0.95)
- [ ] Medium confidence match: DOB + partial name (confidence = 0.6-0.79)
- [ ] Address overlap increases confidence by 0.1
- [ ] Document overlap increases confidence by 0.1
- [ ] Returns match pairs with confidence scores
- [ ] Logs all matches with reasoning
- [ ] Tested with known duplicate persons

**File:** `src/resolution/person_matcher.py`

**Implementation:**
```python
from fuzzywuzzy import fuzz

class PersonMatcher:
    def match_persons(self, p1: Person, p2: Person) -> float:
        """Return match confidence score (0.0 to 1.0)"""
        score = 0.0

        # Strong matches (high confidence)
        if p1.rnokpp and p2.rnokpp:
            if p1.rnokpp == p2.rnokpp:
                return 1.0  # Perfect match

        if p1.unzr and p2.unzr:
            if p1.unzr == p2.unzr:
                return 1.0

        # Weak matches (require multiple signals)
        if p1.birth_date == p2.birth_date:
            score += 0.3

        # Name similarity using fuzzy matching
        name_sim = self._fuzzy_match_names(p1.current_name, p2.current_name)
        score += name_sim * 0.4

        # Address overlap
        if self._has_address_overlap(p1, p2):
            score += 0.2

        # Document overlap
        if self._has_document_overlap(p1, p2):
            score += 0.1

        return min(score, 0.95)  # Cap at 0.95 for fuzzy matches

    def _fuzzy_match_names(self, n1: PersonName, n2: PersonName) -> float:
        """Fuzzy match two names (0.0 to 1.0)"""
        full_name1 = f"{n1.last_name} {n1.first_name} {n1.middle_name or ''}"
        full_name2 = f"{n2.last_name} {n2.first_name} {n2.middle_name or ''}"

        ratio = fuzz.ratio(full_name1, full_name2) / 100.0
        return ratio
```

---

### TASK-3.2: Company Matcher Implementation
**Story Points:** 3 SP
**Priority:** MEDIUM
**Dependencies:** TASK-2.8
**Assigned To:** Developer

**Description:**
Implement company matching algorithm using EDRPOU and fuzzy name matching.

**Acceptance Criteria:**
- [ ] Exact match on EDRPOU (confidence = 1.0)
- [ ] Fuzzy match on company name (confidence = 0.6-0.9)
- [ ] Returns match pairs with confidence scores

**File:** `src/resolution/company_matcher.py`

---

### TASK-3.3: Entity Merger Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-3.1, TASK-3.2
**Assigned To:** Developer

**Description:**
Implement entity merger that consolidates duplicate entities while preserving all source data.

**Acceptance Criteria:**
- [ ] Merges persons above confidence threshold (0.8)
- [ ] Merges companies above confidence threshold (0.8)
- [ ] Preserves all historical data from both entities
- [ ] Tracks merge provenance (which entities were merged)
- [ ] Prefers data from more recent sources
- [ ] Creates merge log for audit trail
- [ ] Saves merged entities to `data/resolved/`

**File:** `src/resolution/entity_merger.py`

**Merge Logic:**
```python
class EntityMerger:
    def merge_persons(self, p1: Person, p2: Person, confidence: float) -> Person:
        """Merge two person entities, preserving all data"""

        merged = Person(
            person_id=p1.person_id,  # Keep first ID
            rnokpp=p1.rnokpp or p2.rnokpp,
            unzr=p1.unzr or p2.unzr,
            birth_date=p1.birth_date or p2.birth_date,
            current_name=self._prefer_recent(p1.current_name, p2.current_name),
            all_names=self._merge_names(p1.all_names, p2.all_names),
            documents=self._merge_documents(p1.documents, p2.documents),
            contacts=self._merge_contacts(p1.contacts, p2.contacts),
            addresses=self._merge_addresses(p1.addresses, p2.addresses),
            employment_history=self._merge_employment(p1.employment_history, p2.employment_history),
            data_sources=list(set(p1.data_sources + p2.data_sources))
        )

        # Log merge
        self._log_merge(p1.person_id, p2.person_id, confidence)

        return merged
```

---

### TASK-3.4: Run Stage 3 on Full Dataset
**Story Points:** 2 SP
**Priority:** HIGH
**Dependencies:** TASK-3.3
**Assigned To:** Developer

**Description:**
Execute entity resolution (Stage 3) on full dataset.

**Acceptance Criteria:**
- [ ] All persons matched and merged
- [ ] At least 20% duplicate reduction
- [ ] Merge log generated
- [ ] Resolved entities saved to `data/resolved/`

**Command:**
```bash
python scripts/run_pipeline.py run --stage 3
```

---

## Afternoon Session (4 hours) - 16 SP

### TASK-3.5: Graph Builder Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-3.4
**Assigned To:** Developer

**Description:**
Implement graph builder that creates file-based adjacency lists for the knowledge graph.

**Acceptance Criteria:**
- [ ] Creates nodes for all entities (persons, companies, vehicles, real estate)
- [ ] Creates edges for all relationships
- [ ] Builds indices for fast lookup (by person_id, rnokpp, edrpou)
- [ ] Validates graph consistency (no orphan edges)
- [ ] Supports bidirectional traversal
- [ ] Saves to `data/graph/{nodes,edges,indices}/`

**File:** `src/graph/graph_builder.py`

**Graph Structure:**
```
data/graph/
  nodes/
    persons/
      {person_id}.json
    companies/
      {company_id}.json
    vehicles/
      {vehicle_id}.json
    real_estate/
      {property_id}.json
  edges/
    {relationship_id}.json
  indices/
    by_person/
      {person_id}.json -> ["related_node_id_1", "related_node_id_2"]
    by_rnokpp/
      {rnokpp}.json -> "person_id"
    by_edrpou/
      {edrpou}.json -> "company_id"
```

---

### TASK-3.6: Graph Analyzer Implementation
**Story Points:** 3 SP
**Priority:** MEDIUM
**Dependencies:** TASK-3.5
**Assigned To:** Developer

**Description:**
Implement graph analyzer for validation and statistics.

**Acceptance Criteria:**
- [ ] Counts nodes by type
- [ ] Counts edges by relationship type
- [ ] Detects orphan nodes
- [ ] Validates edge consistency
- [ ] Generates graph statistics report

**File:** `src/graph/graph_analyzer.py`

---

### TASK-3.7: Run Stage 4 on Full Dataset
**Story Points:** 2 SP
**Priority:** HIGH
**Dependencies:** TASK-3.6
**Assigned To:** Developer

**Description:**
Execute graph construction (Stage 4) on full dataset.

**Acceptance Criteria:**
- [ ] Graph built successfully
- [ ] At least 200 person nodes
- [ ] At least 500 relationship edges
- [ ] Indices created
- [ ] Graph validated

**Command:**
```bash
python scripts/run_pipeline.py run --stage 4
```

---

### TASK-3.8: Anomaly Detector Implementation
**Story Points:** 8 SP
**Priority:** CRITICAL
**Dependencies:** TASK-3.7
**Assigned To:** Developer

**Description:**
Implement anomaly detection engine with 6 anomaly types.

**Acceptance Criteria:**
- [ ] **INCOME_ASSET_MISMATCH**: Detects assets > 10x income
- [ ] **UNDECLARED_ASSET**: Detects assets without income source
- [ ] **RAPID_WEALTH_ACCUMULATION**: Detects multiple assets in short period
- [ ] **SHELL_COMPANY**: Detects offshore founders + short lifespan
- [ ] **CIRCULAR_OWNERSHIP**: DFS cycle detection in ownership graph
- [ ] **RELATED_PARTY_TRANSACTION**: Detects transactions between related persons
- [ ] Each anomaly has severity (low/medium/high/critical)
- [ ] Each anomaly has confidence score (0.0-1.0)
- [ ] Each anomaly has evidence list with sources
- [ ] Saves to `data/anomalies/`

**File:** `src/analysis/anomaly_detector.py`

**Implementation:**
```python
class AnomalyDetector:
    def detect_all_anomalies(self, graph: Graph) -> List[AnomalyDetection]:
        anomalies = []

        # Detect income/asset mismatches
        for person in graph.get_all_persons():
            if anomaly := self._detect_income_asset_mismatch(person, graph):
                anomalies.append(anomaly)

        # Detect shell companies
        for company in graph.get_all_companies():
            if anomaly := self._detect_shell_company(company):
                anomalies.append(anomaly)

        # Detect circular ownership
        for company in graph.get_all_companies():
            if anomaly := self._detect_circular_ownership(company, graph):
                anomalies.append(anomaly)

        return anomalies

    def _detect_income_asset_mismatch(self, person: Person, graph: Graph) -> Optional[AnomalyDetection]:
        # Get financial records
        income_records = graph.get_income_records(person.person_id)
        total_income = sum(r.amount for r in income_records if r.record_type == "income")

        # Get assets
        vehicles = graph.get_owned_vehicles(person.person_id)
        real_estate = graph.get_owned_real_estate(person.person_id)

        # Estimate asset values
        vehicle_value = sum(self._estimate_vehicle_value(v) for v in vehicles)
        property_value = sum(self._estimate_property_value(r) for r in real_estate)
        total_assets = vehicle_value + property_value

        # Calculate ratio
        if total_income > 0:
            ratio = total_assets / total_income
            if ratio > 10:
                return AnomalyDetection(
                    anomaly_id=generate_uuid(),
                    anomaly_type=AnomalyType.INCOME_ASSET_MISMATCH,
                    person_id=person.person_id,
                    severity="high" if ratio > 20 else "medium",
                    confidence=min(0.9, ratio / 50),
                    description=f"Assets ({total_assets:,.0f} UAH) exceed {ratio:.1f}x declared income ({total_income:,.0f} UAH)",
                    evidence=[
                        {"type": "income", "amount": total_income, "years": len(income_records)},
                        {"type": "vehicles", "count": len(vehicles), "value": vehicle_value},
                        {"type": "real_estate", "count": len(real_estate), "value": property_value}
                    ],
                    detected_at=datetime.utcnow()
                )
        return None
```

---

### TASK-3.9: Income Analyzer & Asset Valuator
**Story Points:** 5 SP
**Priority:** HIGH
**Dependencies:** TASK-3.8
**Assigned To:** Developer

**Description:**
Implement income analyzer and asset valuator for financial anomaly detection.

**Acceptance Criteria:**
- [ ] Income analyzer calculates total declared income
- [ ] Asset valuator estimates vehicle values (simplified)
- [ ] Asset valuator estimates property values (simplified)
- [ ] Supports multiple currencies (UAH primary)

**Files:**
- `src/analysis/income_analyzer.py`
- `src/analysis/asset_valuator.py`

---

### TASK-3.10: Run Stage 5 on Full Dataset
**Story Points:** 2 SP
**Priority:** HIGH
**Dependencies:** TASK-3.9
**Assigned To:** Developer

**Description:**
Execute anomaly detection (Stage 5) on full dataset.

**Acceptance Criteria:**
- [ ] At least 10 anomalies detected
- [ ] At least 3 different anomaly types
- [ ] Anomaly report generated

**Command:**
```bash
python scripts/run_pipeline.py run --stage 5
```

---

# DAY 4: Reporting & Polish (32 SP)
**Goal:** Generate PDF reports and finalize system
**Duration:** 8 hours

---

## Morning Session (4 hours) - 18 SP

### TASK-4.1: Profile Aggregator Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-3.10
**Assigned To:** Developer

**Description:**
Implement profile aggregator that collects all data for a person from the knowledge graph.

**Acceptance Criteria:**
- [ ] Aggregates person data from graph
- [ ] Collects all name history sorted chronologically
- [ ] Collects all documents sorted by date
- [ ] Collects all addresses sorted by date
- [ ] Collects employment history sorted by date
- [ ] Collects related persons (family)
- [ ] Collects related companies (business)
- [ ] Collects owned assets (vehicles, real estate)
- [ ] Collects financial records
- [ ] Collects detected anomalies
- [ ] Returns `PersonProfile` object

**File:** `src/reporting/profile_aggregator.py`

**Output Structure:**
```python
@dataclass
class PersonProfile:
    # Personal data
    full_name: str
    birth_date: date
    rnokpp: str
    unzr: str
    photo_url: Optional[str]

    # History
    former_names: List[PersonName]
    documents: List[IdentificationDocument]
    contacts: List[ContactInfo]
    addresses: List[Address]
    employment_history: List[Employment]

    # Relationships
    related_persons: List[Tuple[Person, RelationshipType]]
    related_companies: List[Tuple[Company, RelationshipType]]

    # Assets
    vehicles: List[Vehicle]
    real_estate: List[RealEstate]

    # Financial
    income_records: List[FinancialRecord]
    total_declared_income: float
    total_asset_value: float

    # Anomalies
    anomalies: List[AnomalyDetection]
    risk_score: float
```

---

### TASK-4.2: HTML Template Creation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-4.1
**Assigned To:** Developer

**Description:**
Create HTML template for person profile matching Профіль-зразок.pdf layout.

**Acceptance Criteria:**
- [ ] Template matches sample PDF structure
- [ ] Header section with name, photo placeholder, RNOKPP, УНЗР, date
- [ ] "Колишні ПІБ" table
- [ ] "Інші ідентифікаційні дані" table
- [ ] "Контактні дані" table
- [ ] "Документи" table
- [ ] "Пов'язані адреси" table
- [ ] "Додаткова інформація" section
- [ ] "Трудова діяльність" appendix
- [ ] "Пов'язані особи" appendix (physical and legal)
- [ ] "Майно" appendix (vehicles, real estate)
- [ ] "Фінансові аномалії" appendix
- [ ] Ukrainian labels throughout
- [ ] Responsive table layout
- [ ] UTF-8 encoding
- [ ] CSS styling for PDF conversion

**File:** `src/reporting/templates/person_profile.html`

**Template Structure:**
```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Профіль особи</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 10pt; }
        h1 { font-size: 14pt; border-bottom: 2px solid #000; }
        h2 { font-size: 12pt; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ccc; padding: 5px; text-align: left; }
        th { background-color: #f0f0f0; font-weight: bold; }
        .header { text-align: right; margin-bottom: 20px; }
        .photo-placeholder { width: 100px; height: 120px; border: 1px solid #000; }
    </style>
</head>
<body>
    <div class="header">
        <p>станом на: {{ generation_date }}</p>
    </div>

    <table>
        <tr>
            <td><strong>прізвище:</strong> {{ last_name }}</td>
            <td rowspan="4"><div class="photo-placeholder"></div></td>
        </tr>
        <tr><td><strong>ім'я:</strong> {{ first_name }}</td></tr>
        <tr><td><strong>по батькові:</strong> {{ middle_name }}</td></tr>
        <tr><td><strong>дата народження:</strong> {{ birth_date }}</td></tr>
        <tr><td><strong>РНОКПП:</strong> {{ rnokpp }}</td></tr>
        <tr><td><strong>УНЗР:</strong> {{ unzr }}</td></tr>
    </table>

    <h2>Колишні ПІБ:</h2>
    <table>
        <thead>
            <tr>
                <th>прізвище</th>
                <th>ім'я</th>
                <th>по батькові</th>
                <th>з</th>
                <th>до</th>
                <th>джерело</th>
            </tr>
        </thead>
        <tbody>
            {% for name in former_names %}
            <tr>
                <td>{{ name.last_name }}</td>
                <td>{{ name.first_name }}</td>
                <td>{{ name.middle_name }}</td>
                <td>{{ name.valid_from }}</td>
                <td>{{ name.valid_to }}</td>
                <td>{{ name.source }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- More sections... -->
</body>
</html>
```

---

### TASK-4.3: PDF Generator Implementation
**Story Points:** 8 SP
**Priority:** CRITICAL
**Dependencies:** TASK-4.2
**Assigned To:** Developer

**Description:**
Implement PDF generator using ReportLab or WeasyPrint to convert HTML template to PDF.

**Acceptance Criteria:**
- [ ] Renders HTML template with Jinja2
- [ ] Converts HTML to PDF with proper layout
- [ ] Supports Ukrainian fonts (DejaVu Sans)
- [ ] Handles multi-page reports
- [ ] Handles table pagination
- [ ] Generates within 5 seconds per report
- [ ] Output file size < 5 MB
- [ ] PDF matches sample format visually
- [ ] Tested with 10+ person profiles

**File:** `src/reporting/pdf_generator.py`

**Implementation:**
```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

class PDFGenerator:
    def __init__(self, template_dir: str = "src/reporting/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_person_report(self, profile: PersonProfile, output_path: str):
        """Generate PDF report for a person"""

        # Render HTML template
        template = self.env.get_template("person_profile.html")
        html_content = template.render(
            generation_date=datetime.now().strftime("%d.%m.%Y"),
            last_name=profile.full_name.split()[0],
            first_name=profile.full_name.split()[1],
            middle_name=profile.full_name.split()[2] if len(profile.full_name.split()) > 2 else "",
            birth_date=profile.birth_date.strftime("%d.%m.%Y"),
            rnokpp=profile.rnokpp,
            unzr=profile.unzr,
            former_names=profile.former_names,
            documents=profile.documents,
            contacts=profile.contacts,
            addresses=profile.addresses,
            employment_history=profile.employment_history,
            related_persons=profile.related_persons,
            related_companies=profile.related_companies,
            vehicles=profile.vehicles,
            real_estate=profile.real_estate,
            anomalies=profile.anomalies
        )

        # Convert to PDF
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=self._get_pdf_styles())]
        )

        logger.info(f"Generated PDF report: {output_path}")
```

---

## Afternoon Session (3 hours) - 11 SP

### TASK-4.4: Run Stage 6 on All Persons
**Story Points:** 3 SP
**Priority:** CRITICAL
**Dependencies:** TASK-4.3
**Assigned To:** Developer

**Description:**
Execute report generation (Stage 6) for all persons in the dataset.

**Acceptance Criteria:**
- [ ] PDF generated for each resolved person
- [ ] All PDFs saved to `data/reports/`
- [ ] Generation logs with any errors
- [ ] Sample reports manually inspected for quality
- [ ] At least 50 PDF reports generated

**Command:**
```bash
python scripts/run_pipeline.py run --stage 6
```

**Expected Output:**
```
Stage 6: Report Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 186/186 persons
✓ PDF reports generated: 186
✗ Failed: 0
⏱ Time: 14m 23s (avg 4.6s per report)
📁 Output: data/reports/
```

---

### TASK-4.5: Validate PDF Output Quality
**Story Points:** 3 SP
**Priority:** HIGH
**Dependencies:** TASK-4.4
**Assigned To:** Developer

**Description:**
Manually validate generated PDF reports against sample format, fix formatting issues.

**Acceptance Criteria:**
- [ ] At least 10 PDFs manually reviewed
- [ ] Layout matches Профіль-зразок.pdf
- [ ] All sections present
- [ ] Ukrainian text renders correctly
- [ ] Tables are properly formatted
- [ ] Page breaks work correctly
- [ ] No visual glitches

**Quality Checklist:**
- [ ] Header information complete
- [ ] Photo placeholder present
- [ ] All tables have borders
- [ ] Font is readable
- [ ] No text overflow
- [ ] Assets section included
- [ ] Anomalies section included
- [ ] Sources attributed correctly

---

### TASK-4.6: Pipeline Orchestrator Implementation
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-4.5
**Assigned To:** Developer

**Description:**
Implement pipeline orchestrator that runs all 6 stages sequentially with checkpointing (HYBRID APPROACH).

**Acceptance Criteria:**
- [ ] Runs all 6 stages in order
- [ ] Checkpoint system (saves progress after each stage)
- [ ] Resume capability (continue from last checkpoint)
- [ ] Progress tracking with tqdm
- [ ] Error handling and recovery
- [ ] Logging for each stage
- [ ] Performance metrics (time per stage)
- [ ] Can run specific stage with `--stage` flag

**File:** `src/pipeline/orchestrator.py`

**Implementation:**
```python
class PipelineOrchestrator:
    def __init__(self):
        self.stages = [
            Stage1FormatNormalizer(),    # NO LLM
            Stage2LLMBatchExtractor(),   # YES LLM
            Stage3EntityResolution(),    # NO LLM
            Stage4GraphBuilder(),        # NO LLM
            Stage5AnomalyDetector(),     # NO LLM
            Stage6ReportGenerator()      # NO LLM
        ]
        self.checkpoint_file = "data/.pipeline_checkpoint.json"

    def run_all(self, resume: bool = False):
        """Run all pipeline stages"""
        checkpoint = self.load_checkpoint() if resume else None
        start_stage = checkpoint.get('last_stage', 0) if checkpoint else 0

        for i, stage in enumerate(self.stages[start_stage:], start=start_stage):
            logger.info(f"Running Stage {i+1}: {stage.name}")

            try:
                stage.run()
                self.save_checkpoint({'last_stage': i + 1, 'timestamp': datetime.utcnow()})
                logger.info(f"✓ Stage {i+1} completed successfully")
            except Exception as e:
                logger.error(f"✗ Stage {i+1} failed: {e}")
                self.save_checkpoint({'last_stage': i, 'error': str(e)})
                raise

        logger.info("🎉 Pipeline completed successfully!")
```

---

## Evening Session (1 hour) - 3 SP

### TASK-4.7: CLI Implementation
**Story Points:** 3 SP
**Priority:** HIGH
**Dependencies:** TASK-4.6
**Assigned To:** Developer

**Description:**
Implement CLI using Click for all pipeline operations.

**Acceptance Criteria:**
- [ ] `run` command to run full pipeline or specific stage
- [ ] `report` command to generate single person report
- [ ] `stats` command to show processing statistics
- [ ] `--resume` flag for checkpoint recovery
- [ ] `--stage` flag for running specific stage
- [ ] Help text for all commands
- [ ] Colorized output with rich/click

**File:** `scripts/run_pipeline.py`

**Commands:**
```bash
# Run full pipeline
python scripts/run_pipeline.py run

# Run specific stage
python scripts/run_pipeline.py run --stage 1

# Resume from checkpoint
python scripts/run_pipeline.py run --resume

# Generate single report
python scripts/run_pipeline.py report 550e8400-e29b-41d4-a716-446655440000 --output report.pdf

# Show statistics
python scripts/run_pipeline.py stats
```

---

### TASK-4.8: README and Documentation
**Story Points:** 3 SP
**Priority:** MEDIUM
**Dependencies:** TASK-4.7
**Assigned To:** Developer

**Description:**
Write comprehensive README with installation, usage, troubleshooting.

**Acceptance Criteria:**
- [ ] Project overview
- [ ] Installation instructions
- [ ] Usage examples for all CLI commands
- [ ] Pipeline stages explanation
- [ ] Troubleshooting section
- [ ] Architecture overview
- [ ] Data sources reference

**File:** `README.md`

---

### TASK-4.9: End-to-End Testing
**Story Points:** 5 SP
**Priority:** CRITICAL
**Dependencies:** TASK-4.7
**Assigned To:** Developer

**Description:**
Run full end-to-end pipeline test, verify all success criteria from PRD.

**Acceptance Criteria:**
- [ ] All 207 files parsed (>95% success rate)
- [ ] At least 50 person profiles created
- [ ] At least 100 relationships extracted
- [ ] At least 10 anomalies detected
- [ ] All persons have PDF reports
- [ ] PDF reports match sample format
- [ ] Pipeline completes in <30 minutes
- [ ] All CLI commands work
- [ ] No critical errors in logs

**Test Script:** `scripts/e2e_test.py`

**Final Verification Checklist:**
```
✓ Parsing success rate: ___% (target >95%)
✓ Persons extracted: ___ (target >50)
✓ Companies extracted: ___
✓ Vehicles extracted: ___
✓ Real estate extracted: ___
✓ Relationships extracted: ___ (target >100)
✓ Anomalies detected: ___ (target >10)
✓ PDF reports generated: ___ (target 100%)
✓ Total processing time: ___ minutes (target <30)
✓ LLM API calls: ___ (target <30)
✓ Estimated cost: $___ (target <$10)
```

---

# Summary Statistics (HYBRID APPROACH)

## Total Story Points by Day
- **Day 1:** 26 SP (Format Normalization - NO LLM)
- **Day 2:** 35 SP (LLM Batch Extraction - YES LLM)
- **Day 3:** 34 SP (Deduplication, Graph & Anomaly Detection - NO LLM)
- **TOTAL:** 95 SP (down from 142 SP in custom parser approach)

## Savings from Hybrid Approach
- **Story Points Saved:** 47 SP (33% reduction)
- **Files to Implement:** 18 files (down from 27+ files)
- **Development Time:** 24 hours (down from 32 hours)
- **Risk Level:** LOW (was MEDIUM)

## Story Points by Priority
- **CRITICAL:** 58 SP (61%)
- **HIGH:** 27 SP (28%)
- **MEDIUM:** 7 SP (7%)
- **LOW:** 3 SP (3%)

## Story Points by Component (HYBRID)
- **Format Parsers (Generic):** 21 SP (22%) - NO registry-specific!
- **LLM Integration:** 23 SP (24%) - Does ALL semantic work!
- **Entity Resolution:** 18 SP (19%)
- **Graph Building:** 10 SP (11%)
- **Anomaly Detection:** 13 SP (14%)
- **Reporting:** 18 SP (19%)
- **Infrastructure:** 8 SP (8%)

## Velocity Tracking
- **Expected Velocity:** 32 SP per day
- **Required Daily Hours:** 8 hours
- **SP per Hour:** ~4.0 SP/hour

## Function Calling Benefits
- **JSON Validity:** 99%+ (guaranteed by function calling)
- **Deterministic Output:** temperature=0 for consistent results
- **Model:** lapa-function-calling (optimized for structured extraction)
- **LLM Usage:** Stage 2 only (5 batched requests)

---

# Risk Mitigation Tasks

## BACKUP-1: LLM Fallback Implementation
**If LapaLLM is unavailable or too expensive**
- [ ] Skip Stage 2 LLM extraction
- [ ] Use simple rule-based extraction from normalized JSON
- [ ] Use fuzzywuzzy for name deduplication
- [ ] Use regex for basic pattern extraction
- [ ] Accept lower extraction quality
**Effort:** 13 SP (replaces Stage 2)
**Impact:** Loses semantic understanding, normalization

## BACKUP-2: Simple PDF Generation
**If ReportLab/WeasyPrint issues**
- [ ] Generate simple HTML reports
- [ ] Use browser print-to-PDF (wkhtmltopdf)
- [ ] Accept lower quality formatting
**Effort:** 3 SP

## BACKUP-3: Reduce Batch Size
**If LLM context limits exceeded**
- [ ] Reduce batch size from 50 to 25 files
- [ ] Increases LLM calls from 5 to 10
- [ ] Doubles processing time for Stage 2
**Effort:** 0 SP (config change only)

---

# Daily Standup Template

## Morning Standup
- **Yesterday:** Completed tasks list
- **Today:** Planned tasks list
- **Blockers:** Any issues or dependencies

## End of Day Retrospective
- **Completed:** Tasks finished (SP completed)
- **In Progress:** Tasks started but not finished
- **Blocked:** Tasks blocked by dependencies or issues
- **Tomorrow:** Plan for next day

---

**END OF TASK LIST (HYBRID APPROACH + FUNCTION CALLING)**

This task list provides a complete implementation roadmap with **95 story points across 3 days**, breaking down every component needed to build the NABU AI Platform using the **HYBRID APPROACH WITH FUNCTION CALLING**:

## Key Benefits of Hybrid Approach + Function Calling:
1. **33% Faster Development:** 95 SP vs 142 SP (47 SP saved)
2. **60% Less Code:** 18 files vs 27+ files
3. **Simpler Architecture:** Generic format parsers + LLM function calling
4. **Flexible:** LLM handles schema variations automatically
5. **99%+ JSON Validity:** Function calling guarantees structured output
6. **Deterministic:** temperature=0 for consistent, reproducible results
7. **Lower Risk:** Can finish in 3 days instead of 4

## Pipeline Flow:
- **Stage 1 (NO LLM):** Format normalization (XML/JSON/HTML/Excel/CSV → clean JSON)
- **Stage 2 (YES LLM with Function Calling):** "lapa-function-calling" model extracts ALL entities with guaranteed structure
- **Stage 3-6 (NO LLM):** Deduplication, graph building, anomaly detection, PDF generation

## Function Calling Advantages:
- **Model:** "lapa-function-calling" (temperature=0)
- **Structured Output:** JSON schema enforcement
- **Reliability:** No more parsing errors or malformed JSON
- **Efficiency:** Optimized for entity extraction tasks

This approach is **pragmatic, achievable, and reliable** for the hackathon timeline!
