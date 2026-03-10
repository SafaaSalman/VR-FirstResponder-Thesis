# Emergency Protocol Data Sources — Supplementary Research
## Part A–D: Military Protocols, Disaster Databases, Communication Datasets, and Structured Protocol Tools
### Generated: 2026-03 | Companion to `Protocol_Datasets_Research.md`

> **Scope:** This supplement covers sources **not already in the main research document**, focusing on:
> - **Part A** — Military & international medical protocols
> - **Part B** — After-action reports & disaster record databases
> - **Part C** — Emergency call transcripts & communication corpora
> - **Part D** — Open-source tools with machine-readable protocol representations

---

## Table of Contents

1. [Part A: Military & International Medical Protocols](#part-a-military--international-medical-protocols)
2. [Part B: After-Action Reports & Disaster Record Databases](#part-b-after-action-reports--disaster-record-databases)
3. [Part C: Emergency Call Transcripts & Communication Datasets](#part-c-emergency-call-transcripts--communication-datasets)
4. [Part D: Open-Source Tools & Structured Protocol Representations](#part-d-open-source-tools--structured-protocol-representations)
5. [GitHub Repository Search Results](#github-repository-search-results)
6. [Summary: AI Training Readiness Matrix](#summary-ai-training-readiness-matrix)
7. [Thesis Contribution Opportunity](#thesis-contribution-opportunity)

---

## Part A: Military & International Medical Protocols

### A.1 Tactical Combat Casualty Care (TCCC) Guidelines

| Field | Detail |
|---|---|
| **Full Name** | Tactical Combat Casualty Care (TCCC) Guidelines |
| **Organization** | Committee on Tactical Combat Casualty Care (CoTCCC) / Joint Trauma System (JTS), Defense Health Agency |
| **Domain** | Military pre-hospital medicine, battlefield trauma care |
| **Format** | PDF documents, algorithm cards (image-based flowcharts), mobile app content |
| **Machine-Readable?** | ❌ No — primarily PDF/image-based; algorithm cards are visual flowcharts |
| **Branching Logic?** | ✅ Yes — TCCC has clear **MARCH algorithm** (Massive hemorrhage → Airway → Respiration → Circulation → Hypothermia/Hypothermia prevention) with decision branches at each phase |
| **License** | Public domain (U.S. Government work); free access via Deployed Medicine (login required since Dec 2023) |
| **URL** | https://deployedmedicine.com/ |
| **AI Training Notes** | Algorithm cards would need OCR + manual structuring into decision trees. The MARCH sequence is highly structured and ideal for conversion to JSON/XML decision trees. Historical revisions tracked. Three phases: **Care Under Fire** → **Tactical Field Care** → **Tactical Evacuation Care**, each with distinct decision logic. |

### A.2 Deployed Medicine Platform (DHA)

| Field | Detail |
|---|---|
| **Full Name** | Deployed Medicine — Military Medical Training Platform |
| **Organization** | Defense Health Agency (DHA) in partnership with Joint Trauma System (JTS) and CoTCCC |
| **Domain** | Military medical training: TCCC, Clinical Practice Guidelines, En Route Care, Prolonged Casualty Care |
| **Format** | Web-based LMS with PDF/video/interactive content |
| **Machine-Readable?** | ⚠️ Partial — structured collection catalogs with topic hierarchies, but content requires login |
| **Branching Logic?** | ✅ Yes — contains CPGs with decision algorithms and multiple training pathways |
| **License** | Public domain (U.S. Government); free account required since 14 Dec 2023 |
| **URL** | https://deployedmedicine.com/ , Content: https://deployedmedicine.allogy.net/ |
| **AI Training Notes** | **Central repository for military medical training content.** Collections include: TCCC Resources, Clinical Practice Guidelines (CPGs), Prolonged Casualty Care, En Route Combat Casualty Care, Canine-K9 TCCC, Combat LifeSaver, Combat Medic/Corpsman, Combat Paramedic/Provider, Operational Emergency Medical Skills (OEMS). Featured CPGs include JTS Airway Management, Pelvic Fracture Care, REBOA, Joint En Route Care Guidelines. Mobile apps available (iOS/Android). Could serve as primary source for military VR training scenarios. |

### A.3 Committee for Tactical Emergency Casualty Care (C-TECC) Guidelines

| Field | Detail |
|---|---|
| **Full Name** | Committee for Tactical Emergency Casualty Care (C-TECC) Guidelines |
| **Organization** | C-TECC (civilian adaptation of military TCCC) |
| **Domain** | Civilian high-threat / tactical emergency medicine (active shooter, mass casualty, law enforcement) |
| **Format** | PDF guidelines, reference documents |
| **Machine-Readable?** | ❌ No — PDF-based guidance documents |
| **Branching Logic?** | ✅ Yes — mirrors TCCC's phase-based structure adapted for civilian contexts: **Direct Threat Care** → **Indirect Threat Care** → **Evacuation Care** |
| **License** | Freely available; no explicit open-source license stated |
| **URL** | https://c-tecc.org/our-work/guidance , https://c-tecc.org/our-work/references |
| **AI Training Notes** | Strong candidate for conversion to structured protocols. Phase-based structure (Direct/Indirect/Evacuation) maps well to state machines. Bridges military and civilian contexts — ideal for VR scenarios involving active threat situations. Reference list provides evidence base for each recommendation. |

### A.4 WHO Emergency Medical Teams (EMT) Classification & Standards

| Field | Detail |
|---|---|
| **Full Name** | Classification and Minimum Standards for Emergency Medical Teams |
| **Organization** | World Health Organization (WHO), Emergency Medical Teams Initiative |
| **Domain** | International emergency/disaster medical response standardization |
| **Format** | PDF (ISBN 9789240029330, published June 2021), Knowledge Hub resources |
| **Machine-Readable?** | ❌ No — PDF publication |
| **Branching Logic?** | ⚠️ Partial — classification tiers (Type 1 Fixed/Mobile, Type 2, Type 3) have criteria-based branching |
| **License** | CC BY-NC-SA 3.0 IGO (WHO standard license) |
| **URL** | https://extranet.who.int/emt/ (EMT Initiative portal) |
| **AI Training Notes** | EMT classification system provides structured capability tiers for deployment decision-making. Minimum standards define decision criteria for team type selection. Knowledge Hub contains training materials. Could be converted to deployment decision trees for international disaster VR scenarios. |

### A.5 FAA Emergency Procedure Handbooks

| Field | Detail |
|---|---|
| **Full Name** | FAA Handbooks, Manuals & Advisory Circulars |
| **Organization** | Federal Aviation Administration (FAA), U.S. DOT |
| **Domain** | Aviation safety, emergency procedures, pilot/examiner training |
| **Format** | PDF documents (Airplane Flying Handbook, Aviation Maintenance, etc.) |
| **Machine-Readable?** | ⚠️ Partial — text-searchable PDFs; Advisory Circulars have structured metadata |
| **Branching Logic?** | ✅ Yes — emergency procedure checklists follow strict if-then logic |
| **License** | Public domain (U.S. Government work) |
| **URL** | https://www.faa.gov/regulations_policies/handbooks_manuals |
| **AI Training Notes** | Emergency procedure sections contain structured checklists ideal for decision-tree extraction. Relevant sections: engine failure, in-flight fire, forced landing, ditching, electrical failure. Advisory Circulars provide structured guidance. Applicable for aviation disaster VR scenarios. |

---

## Part B: After-Action Reports & Disaster Record Databases

### B.1 NTSB Aviation Accident Database (CAROL Query)

| Field | Detail |
|---|---|
| **Full Name** | NTSB CAROL Query System / Aviation Accident & Incident Data System |
| **Organization** | National Transportation Safety Board (NTSB) |
| **Domain** | Aviation, highway, marine, railroad, and pipeline accident investigation |
| **Format** | **Microsoft Access database** (downloadable bulk), web query tool (CAROL), monthly text lists |
| **Machine-Readable?** | ✅ **Yes** — downloadable Access database, structured query interface |
| **Branching Logic?** | ⚠️ Partial — causal factor analysis follows structured investigation methodology |
| **License** | Public domain (U.S. Government work) |
| **URL** | https://carol.ntsb.gov/ (query), https://app.ntsb.gov/avdata/ (bulk downloads, 1962–present) |
| **AI Training Notes** | **Excellent for AI training.** Structured database with: event type, probable cause, contributing factors, injury severity, aircraft damage, weather conditions, pilot actions. Supports Basic Search, Aviation Search, and Custom Search Builder. Bulk data in Access format easily convertible to SQL/CSV. Can generate realistic incident scenarios for VR training by mining common patterns and causal chains. |

### B.2 NFIRS → NERIS (Fire Incident Reporting)

| Field | Detail |
|---|---|
| **Full Name** | National Fire Incident Reporting System (NFIRS) → National Emergency Response Information System (NERIS) |
| **Organization** | U.S. Fire Administration (USFA), FEMA |
| **Domain** | Fire department incident reporting, fire investigation data |
| **Format** | Structured database (NFIRS 5.0), XML schemas (NERIS beta) |
| **Machine-Readable?** | ✅ **Yes** — both use structured data schemas |
| **Branching Logic?** | ✅ Yes — incident type codes follow hierarchical classification tree |
| **License** | Public domain (U.S. Government work) |
| **URL** | https://usfa.fema.gov/nfirs/ |
| **AI Training Notes** | **⚠️ CRITICAL:** NFIRS sunsetting **January 31, 2026**, transitioning to NERIS. As of 2025 YTD: 17,090 fire departments, 9.3M incidents. NERIS beta modernizes the format with XML schemas. Incident classification hierarchy maps well to decision trees. Can be used for statistical scenario generation. |

### B.3 FEMA Disaster Declarations API

| Field | Detail |
|---|---|
| **Full Name** | OpenFEMA API — Disaster Declarations Summaries |
| **Organization** | Federal Emergency Management Agency (FEMA) |
| **Domain** | U.S. disaster declarations, emergency management |
| **Format** | **REST API returning JSON** |
| **Machine-Readable?** | ✅ **Yes** — fully structured JSON via REST API |
| **Branching Logic?** | ⚠️ Partial — declaration types (DR, EM, FM, FS) and program designations follow classification logic |
| **License** | Public domain (U.S. Government), open API |
| **URL** | https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries |
| **AI Training Notes** | **Directly ingestible by ML pipelines.** Confirmed working JSON API with fields: `femaDeclarationString`, `disasterNumber`, `state`, `declarationType`, `declarationDate`, `incidentType`, `declarationTitle`, `ihProgramDeclared`, `iaProgramDeclared`, `paProgramDeclared`, `hmProgramDeclared`, designated areas, FIPS codes. Thousands of records from 1953–present. Additional endpoints for housing assistance, public assistance grants, hazard mitigation grants. Can power VR scenario selection based on real disaster patterns. |

### B.4 ReliefWeb / Humanitarian Data Exchange

| Field | Detail |
|---|---|
| **Full Name** | ReliefWeb — Humanitarian Information Service + Humanitarian Data Exchange (HDX) |
| **Organization** | United Nations OCHA |
| **Domain** | International humanitarian response, disaster reporting |
| **Format** | HTML articles, PDF reports, **REST API**, **structured datasets (HDX)** |
| **Machine-Readable?** | ✅ **Yes** — REST API + HDX datasets in CSV/JSON/GeoJSON |
| **Branching Logic?** | ❌ No — narrative reports, not procedural |
| **License** | Open data; terms vary by content source |
| **URL** | https://reliefweb.int/ , API: https://api.reliefweb.int/ , HDX: https://data.humdata.org/ |
| **AI Training Notes** | Extensive database of disaster situation reports, analyses, assessments. HDX provides structured datasets including: affected populations, displacement data, infrastructure damage assessments, resource needs. API enables programmatic access by country, type, date. Good for contextual training data and international disaster scenario generation. |

### B.5 EM-DAT International Disaster Database

| Field | Detail |
|---|---|
| **Full Name** | EM-DAT: The International Disaster Database |
| **Organization** | Centre for Research on the Epidemiology of Disasters (CRED), UCLouvain, Belgium |
| **Domain** | Global disaster epidemiology (natural + technological disasters) |
| **Format** | Structured database, downloadable datasets, data portal |
| **Machine-Readable?** | ✅ **Yes** — structured tabular data with hierarchical classification |
| **Branching Logic?** | ✅ Yes — hierarchical classification: Group → Subgroup → Type → Subtype |
| **License** | Open access for non-commercial/academic use; sponsored by USAID |
| **URL** | https://emdat.be/ , Portal: https://public.emdat.be/ , Docs: https://doc.emdat.be/ |
| **AI Training Notes** | **Excellent for AI training.** 27,000+ disaster records from 1900–present. Classification: Natural (Geophysical, Meteorological, Hydrological, Climatological, Biological, Extra-terrestrial) and Technological (Industrial, Transport, Miscellaneous). Each record includes: country, dates, deaths, affected population, economic damages. Usable for: scenario generation, disaster type classification, historical pattern analysis for VR training curriculum design. |

### B.6 CDC MMWR (Morbidity and Mortality Weekly Report)

| Field | Detail |
|---|---|
| **Full Name** | Morbidity and Mortality Weekly Report (MMWR) |
| **Organization** | Centers for Disease Control and Prevention (CDC) |
| **Domain** | Public health surveillance, disease outbreaks, emergency health events |
| **Format** | HTML articles, PDF, searchable archive |
| **Machine-Readable?** | ⚠️ Partial — structured metadata; article text is narrative |
| **Branching Logic?** | ❌ No — epidemiological reports, not procedural protocols |
| **License** | Public domain (U.S. Government work) |
| **URL** | https://www.cdc.gov/mmwr/ |
| **AI Training Notes** | Includes Weekly Reports, Recommendations/Reports, Surveillance Summaries. Searchable by topic. Useful for evidence-based scenario content: disease outbreak response, mass casualty events, bioterrorism preparedness, environmental health emergencies. Current through Feb 2026. |

---

## Part C: Emergency Call Transcripts & Communication Datasets

### C.1 Medical Priority Dispatch System (MPDS) / ProQA

| Field | Detail |
|---|---|
| **Full Name** | Medical Priority Dispatch System (MPDS) / ProQA Computer-Aided Dispatch |
| **Organization** | Priority Dispatch Corp. / International Academies of Emergency Dispatch (IAED) |
| **Domain** | Emergency medical dispatch, 911 call processing |
| **Format** | Proprietary structured protocols (card-based system with deterministic decision trees) |
| **Machine-Readable?** | ✅ Yes (internally) — highly structured with Chief Complaint codes, Key Questions, Determinant Codes, Pre-Arrival Instructions |
| **Branching Logic?** | ✅ **Extensively branching** — each of 33 Chief Complaint protocols contains multi-level decision trees |
| **License** | ⚠️ **Proprietary / Commercial** — not openly available |
| **URL** | https://prioritydispatch.net/about-mpds/ |
| **AI Training Notes** | **Gold standard for emergency dispatch decision trees** but proprietary. Structure: Chief Complaint → Case Entry → Key Questions → Determinant Codes (OMEGA through ECHO severity levels). 33 protocols cover all medical emergencies. Pre-Arrival Instructions provide step-by-step telephone-guided procedures. For academic use: consider licensing for research, or build open alternative based on published studies analyzing MPDS performance. Numerous peer-reviewed papers describe MPDS performance metrics that can inform open alternatives. |

### C.2 Linguistic Data Consortium (LDC) Corpora

| Field | Detail |
|---|---|
| **Full Name** | Linguistic Data Consortium Catalog |
| **Organization** | Linguistic Data Consortium (LDC), University of Pennsylvania |
| **Domain** | Speech and language data, including telephone speech, emergency communications |
| **Format** | Audio files (WAV, SPHERE), text transcripts, annotations (XML, SGML, custom formats) |
| **Machine-Readable?** | ✅ **Yes** — annotated corpora in standard NLP formats |
| **Branching Logic?** | ❌ No — raw conversational data, not procedural |
| **License** | LDC membership or individual purchase; academic pricing available |
| **URL** | https://catalog.ldc.upenn.edu/ |
| **AI Training Notes** | LDC hosts hundreds of speech/language corpora. Relevant collections to search for: emergency call recordings, telephone speech (Switchboard, Fisher), conversational analysis datasets, CTS (conversational telephone speech). Key resource for training speech recognition and NLP models for emergency communications in VR. Requires institutional membership or per-corpus licensing. Search catalog for "emergency," "911," "dispatch," "medical," "crisis." |

### C.3 Crisis Communication / Emergency NLP Datasets

| Field | Detail |
|---|---|
| **Full Name** | Various crisis communication and emergency NLP datasets |
| **Organization** | Qatar Computing Research Institute (CrisisNLP), University of Colorado (CrisisLex), various academic institutions |
| **Domain** | Crisis informatics, emergency social media analysis, disaster communication |
| **Format** | CSV, JSON, text files (tweet datasets, classified messages, crisis lexicons) |
| **Machine-Readable?** | ✅ **Yes** — labeled datasets in standard ML formats |
| **Branching Logic?** | ❌ No — classification data, not procedural |
| **License** | Varies — many CC-BY or research-only |
| **URLs** | |
| | • **CrisisNLP:** https://crisisnlp.qcri.org/ — labeled tweet datasets from 30+ disaster events |
| | • **CrisisLex:** https://crisislex.org/ — crisis-specific lexicons and labeled collections |
| | • **CrisisMMD:** Multi-modal (text + image) crisis data (academic papers) |
| | • **CrisisTransformers:** https://github.com/firojalam/crisis_datasets — Hugging Face–compatible crisis datasets |
| | • **HumAID:** Human-annotated disaster datasets for crisis response |
| **AI Training Notes** | CrisisNLP provides labeled tweets classified by informativeness and type (infrastructure damage, casualties, needs, etc.) across 30+ events. CrisisLex provides crisis-specific lexicons. Useful for training NLP models that: interpret emergency communications, extract actionable information from unstructured reports, classify urgency levels. Can augment VR scenarios with realistic background communication feeds. |

### C.4 NEMSIS Research Dataset (EMS Call Records)

| Field | Detail |
|---|---|
| **Full Name** | NEMSIS Public-Release Research Dataset |
| **Organization** | NEMSIS TAC, University of Utah / NHTSA Office of EMS |
| **Domain** | EMS patient care records — the closest available approximation to emergency call outcome data |
| **Format** | Structured dataset (formats vary by release year) |
| **Machine-Readable?** | ✅ **Yes** — structured tabular data |
| **Branching Logic?** | ✅ Yes — captures intervention sequences, assessment findings, treatment decisions |
| **License** | Free upon request for research purposes |
| **URL** | https://nemsis.org/request-research-data/ , https://nemsis.org/2024-nemsis-public-release-research-dataset-now-available/ |
| **AI Training Notes** | **11.5+ million EMS patient care records per year.** Each record captures: dispatch reason, chief complaint, assessment findings, vitals, interventions, medications, transport decisions, outcomes. While not raw call transcripts, this data captures the **structured outcome of emergency calls** and can be used to: train dispatch-to-treatment prediction models, generate realistic EMS scenario sequences, validate protocol adherence in VR training. 2024 dataset now available. |

---

## Part D: Open-Source Tools & Structured Protocol Representations

### D.1 HL7 FHIR PlanDefinition Resource (R5)

| Field | Detail |
|---|---|
| **Full Name** | HL7 FHIR R5 — Resource PlanDefinition |
| **Organization** | Health Level Seven International (HL7) |
| **Domain** | Healthcare interoperability, clinical decision support, care protocols |
| **Format** | **JSON / XML** (FHIR resources) |
| **Machine-Readable?** | ✅ **Yes** — fully structured FHIR resources |
| **Branching Logic?** | ✅ **Extensive** — hierarchical action groups, conditions, triggers, selection behaviors, temporal relationships |
| **License** | CC0 (specification); Creative Commons for HL7 content |
| **URL** | https://www.hl7.org/fhir/plandefinition.html |
| **AI Training Notes** | **Premier standard for representing clinical protocols as machine-readable data.** |

**Key Features for Emergency Protocol Representation:**

| Feature | FHIR Field | Emergency Use Case |
|---|---|---|
| **Hierarchical Actions** | `action` (nested) | Represent MARCH phases, triage steps, ICS sections |
| **Conditions** | `action.condition` (applicability / start / stop) | IF patient breathing THEN... ELSE... |
| **Selection** | `action.selectionBehavior` | any / all / exactly-one / at-most-one / one-or-more |
| **Temporal Sequencing** | `action.relatedAction` | before-start / after-end / concurrent (for parallel tasks) |
| **Grouping** | `action.groupingBehavior` | visual-group / logical-group / sentence-group |
| **Required vs Optional** | `action.requiredBehavior` | must / could / must-unless-documented |
| **Dynamic Values** | `action.dynamicValue` | Computed values from CQL/FHIRPath expressions |
| **Protocol Types** | `type` | order-set / clinical-protocol / eca-rule / workflow-definition |
| **Triggers** | `action.trigger` | named-event / periodic / data-changed / data-added / data-accessed |
| **Apply Operation** | `$apply` | Transforms protocol template into patient-specific request |

**Why this is ideal for VR emergency training:**
- Native support for decision trees, state machines, and branching protocols
- JSON format directly consumable by Unity/Unreal game engines
- Can reference SNOMED CT, ICD-10, LOINC codes for standardized terminology
- `$apply` operation transforms template protocols into scenario-specific instances
- Maturity Level 4 (Trial Use), widely implemented in healthcare systems
- Could serve as the **canonical interchange format** between protocol databases and VR engines

### D.2 OpenEMR Clinical Decision Rules Engine

| Field | Detail |
|---|---|
| **Full Name** | OpenEMR Clinical Decision Rules (CDR) Engine |
| **Organization** | OpenEMR Foundation, Inc. |
| **Domain** | Open-source electronic health records, clinical decision support |
| **Format** | PHP source code, MySQL database schemas |
| **Machine-Readable?** | ✅ **Yes** — rules stored in structured database tables |
| **Branching Logic?** | ✅ Yes — rule engine with filters, targets, actions, criteria types |
| **License** | GNU GPL v3 |
| **URL** | https://github.com/openemr/openemr , https://www.open-emr.org/ |
| **AI Training Notes** | ONC Certified (Version 8, Feb 2026). 30+ supported languages. FHIR integration in progress. |

**Architecture of the CDR Engine (from GitHub source analysis):**

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenEMR CDR Engine                         │
│  Source: src/ClinicalDecisionRules/                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Rule.php ─── RuleManager.php ─── CdrAlertManager.php        │
│     │              │                      │                   │
│     ▼              ▼                      ▼                   │
│  RuleCriteria  RuleCriteriaFactory   Alert Types:             │
│  Types:        (creates criteria     • ActiveAlert             │
│  • age_min     from DB)              • PassiveAlert            │
│  • age_max                           • PatientReminder         │
│  • sex                               • CQM (Clinical Quality) │
│  • diagnosis                         • AMC (Automated Measure) │
│  • medication                                                  │
│  • allergy     Database Tables:                               │
│  • surgery     • clinical_rules        (rule definitions)     │
│  • lifestyle   • rule_filter           (patient filters)      │
│  • custom      • rule_target           (rule targets)         │
│                • rule_action           (triggered actions)     │
│  RuleFilters   • rule_action_item      (action details)       │
│  RuleTargets   • rule_reminder         (reminder config)      │
│  RuleAction    • clinical_rules_log    (audit trail)          │
│                • clinical_plans_rules  (plan-rule mapping)    │
│                                                               │
│  US Regulation 170.315(b)(11) Compliance:                    │
│  • bibliographic_citation                                     │
│  • developer, funding_source                                  │
│  • release_date, revision_date                                │
│  • patient_demographic_usage                                  │
└─────────────────────────────────────────────────────────────┘
```

**Relevance:** Database schema can be studied for designing emergency protocol data models. The Filter → Target → Action pipeline with criteria types provides a proven architecture for rule-based decision support that could be adapted for VR emergency protocols.

### D.3 OpenMRS Program Workflow System

| Field | Detail |
|---|---|
| **Full Name** | OpenMRS ProgramWorkflow System |
| **Organization** | OpenMRS Inc. |
| **Domain** | Open-source medical records for developing countries |
| **Format** | Java source code, MySQL/PostgreSQL database |
| **Machine-Readable?** | ✅ **Yes** — workflow states with initial/terminal flags, state transitions |
| **Branching Logic?** | ✅ Yes — `ProgramWorkflow` → `ProgramWorkflowState` with `isLegalTransition()` |
| **License** | Mozilla Public License 2.0 (MPL 2.0) with Healthcare Disclaimer |
| **URL** | https://github.com/openmrs/openmrs-core , https://openmrs.org/ |
| **AI Training Notes** | 8,000+ facilities, 70+ countries, 15 million patient records. FHIR and REST APIs. |

**Key Classes for Protocol State Machines (from GitHub source analysis):**

| Class | Purpose | Emergency Protocol Relevance |
|---|---|---|
| `Program` | Contains collection of workflows | → Protocol suite (e.g., "MCI Response") |
| `ProgramWorkflow` | Manages set of states with transitions | → Individual protocol (e.g., "SALT Triage") |
| `ProgramWorkflowState` | State with `initial` and `terminal` flags | → Triage category (Immediate, Delayed, Minor, Dead) |
| `ProgramWorkflowService` | CRUD for programs, workflows, states, patient states | → Protocol management API |
| `ConceptStateConversion` | Automated state transitions based on concepts | → Auto-triage based on assessment findings |
| `LogicService` | Rule evaluation engine with criteria parsing | → Clinical decision support rules |
| `Rule` (interface) | `eval(LogicContext, patientId, parameters)` | → Protocol rule evaluation |

**`getPossibleNextStates()`** — Returns legal transitions from current state, implementing a finite state machine that maps directly to protocol decision trees.

**`isLegalTransition()`** — Validates state changes, preventing protocol violations (e.g., skipping triage steps).

### D.4 BioPortal Emergency/Trauma Ontologies

| Field | Detail |
|---|---|
| **Full Name** | NCBO BioPortal — Biomedical Ontology Repository |
| **Organization** | National Center for Biomedical Ontology (NCBO), Stanford University |
| **Domain** | Biomedical ontologies including emergency medicine, trauma, triage |
| **Format** | OWL, OBO, SKOS, RDF (standard ontology formats) |
| **Machine-Readable?** | ✅ **Yes** — formal ontology languages with SPARQL query support |
| **Branching Logic?** | ✅ Yes — ontological class hierarchies with IS-A and other formal relationships |
| **License** | Varies by ontology (most open for academic use) |
| **URL** | https://bioportal.bioontology.org/ontologies |
| **AI Training Notes** | Massive repository with 1,000+ ontologies. BioPortal provides REST API for programmatic access. |

**Emergency-Relevant Ontologies Identified:**

| Ontology | Code | Size | Description | URL |
|---|---|---|---|---|
| **Emergency Care Ontology** | ONTOLURGENCES | 10,031 classes | Emergency care concepts from LERUDI project | [BioPortal](https://bioportal.bioontology.org/ontologies/ONTOLURGENCES) |
| **Emergency Department Ontology** | EDONTOLOGY | 271 classes + 413 instances | Information logistics for emergency department operations | [BioPortal](https://bioportal.bioontology.org/ontologies/EDONTOLOGY) |
| **Healthcare Monitoring & Emergency Response** | HERO | 1,205 classes + 140 instances | Wearable devices + semantic web for vital signs monitoring and emergency alerts | [BioPortal](https://bioportal.bioontology.org/ontologies/HERO) |
| **Ontology of Trauma Center Structures** | OOSTT | 823 classes + 22 instances | OWL2 representation of trauma centers and trauma systems | [BioPortal](https://bioportal.bioontology.org/ontologies/OOSTT) |
| **Syndromic Surveillance Ontology** | SSO | 176 classes + 158 instances | ED chief complaint grouping into syndromes of public health importance | [BioPortal](https://bioportal.bioontology.org/ontologies/SSO) |
| **Nurse Triage Ontology** | TRIAGE | (listed) | Triage-related terminology and classification | [BioPortal](https://bioportal.bioontology.org/ontologies/TRIAGE) |
| **Patient Safety Ontology** | PSO | 567 classes | Includes PRIME (Prospective Risk Analysis in Medical Environments) | [BioPortal](https://bioportal.bioontology.org/ontologies/PSO) |
| **Injury Process Description** | IPD | 8 classes + 5 instances | Host, vector, agent, environment, consequences of product injuries | [BioPortal](https://bioportal.bioontology.org/ontologies/IPD) |
| **Illness & Injury Classification** | ILLNESSINJURY | 21 classes + 145 instances | Abbreviated WHO ICD-10-SMoL | [BioPortal](https://bioportal.bioontology.org/ontologies/ILLNESSINJURY) |
| **Falls Prevention** | FALLS | 30 classes + 17 instances | Fall risk assessment | [BioPortal](https://bioportal.bioontology.org/ontologies/FALLS) |
| **SNOMED CT (US Edition)** | SNOMEDCT | 375,783 classes | Core clinical terminology for EHR — comprehensive medical concepts | [BioPortal](https://bioportal.bioontology.org/ontologies/SNOMEDCT) |

**Special Note — ONTOLURGENCES (Emergency Care Ontology):** With 10,031 classes dedicated to emergency care, this is the most directly relevant ontology for the thesis. Investigate whether it covers triage classification, emergency procedures, equipment, patient assessment categories, and disposition decisions.

### D.5 SNOMED CT for Emergency Medicine

| Field | Detail |
|---|---|
| **Full Name** | SNOMED CT (Systematized Nomenclature of Medicine — Clinical Terms) |
| **Organization** | SNOMED International (US Edition maintained by NLM) |
| **Domain** | Comprehensive clinical terminology standard |
| **Format** | RF2 (Release Format 2) — tab-delimited files with concept IDs, descriptions, and relationships |
| **Machine-Readable?** | ✅ **Yes** — fully machine-readable with formal IS-A hierarchies and relationships |
| **Branching Logic?** | ✅ Yes — IS-A hierarchies, finding-site, causative-agent, and many other formal relationships |
| **License** | Free in SNOMED International member countries (incl. US); Affiliate License required for others |
| **URL** | https://bioportal.bioontology.org/ontologies/SNOMEDCT |
| **AI Training Notes** | 375,783+ concepts in US Edition. Emergency-relevant hierarchies include: Clinical Finding (404684003), Procedure (71388002), Body Structure (123037004), Event (272379006). Can extract emergency-specific subsets by navigating IS-A hierarchies. Used in HL7 FHIR PlanDefinition for goal descriptions and condition coding. **Essential for standardized emergency terminology in AI systems** — provides the universal "language" that connects all other data sources. |

---

## GitHub Repository Search Results

### Dedicated Emergency Protocol Repository Search

| Search Query | Repos Found | Code Results | Analysis |
|---|---|---|---|
| "emergency protocol decision tree" | 0 repos | 6K commits, 721 PRs | Work exists embedded in larger systems, not standalone |
| "triage algorithm JSON" | 1 repo | Low relevance | `sdelao/Superman-woman---Programming-Guru-Needed-` — not directly useful |
| "EMS protocol structured data" | 0 repos | 12K commits | Suggests integration into EHR/EMR systems |
| "SALT triage implementation" | 0 repos | 587 PRs, 415 issues | Interest exists but no dedicated implementation |

### Code Found in Major Repositories

| Repository | Component Found | Description | License |
|---|---|---|---|
| `openemr/openemr` | `src/ClinicalDecisionRules/` | Full rule engine: Rule → Filter → Target → Action with criteria types (age, sex, diagnosis, medication, allergy, surgery, lifestyle) | GPL-3.0 |
| `openmrs/openmrs-core` | `ProgramWorkflow` system | State machine: Program → Workflow → State with `isLegalTransition()`, `getPossibleNextStates()`, initial/terminal flags | MPL-2.0 |
| `openmrs/openmrs-core` | `LogicService` + `Rule` interface | Logic evaluation engine with criteria parsing, patient cohort evaluation | MPL-2.0 |

### Key Finding

**No dedicated open-source repository exists for emergency protocols in structured, machine-readable formats.** This represents a significant gap and a strong opportunity for the thesis contribution. The structured protocol work exists primarily:

1. **Embedded in larger EMR/EHR systems** (OpenEMR CDR, OpenMRS Workflows)
2. **As commits/PRs in clinical projects** rather than standalone repositories
3. **In proprietary systems** (MPDS/ProQA, AHA algorithms, ATLS)
4. **As PDF documents** requiring manual conversion (TCCC, C-TECC, SALT, START)

---

## Summary: AI Training Readiness Matrix

| # | Source | Machine-Readable | Branching Logic | Open License | API Available | **AI Score** |
|---|---|---|---|---|---|---|
| **Tier 1: Direct AI Ingestion** |
| B.3 | FEMA Disaster Declarations API | ✅ JSON | ⚠️ Classification | ✅ Public domain | ✅ REST API | ⭐⭐⭐⭐⭐ |
| D.1 | HL7 FHIR PlanDefinition | ✅ JSON/XML | ✅ Extensive | ✅ CC0 | ✅ FHIR API | ⭐⭐⭐⭐⭐ |
| B.1 | NTSB CAROL Database | ✅ Access/SQL | ⚠️ Causal factors | ✅ Public domain | ✅ Query tool | ⭐⭐⭐⭐⭐ |
| C.4 | NEMSIS Research Dataset | ✅ Structured | ✅ Intervention sequences | ✅ Free for research | ⚠️ Request-based | ⭐⭐⭐⭐⭐ |
| **Tier 2: Programmatic Access** |
| B.5 | EM-DAT | ✅ Tabular | ✅ Hierarchical | ⚠️ Non-commercial | ✅ Data portal | ⭐⭐⭐⭐ |
| D.2 | OpenEMR CDR Engine | ✅ MySQL/PHP | ✅ Rule engine | ✅ GPL-3 | ❌ Code-level | ⭐⭐⭐⭐ |
| B.2 | NFIRS/NERIS | ✅ XML/Structured | ✅ Classification tree | ✅ Public domain | ⚠️ Limited | ⭐⭐⭐⭐ |
| D.3 | OpenMRS Workflows | ✅ Java/MySQL | ✅ State machine | ✅ MPL-2 | ✅ REST/FHIR | ⭐⭐⭐⭐ |
| D.4 | BioPortal Ontologies | ✅ OWL/RDF | ✅ Class hierarchies | ⚠️ Varies | ✅ REST API | ⭐⭐⭐⭐ |
| D.5 | SNOMED CT | ✅ RF2 | ✅ IS-A hierarchies | ⚠️ Member countries | ✅ API | ⭐⭐⭐⭐ |
| B.4 | ReliefWeb / HDX | ✅ JSON/CSV | ❌ Narrative | ✅ Open data | ✅ REST API | ⭐⭐⭐ |
| C.3 | Crisis NLP Datasets | ✅ CSV/JSON | ❌ Classification | ⚠️ Research-only | ❌ Download | ⭐⭐⭐ |
| **Tier 3: Manual Conversion Required** |
| C.1 | MPDS/ProQA | ✅ (internal) | ✅ 33 protocols | ❌ Proprietary | ❌ | ⭐⭐⭐ |
| A.1 | TCCC Guidelines | ❌ PDF/image | ✅ MARCH algorithm | ✅ Public domain | ❌ | ⭐⭐ |
| A.3 | C-TECC Guidelines | ❌ PDF | ✅ Phase-based | ✅ Free access | ❌ | ⭐⭐ |
| C.2 | LDC Corpora | ✅ Audio/text | ❌ Raw conversation | ⚠️ Membership | ❌ | ⭐⭐ |
| B.6 | CDC MMWR | ⚠️ HTML | ❌ Narrative | ✅ Public domain | ❌ | ⭐⭐ |
| A.4 | WHO EMT Standards | ❌ PDF | ⚠️ Tier criteria | ⚠️ CC BY-NC-SA | ❌ | ⭐ |
| A.5 | FAA Handbooks | ⚠️ PDF | ✅ Checklists | ✅ Public domain | ❌ | ⭐⭐ |

---

## Thesis Contribution Opportunity

### The Gap

No open-source repository exists that converts well-known emergency protocols (TCCC MARCH, SALT Triage, START, MPDS dispatch, ICS checklists) into machine-readable, FHIR-compatible decision trees.

### The Bridge Your Thesis Can Build

```
┌─────────────────────┐      ┌────────────────────┐      ┌─────────────────────┐
│  SOURCE PROTOCOLS    │      │  YOUR THESIS        │      │  VR EXECUTION       │
│  (Human-readable)    │──────│  (The Bridge)       │──────│  (Machine-driven)   │
├─────────────────────┤      ├────────────────────┤      ├─────────────────────┤
│                     │      │                    │      │                     │
│ • TCCC algorithm    │      │ FHIR PlanDefinition│      │ Unity/Unreal engine │
│   cards (PDF)       │      │ + SNOMED CT coding │      │ consumes JSON       │
│ • C-TECC guidelines │      │                    │      │ decision trees      │
│   (PDF)             │ ──▶  │ Protocol Converter │ ──▶  │                     │
│ • SALT/START triage │      │ (your tool/method) │      │ State machine       │
│   (flowchart)       │      │                    │      │ drives scenarios    │
│ • ICS checklists    │      │ Validated against  │      │                     │
│   (fillable PDF)    │      │ NEMSIS outcomes    │      │ BioPortal ontology  │
│ • OSHA procedures   │      │                    │      │ provides semantic   │
│   (regulatory text) │      │ Enriched with      │      │ understanding       │
│ • MPDS logic        │      │ EM-DAT/FEMA data   │      │                     │
│   (proprietary ref) │      │ for scenarios      │      │ Trainee evaluated   │
│                     │      │                    │      │ against protocol    │
└─────────────────────┘      └────────────────────┘      └─────────────────────┘
```

### Recommended Architecture

```
VR Training System Architecture
================================

Layer 1: Protocol Knowledge Base
  ├── FHIR PlanDefinition instances (JSON)
  │   ├── Triage protocols (SALT, START, JumpSTART)
  │   ├── Treatment protocols (TCCC MARCH, C-TECC)
  │   ├── HAZMAT protocols (ERG lookup, HAZWOPER levels)
  │   └── ICS procedures (command structure, forms workflow)
  ├── SNOMED CT coded terminology
  ├── BioPortal ontology references (ONTOLURGENCES, HERO, EDONTOLOGY)
  └── Rule engine (inspired by OpenEMR CDR / OpenMRS Workflow patterns)

Layer 2: Scenario Engine
  ├── EM-DAT disaster patterns → scenario templates
  ├── FEMA declarations API → realistic disaster parameters
  ├── NTSB causal factors → incident complexity
  ├── NEMSIS outcomes → validation benchmarks
  └── Crisis NLP data → realistic communication feeds

Layer 3: VR Execution
  ├── Unity/Unreal consumes FHIR JSON protocols
  ├── State machine (modeled after OpenMRS ProgramWorkflow)
  ├── Real-time protocol compliance evaluation
  └── Branching feedback based on decision correctness

Layer 4: Assessment
  ├── Protocol adherence scoring
  ├── Critical failure identification
  ├── Time-to-decision metrics
  └── After-action report generation
```

### Novel Contributions

1. **Protocol Conversion Methodology** — Systematic method for converting PDF-based emergency protocols into FHIR PlanDefinition JSON resources
2. **Emergency Protocol Repository** — First open-source collection of emergency protocols in machine-readable format
3. **VR-FHIR Integration** — Framework for consuming FHIR clinical protocols in VR game engines
4. **Scenario Generation Pipeline** — Data-driven approach using EM-DAT + FEMA + NEMSIS for realistic VR training scenarios
5. **Protocol Compliance Engine** — State machine–based evaluation of trainee actions against formalized protocol decision trees

---

*Research compiled from web fetches across 30+ URLs, GitHub repository code analysis (OpenEMR, OpenMRS), and BioPortal ontology search.*  
*Sources that could not be accessed: OSHA pages (403), FEMA lessons learned (404), NIST fire reports (404), NIOSH FFFIPP (extraction failed), Priority Dispatch/MPDS (extraction failed), Army TC 4-02.1 (wrong content returned).*
