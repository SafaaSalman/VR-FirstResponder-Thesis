# Emergency Response Protocol Datasets & Guideline Repositories
## Research Report for VR AI Procedural Trainer Development
### Generated: 2026-03-03

---

## Table of Contents
1. [Focus Area 1: EMS / EMT / Triage Protocols](#focus-area-1-ems--emt--triage-protocols)
2. [Focus Area 2: Mass Casualty Incident (MCI) Protocols](#focus-area-2-mass-casualty-incident-mci-protocols)
3. [Focus Area 3: Clinical Protocols (ACLS, ATLS, BLS, PALS)](#focus-area-3-clinical-protocols-acls-atls-bls-pals)
4. [Focus Area 4: Firefighting Operational SOPs](#focus-area-4-firefighting-operational-sops)
5. [Focus Area 5: Incident Command System (ICS) Protocols](#focus-area-5-incident-command-system-ics-protocols)
6. [Focus Area 6: HAZMAT Response](#focus-area-6-hazmat-response)
7. [Focus Area 7: Search and Rescue](#focus-area-7-search-and-rescue)
8. [Focus Area 8: Disaster Evacuation & Civil Defense](#focus-area-8-disaster-evacuation--civil-defense)
9. [Supplementary Sources](#supplementary-sources)
10. [Summary Comparison Matrix](#summary-comparison-matrix)
11. [Recommendations for AI Training Pipeline](#recommendations-for-ai-training-pipeline)

---

## Focus Area 1: EMS / EMT / Triage Protocols

### 1.1 NEMSIS — National EMS Information System (v3.5.1)

| Field | Details |
|---|---|
| **Full Name** | National EMS Information System (NEMSIS) Data Standard v3.5.1 |
| **Hosting Organization** | NEMSIS TAC (University of Utah), funded by NHTSA Office of EMS |
| **Domain** | EMS data collection, patient care reporting, system-level analytics |
| **Format** | **XSD (XML Schema Definitions)**, XML, PDF data dictionaries, TXT element enumerations, HTML web APIs, JSON-compatible REST APIs |
| **Machine-Readable** | ✅ **YES** — Fully machine-readable. XSDs define the complete schema. Element enumerations and data dictionaries are available as structured TXT files. REST APIs are documented. |
| **Decision Trees / Branching Logic** | ❌ Not directly — NEMSIS is a *data standard*, not a protocol. However, it defines the *vocabulary* and *data elements* that protocol-driven EMS care generates (e.g., triage categories, interventions, vitals, medications, procedures). |
| **Licensing** | 🟢 **Public domain / Open** — Freely downloadable. Public-release research datasets available upon request. |
| **Direct URLs** | |
| | • Homepage: https://nemsis.org/ |
| | • Data Dictionaries & XSD: https://nemsis.org/technical-resources/version-3/version-3-data-dictionaries/ |
| | • v3.5.1 XSD download: https://nemsis.org/media/nemsis_v3/release-3.5.1/XSDs/NEMSIS_XSDs.zip |
| | • v3.5.1 Data Dictionary (PDF): https://nemsis.org/media/nemsis_v3/release-3.5.1/DataDictionary/PDFHTML/EMSDEMSTATE/NEMSISDataDictionary.pdf |
| | • v3.5.1 Data Dictionary (Web): https://nemsis.org/media/nemsis_v3/release-3.5.1/DataDictionary/PDFHTML/EMSDEMSTATE/index.html |
| | • Element Enumerations (TXT): https://nemsis.org/media/nemsis_v3/release-3.5.1/DataDictionary/Ancillary/DEMEMS/Combined_ElementEnumerations.txt |
| | • EMS API: https://nemsis.org/media/nemsis_v3/release-3.5.1/DataDictionary/APIs/EMSDataSetAPI/EMSDataSet_v3.html |
| | • GIT Repository: https://git.nemsis.org/ |
| | • Request Research Data: https://nemsis.org/request-research-data/ |
| | • 2024 Public-Release Research Dataset: https://nemsis.org/2024-nemsis-public-release-research-dataset-now-available/ |
| **AI Training Suitability** | **HIGH** — The XSD schemas can be parsed to build ontologies / knowledge graphs of EMS concepts. The enumerated value sets provide controlled vocabularies for NLP. The public-release research dataset (11M+ patient care records/year) is ideal for supervised fine-tuning of triage/treatment prediction models. Can be used to generate realistic VR scenario data. The structured XML format maps well to knowledge graphs and rule engines. |

**Key Resources within NEMSIS:**
- **EMS Dataset XSDs** — Complete XML schema for patient care records, demographic data, and state-level data
- **Element Enumerations** — Controlled vocabulary lists (medications, procedures, impressions, triage categories)
- **REST APIs** — Programmatic access definitions
- **Public-Release Research Dataset (2024)** — Largest publicly available EMS dataset in the US (~11.5M PCRs/year from 13,225+ agencies)

---

### 1.2 SALT Triage Algorithm

| Field | Details |
|---|---|
| **Full Name** | SALT Mass Casualty Triage Algorithm (Sort, Assess, Lifesaving Interventions, Treatment/Transport) |
| **Hosting Organization** | HHS/ASPR via CHEMM; endorsed by ACEP, ACS-COT, ATS, NAEMSP, NDLSEC, STIPDA |
| **Domain** | Mass casualty incident triage — field-level patient sorting |
| **Format** | **PNG image** (flowchart), **PDF** (printable), HTML text version available |
| **Machine-Readable** | ⚠️ **PARTIAL** — Flowchart is an image (needs OCR/manual digitization). A text version exists at CHEMM. The algorithm itself is well-defined and can be manually encoded. |
| **Decision Trees / Branching Logic** | ✅ **YES** — SALT is fundamentally a two-phase decision tree: (1) Global Sorting → walk/wave/still, (2) Individual Assessment → decision nodes based on breathing, pulse, obey commands → assigns Immediate/Delayed/Minimal/Expectant/Dead |
| **Licensing** | 🟢 **Public domain** — Published in peer-reviewed literature (Disaster Med Public Health Prep, 2008). Government-hosted (HHS). |
| **Direct URLs** | |
| | • SALT Algorithm (CHEMM): https://chemm.hhs.gov/salttriage.htm |
| | • SALT Image: https://chemm.hhs.gov/chemmimages/salt.png |
| | • SALT on REMM: https://remm.hhs.gov/salttriage.htm |
| | • Original Paper: https://pubmed.ncbi.nlm.nih.gov/19050431/ |
| **AI Training Suitability** | **VERY HIGH** — Compact, well-defined decision tree that maps directly to a finite state machine (FSM). Ideal for: rule engines, reinforcement learning reward functions, prompt-based evaluation rubrics, VR scenario branching logic. Can be encoded as JSON decision tree. Approximately 8-10 decision nodes. The two-phase structure (global sort → individual assessment) maps well to VR simulation phases. |

**SALT Algorithm Structure (for encoding):**
```
Phase 1: Global Sorting
  → Can walk? → MINIMAL (Green)
  → Can wave/make purposeful movement? → DELAYED assessment priority
  → Still/obvious life threat? → IMMEDIATE assessment priority

Phase 2: Individual Assessment (for non-walkers)
  → Breathing? 
    → No → Open airway → Breathing now? 
      → No → DEAD (Black)
      → Yes → IMMEDIATE (Red)
    → Yes → Obeys commands OR has pulse? 
      → No → EXPECTANT (Gray/Blue)
      → Yes → Major hemorrhage controlled? Life-saving interventions needed?
        → Yes → IMMEDIATE (Red)
        → Injuries? → DELAYED (Yellow) or MINIMAL (Green)
```

---

### 1.3 START Triage Algorithm (Adult)

| Field | Details |
|---|---|
| **Full Name** | START Adult Triage Algorithm (Simple Triage and Rapid Treatment) |
| **Hosting Organization** | HHS/ASPR via CHEMM; originally developed by Newport Beach Fire Dept. & Hoag Hospital (1983) |
| **Domain** | Mass casualty incident triage — most commonly used MCI triage algorithm in the US |
| **Format** | **GIF image** (flowchart), **PDF** (98 KB printable), **HTML text version** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Flowchart is an image. Text version available. Algorithm is simple enough to manually encode in ~10 decision nodes. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Pure binary/ternary decision tree based on: ability to walk, respiration rate, perfusion (radial pulse), mental status |
| **Licensing** | 🟢 **Public domain** — Government-hosted, originally from public fire department training materials |
| **Direct URLs** | |
| | • START Algorithm (CHEMM): https://chemm.hhs.gov/startadult.htm |
| | • PDF Download: https://chemm.hhs.gov/StartAdultTriageAlgorithm.pdf |
| | • Text Version: https://chemm.hhs.gov/startalgotext.htm |
| | • Algorithm Image: https://chemm.hhs.gov/chemmimages/StartAdultTriageAlgorithm.gif |
| | • REMM mirror: https://remm.hhs.gov/startadult.htm |
| | • Original source: https://www.cert-la.com/downloads/education/english/start.pdf |
| **AI Training Suitability** | **VERY HIGH** — The simplest and most widely used triage algorithm. ~6 decision nodes. Perfect for FSM encoding, RL environment design, beginner VR scenarios. Can be encoded as JSON in minutes. Ideal baseline for triage training AI. Modified Benson version (1996) substituted radial pulse for capillary refill. |

**START Decision Tree:**
```
Can walk? → YES → MINOR (Green)
Can walk? → NO →
  Breathing? → NO → Open airway → Breathing now?
    → NO → DEAD/EXPECTANT (Black)
    → YES → IMMEDIATE (Red)
  Breathing? → YES →
    Respiratory Rate > 30? → YES → IMMEDIATE (Red)
    Respiratory Rate ≤ 30? →
      Radial Pulse absent (or CRT > 2s)? → YES → IMMEDIATE (Red)
      Radial Pulse present →
        Can follow commands? → NO → IMMEDIATE (Red)
        Can follow commands? → YES → DELAYED (Yellow)
```

---

### 1.4 JumpSTART Pediatric Triage Algorithm

| Field | Details |
|---|---|
| **Full Name** | JumpSTART Pediatric Mass Casualty Triage Algorithm |
| **Hosting Organization** | HHS/ASPR via CHEMM; developed by Dr. Lou Romig at Miami Children's Hospital (1995, modified 2001) |
| **Domain** | Pediatric mass casualty triage |
| **Format** | **GIF image** (flowchart), **PDF** (68 KB), **HTML text version** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Same as START; image-based but simple enough to encode manually |
| **Decision Trees / Branching Logic** | ✅ **YES** — Modified START tree with pediatric-specific adjustments (e.g., 5 rescue breaths intervention, respiratory rate 15-45 normal range) |
| **Licensing** | 🟢 **Public domain** — Government-hosted |
| **Direct URLs** | |
| | • JumpSTART (CHEMM): https://chemm.hhs.gov/startpediatric.htm |
| | • PDF: https://chemm.hhs.gov/StartPediatricTriageAlgorithm.pdf |
| | • Text Version: https://chemm.hhs.gov/jumpstartalgotext.htm |
| | • Image: https://chemm.hhs.gov/chemmimages/StartPediatricTriageAlgorithm.gif |
| | • Original Paper: https://pubmed.ncbi.nlm.nih.gov/12141119/ |
| **AI Training Suitability** | **VERY HIGH** — Companion to START for pediatric scenarios. Adds ~2 additional decision nodes (rescue breaths, age-adjusted vital signs). Essential for comprehensive triage VR training. Encodes to FSM/decision tree easily. |

---

### 1.5 NHTSA National EMS Education Standards

| Field | Details |
|---|---|
| **Full Name** | National EMS Education Standards |
| **Hosting Organization** | NHTSA Office of EMS (EMS.gov) |
| **Domain** | Competency standards for EMR, EMT, AEMT, and Paramedic education |
| **Format** | **PDF** (large document) |
| **Machine-Readable** | ❌ **NO** — PDF text document. Would need NLP extraction to structure. |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — Contains competency matrices and learning objectives organized by topic area, which define procedural knowledge trees |
| **Licensing** | 🟢 **Public domain** — US Government document |
| **Direct URLs** | |
| | • PDF: https://www.ems.gov/assets/National-EMS-Education-Standards-FINAL-Jan-2009.pdf |
| | • Education resources: https://www.ems.gov/resources/search?category=education |
| | • Evidence-based guidelines: https://www.ems.gov/resources/search/category/evidence-based-guidelines |
| **AI Training Suitability** | **MEDIUM-HIGH** — Defines the knowledge domain and competency requirements. Excellent for building curriculum-aligned evaluation rubrics. Can structure learning objectives into knowledge graphs. Useful for prompt-based evaluation ("Does the trainee demonstrate EMT-level competency in airway management?"). The competency matrix structure can seed scenario generation. |

---

### 1.6 NREMT Certification Examination Content & Skill Sheets

| Field | Details |
|---|---|
| **Full Name** | National Registry of EMTs — Certification Examination Test Plans, Sample Packets, and Psychomotor Skill Sheets |
| **Hosting Organization** | National Registry of Emergency Medical Technicians (NREMT) |
| **Domain** | EMT/Paramedic psychomotor skill evaluation, cognitive examination domains |
| **Format** | **PDF** (test plans, sample packets), **HTML** (interactive sample items), structured examination domain tables |
| **Machine-Readable** | ⚠️ **PARTIAL** — Test plan domain percentages are tabular. Sample items are interactive web-based. Skill sheets are PDFs with step-by-step checklists. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Psychomotor skill sheets are sequential checklists with pass/fail branch points (critical criteria). Examination uses Computerized Adaptive Testing (CAT) with algorithmic item selection. |
| **Licensing** | 🟡 **Restricted** — NREMT owns content. Test plans are public. Actual exam content and skill sheets are proprietary. Sample items/packets are freely available for educational purposes. |
| **Direct URLs** | |
| | • BLS Examination Info: https://www.nremt.org/Pages/Examinations/EMR-and-EMT-Certification-Examinations |
| | • ALS Examination Info: https://www.nremt.org/Pages/Examinations/AEMT-and-Paramedic-Certification-Examinations |
| | • EMR Test Plan: https://www.nremt.org/admin/getmedia/4657d30a-a955-43af-aa8f-a92388f0d9f4/EMR-Test-Plan_Public |
| | • EMT Test Plan: https://www.nremt.org/admin/getmedia/4cb170ab-35fa-4ec0-a76c-634847005bc4/EMT-Test-Plan_Public |
| | • EMR Sample Packet: https://www.nremt.org/admin/getmedia/c35a3738-30df-4d43-81c8-52035ca536a8/emr_sample_packet_final-11-20-2024 |
| | • EMT Sample Packet: https://www.nremt.org/admin/getmedia/e9aef682-a401-4d47-a6d9-586580b25d02/emt_sample_packet_final-11-25-2024 |
| | • EMR Interactive Samples: http://emr-sampleitems.startpractice.com/ |
| | • EMT Interactive Samples: http://emt-sampleitems.startpractice.com/ |
| | • Handbooks: https://www.nremt.org/Pages/Handbook/Handbook-Landing |
| **AI Training Suitability** | **HIGH** — Test plan domains provide the evaluation framework structure. Domain percentages map to training emphasis. Skill sheet checklists (when obtained) are directly encodable as sequential FSMs with critical failure points — ideal for VR step-by-step procedure evaluation. The examination domains are: Scene Size-Up & Safety (15-19%), Primary Assessment (39-43%), Secondary Assessment (5-9%), Patient Treatment & Transport (20-24%), Operations (10-14%). |

**NREMT EMT Examination Domains (2025 Update):**
| Content Domain | % of Examination |
|---|---|
| Scene Size-Up and Safety | 15% – 19% |
| Primary Assessment | 39% – 43% |
| Secondary Assessment | 5% – 9% |
| Patient Treatment and Transport | 20% – 24% |
| Operations | 10% – 14% |

---

### 1.7 NASEMSO National Model EMS Clinical Guidelines

| Field | Details |
|---|---|
| **Full Name** | National Model EMS Clinical Guidelines (NASEMSO) |
| **Hosting Organization** | National Association of State EMS Officials (NASEMSO) |
| **Domain** | Model clinical protocols for prehospital EMS care — designed for adoption/adaptation by states |
| **Format** | **PDF** (comprehensive guideline document) |
| **Machine-Readable** | ❌ **NO** — PDF format. Requires NLP extraction. However, protocols are organized systematically by chief complaint / condition with clear algorithmic structures. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Each guideline contains structured protocols with assessment criteria, treatment algorithms, medication dosing, and decision points for BLS vs. ALS interventions |
| **Licensing** | 🟡 **Semi-open** — Available to NASEMSO members; widely distributed. Individual state adaptations are typically public. Check NASEMSO for current access. |
| **Direct URLs** | |
| | • NASEMSO homepage: https://www.nasemso.org/ |
| | • Resources Library: https://www.nasemso.org/content.aspx?page_id=86&club_id=157064 |
| | • (Note: The direct project page returned a "page not found" error — the guidelines may have been reorganized on NASEMSO's ClubExpress site) |
| **AI Training Suitability** | **VERY HIGH** — These are the gold-standard model protocols used across the US. Each protocol is essentially a clinical decision tree. If digitized, they provide the complete treatment algorithm library for VR training scenarios. Covers: cardiac arrest, chest pain, respiratory distress, altered mental status, trauma, pediatrics, obstetrics, toxicology, behavioral emergencies, and more. Ideal for knowledge graphs, rule engines, and scenario generation. |

---

### 1.8 New York State EMS Protocols (NY REMAC/SEMAC)

| Field | Details |
|---|---|
| **Full Name** | New York State BLS & ALS Statewide Protocols, SEMAC Advisories |
| **Hosting Organization** | New York State Department of Health, Bureau of EMS |
| **Domain** | State-level prehospital EMS treatment protocols |
| **Format** | **PDF** documents |
| **Machine-Readable** | ❌ **NO** — PDF format with some tabular data |
| **Decision Trees / Branching Logic** | ✅ **YES** — Protocols are structured as step-by-step treatment algorithms with branching by patient presentation, BLS/ALS differentiation |
| **Licensing** | 🟢 **Public domain** — State government documents |
| **Direct URLs** | |
| | • Protocols and Advisories: https://www.health.ny.gov/professionals/ems/protocols_advisories.htm |
| | • Statewide Protocols: https://www.health.ny.gov/professionals/ems/protocolsnew.htm |
| | • SEMAC Advisories: https://www.health.ny.gov/professionals/ems/semac_advisories.htm |
| | • Bureau of EMS: https://www.health.ny.gov/professionals/ems/ |
| **AI Training Suitability** | **HIGH** — Representative example of state-level protocol implementation. Shows how national guidelines translate to actionable field protocols. Includes both BLS and ALS protocols, medication formularies, and special population considerations. Each protocol is a structured decision tree suitable for FSM encoding. |

---

### 1.9 California EMSA Guidelines

| Field | Details |
|---|---|
| **Full Name** | California Emergency Medical Services Authority Guidelines and Publications |
| **Hosting Organization** | California Emergency Medical Services Authority (EMSA) |
| **Domain** | State-level EMS guidelines, scope of practice, tactical casualty care |
| **Format** | **PDF**, **DOC/DOCX** (some documents available in editable format) |
| **Machine-Readable** | ⚠️ **PARTIAL** — PDFs, but some available as DOCX (editable) |
| **Decision Trees / Branching Logic** | ✅ **YES** — Scope of practice documents define procedural hierarchies. Tactical Casualty Care (EMSA #370) contains tactical first aid algorithms. |
| **Licensing** | 🟢 **Public domain** — State government documents |
| **Direct URLs** | |
| | • Guidelines Page: https://emsa.ca.gov/guidelines/ |
| | • Scope of Practice (EMSA #300): https://emsa.ca.gov/wp-content/uploads/sites/71/2017/10/Scope-of-Practice-Documents-Current.12.11.18.pdf |
| | • Tactical Casualty Care (EMSA #370): https://emsa.ca.gov/wp-content/uploads/sites/71/2017/07/EMSA_TCC_Tactical_First_Aid_TEMS_FRO_Guidelines_032017.pdf |
| | • Patient Decontamination (EMSA #233): https://emsa.ca.gov/wp-content/uploads/sites/71/2017/07/emsa233.pdf |
| | • PPE Guidelines (EMSA #216): https://emsa.ca.gov/wp-content/uploads/sites/71/2017/07/emsa216.pdf |
| | • DNR Guidelines (EMSA #311): https://emsa.ca.gov/wp-content/uploads/sites/71/2017/07/DNRGuidelines_2018.pdf |
| | • EMS Operations & Communications (EMSA #145): https://emsa.ca.gov/wp-content/uploads/sites/71/2020/02/Comm-Manual-Update-hw-072419-new-format.pdf |
| **AI Training Suitability** | **MEDIUM-HIGH** — Provides California-specific implementation of EMS protocols. The Tactical Casualty Care document (EMSA #370) is particularly valuable for VR disaster/active threat scenarios. Patient Decontamination (#233) useful for HAZMAT VR scenarios. The DOCX versions are easier to parse programmatically. |

---

### 1.10 NAEMSP Position Statements & Prehospital Guidelines Consortium

| Field | Details |
|---|---|
| **Full Name** | NAEMSP Position Statements and Prehospital Guidelines Consortium |
| **Hosting Organization** | National Association of EMS Physicians (NAEMSP) |
| **Domain** | Evidence-based position statements on prehospital emergency medical care |
| **Format** | **PDF** (published papers), **HTML** web content |
| **Machine-Readable** | ❌ **NO** — Academic paper format |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — Position statements contain clinical recommendations that can inform decision logic |
| **Licensing** | 🟡 **Mixed** — Some publicly accessible, some require membership or journal access |
| **Direct URLs** | |
| | • Position Statements: https://naemsp.org/position-statements/ |
| | • Prehospital Guidelines Consortium: https://naemsp.org/prehospital-guidelines-consortium/ |
| | • Resource Hub: https://naemsp.org/resource-hub/ |
| | • PEC Journal: https://naemsp.org/prehospital-emergency-care-journal/ |
| **AI Training Suitability** | **MEDIUM** — Provides authoritative clinical guidance that should inform protocol logic. Not directly structured for machine consumption but essential for validation of AI-generated recommendations. The Prehospital Guidelines Consortium specifically works on standardizing prehospital clinical guidelines. |

---

### 1.11 PHTLS / ITLS Protocol Structures

| Field | Details |
|---|---|
| **Full Name** | Prehospital Trauma Life Support (PHTLS) / International Trauma Life Support (ITLS) |
| **Hosting Organization** | PHTLS: NAEMT (National Association of EMTs) in cooperation with ACS-COT; ITLS: International Trauma Life Support |
| **Domain** | Prehospital trauma assessment and management protocols |
| **Format** | **Textbook** (printed), **PDF** (course materials) |
| **Machine-Readable** | ❌ **NO** — Copyrighted textbook content |
| **Decision Trees / Branching Logic** | ✅ **YES** — PHTLS uses structured assessment algorithms (primary survey XABCDE, secondary survey, ongoing assessment). ITLS similarly uses systematic assessment trees. |
| **Licensing** | 🔴 **Copyright restricted** — Commercial textbooks, course registration required. Content cannot be reproduced. |
| **Direct URLs** | |
| | • PHTLS (NAEMT): https://www.naemt.org/education/phtls |
| | • ITLS: https://www.itrauma.org/ |
| **AI Training Suitability** | **HIGH (concept), LOW (data access)** — The PHTLS XABCDE framework and systematic assessment structure are extremely valuable for VR scenario design. However, the content is copyright-protected. You can reference the *structure* (primary survey → secondary survey → ongoing) and encode the public domain concepts. The XABCDE mnemonic itself (eXsanguinating hemorrhage → Airway → Breathing → Circulation → Disability → Exposure) is widely used and can be encoded as a decision tree framework. |

---

### 1.12 EMS.gov — NHTSA Office of EMS Resources

| Field | Details |
|---|---|
| **Full Name** | NHTSA Office of EMS Resource Library |
| **Hosting Organization** | U.S. Department of Transportation, NHTSA |
| **Domain** | Federal EMS policy, guidelines, evidence-based protocols, education standards |
| **Format** | **PDF**, **HTML** |
| **Machine-Readable** | ❌ **NO** — Primarily PDFs and HTML pages |
| **Decision Trees / Branching Logic** | Varies by document |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • Homepage: https://www.ems.gov |
| | • Resources: https://www.ems.gov/resources |
| | • Evidence-Based Guidelines: https://www.ems.gov/resources/search/category/evidence-based-guidelines |
| | • Education Resources: https://www.ems.gov/resources/search?category=education |
| | • Innovation White Paper: https://www.ems.gov/assets/EMS_Innovation_White_Paper-draft.pdf |
| | • ⚠️ NOTE: Some subpages were under maintenance at time of access (2026-03-03) |
| **AI Training Suitability** | **MEDIUM** — Meta-resource that points to authoritative documents. The evidence-based guidelines section is particularly valuable for validating protocol correctness. The EMS education standards define the complete competency framework. |

---

## Focus Area 2: Mass Casualty Incident (MCI) Protocols

### 2.1 CHEMM — Chemical Hazards Emergency Medical Management

| Field | Details |
|---|---|
| **Full Name** | Chemical Hazards Emergency Medical Management (CHEMM) |
| **Hosting Organization** | HHS / ASPR / BARDA / NLM |
| **Domain** | Chemical incident emergency response — triage, syndrome identification, acute patient care, decontamination |
| **Format** | **HTML** (interactive web tool), **PDF**, **PNG/GIF** (algorithm images), **downloadable offline package** (HTML+JS+CSS, 73MB ZIP) |
| **Machine-Readable** | ⚠️ **PARTIAL** — The downloadable offline version is HTML/JS which can be parsed. CHEMM-IST is an interactive JavaScript-based tool. Algorithm images need conversion. |
| **Decision Trees / Branching Logic** | ✅ **YES — EXTENSIVE** — CHEMM contains multiple decision trees: |
| | • SALT, START, JumpSTART triage algorithms |
| | • CHEMM-IST 2.0: Interactive syndrome identification decision support (IF-THEN rules for 7 chemical syndromes) |
| | • Chemical-specific acute patient care guidelines (prehospital and ED) for: Ammonia, Chlorine, Hydrogen Cyanide, Mustard Agents, Nerve Agents (including 4th gen), Phosgene |
| | • ASPIRE decontamination algorithm |
| **Licensing** | 🟢 **Public domain** — US Government (HHS) |
| **Direct URLs** | |
| | • Homepage: https://chemm.hhs.gov/ |
| | • CHEMM-IST 2.0 (Interactive Syndromes Tool): https://chemm.hhs.gov/chemmist.htm |
| | • SALT Algorithm: https://chemm.hhs.gov/salttriage.htm |
| | • START Algorithm: https://chemm.hhs.gov/startadult.htm |
| | • JumpSTART: https://chemm.hhs.gov/startpediatric.htm |
| | • Triage Guidelines Hub: https://chemm.hhs.gov/triage.htm |
| | • Acute Patient Care Guidelines: https://chemm.hhs.gov/mmghome.htm |
| | • Chemical Categories: https://chemm.hhs.gov/agentcategories.htm |
| | • First Responders: https://chemm.hhs.gov/firstresponders.htm |
| | • Download Offline (ZIP): https://chemm.hhs.gov/CHEMM.zip?v=2.4 |
| | • Download (Windows Installer): https://chemm.hhs.gov/CHEMM_setup.exe?v=2.5 |
| | • ASPIRE Decontamination Algorithm: https://chemm.hhs.gov/aspire.htm |
| | • Nerve Agent Prehospital Guidelines: https://chemm.hhs.gov/na_prehospital_mmg.htm |
| | • Nerve Agent Hospital Guidelines: https://chemm.hhs.gov/na_hospital_mmg.htm |
| **AI Training Suitability** | **EXTREMELY HIGH** — This is one of the most valuable resources identified. Key reasons: |
| | 1. **CHEMM-IST** is already structured as an IF-THEN expert system (built from FALCON decision support system). Its decision trees can be directly extracted from the JavaScript source of the downloadable version. |
| | 2. The syndrome identification logic (7 syndromes: Knockdown, Pesticide/Cholinergic, Solvents/Anesthetics/Sedatives, Irritant Gas, Opioid, Anticholinergic, Convulsant) maps perfectly to a knowledge graph / rule engine. |
| | 3. Input features are simple BLS-level observations: vital signs, mental status, pupil size, mucous membrane irritation, lung exam, skin condition. |
| | 4. The offline downloadable package contains all HTML/JS/CSS — the JavaScript implements the decision logic and can be reverse-engineered. |
| | 5. Chemical-specific treatment protocols are structured by agent → route → severity. |
| | 6. Ideal for HAZMAT VR scenarios, chemical MCI training, and toxidrome identification training. |

---

### 2.2 REMM — Radiation Emergency Medical Management

| Field | Details |
|---|---|
| **Full Name** | Radiation Emergency Medical Management (REMM) |
| **Hosting Organization** | HHS / ASPR / BARDA |
| **Domain** | Radiation emergency response — triage, patient management, medical countermeasures |
| **Format** | **HTML** (interactive tools), **PDF** (algorithms, guidelines), **mobile app**, **downloadable offline version** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Interactive web tools are HTML/JS. Algorithms are structured as flowcharts. Mobile app available. |
| **Decision Trees / Branching Logic** | ✅ **YES — EXTENSIVE** — Contains multiple algorithm types: |
| | • Patient management algorithms (Contamination, Exposure, Exposure+Contamination, No Contamination/Exposure) |
| | • Radiation triage algorithms adapted from SALT for nuclear scenarios |
| | • Scarce Resources Triage Tool (changes triage categories over time) |
| | • EAST Tool (Exposure and Symptom Triage) |
| | • RTR (Triage-Treatment-Transport) medical response model |
| | • ARS (Acute Radiation Syndrome) management algorithms |
| | • Hospital Approach algorithm for nuclear detonation patients |
| | • Cytokine Administration Triage Guidelines |
| **Licensing** | 🟢 **Public domain** — US Government (HHS) |
| **Direct URLs** | |
| | • Homepage: https://remm.hhs.gov/ |
| | • Triage Guidelines (comprehensive): https://remm.hhs.gov/radtriage.htm |
| | • Choose Algorithm (interactive): https://remm.hhs.gov/newptinteract.htm |
| | • Contamination Algorithm: https://remm.hhs.gov/contamonly.htm |
| | • Exposure Algorithm: https://remm.hhs.gov/exposureonly.htm |
| | • Exposure + Contamination: https://remm.hhs.gov/exposurecontam.htm |
| | • Scarce Resources Triage Tool: https://remm.hhs.gov/triagetool_intro.htm |
| | • Hospital Approach Algorithm: https://remm.hhs.gov/hospitalapproach_algo.htm |
| | • Interactive Clinical Tools: https://remm.hhs.gov/interactivetools.htm |
| | • Tools & Guidelines: https://remm.hhs.gov/toolsguidelines.htm |
| | • Key Guidance Documents: https://remm.hhs.gov/keyguidancedocs.htm |
| | • EAST Tool: https://remm.hhs.gov/EAST-tool-notes.htm |
| | • Mobile App Download: https://remm.hhs.gov/downloadmremm.htm |
| | • Offline Download: https://remm.hhs.gov/download.htm |
| | • Nuclear Detonation Planning Guidance (PDF, FEMA 2022): https://remm.hhs.gov/PlanningGuidanceNuclearDetonation_2023.pdf |
| | • RITN ARS Treatment Guidelines (PDF): https://remm.hhs.gov/RITN-ARS-Treatment-Guidelines-21Oct-FINAL.pdf |
| | • RITN Cytokine Triage Guidelines: https://ritn.net/triage/ |
| | • AFRRI BAT Tool: https://afrri.usuhs.edu/research-assessment-of-radiation-injury |
| | • Medical Aspects of Radiation Incidents (PDF): https://orise.orau.gov/resources/reacts/documents/medical-aspects-of-radiation-incidents.pdf |
| **AI Training Suitability** | **EXTREMELY HIGH** — Like CHEMM, this is an expert system designed for first responders and healthcare providers. Key AI training applications: |
| | 1. The **algorithm chooser** (contamination vs. exposure vs. both) is a simple decision tree that can be directly encoded as an FSM. |
| | 2. **Scarce Resources Triage Tool** implements *dynamic* triage reassignment — ideal for RL environments where resources change over time. |
| | 3. **ARS grading** uses time-dependent clinical parameters — can train temporal reasoning models. |
| | 4. Comprehensive radiation-specific triage complements chemical (CHEMM) and trauma (START/SALT) triage. |
| | 5. Nuclear detonation planning guidance provides scenario generation parameters. |
| | 6. Mobile app and offline version contain parseable HTML/JS decision logic. |

---

### 2.3 FEMA ICS (Incident Command System) Resources

| Field | Details |
|---|---|
| **Full Name** | FEMA National Incident Management System (NIMS) / Incident Command System (ICS) Resources |
| **Hosting Organization** | FEMA Emergency Management Institute (EMI) |
| **Domain** | Incident command structure, mass casualty management, emergency operations |
| **Format** | **PDF** (ICS forms, review documents, position task books), **fillable PDF forms** |
| **Machine-Readable** | ⚠️ **PARTIAL** — ICS forms are fillable PDFs (structured fields). Position Task Books have structured checklists. |
| **Decision Trees / Branching Logic** | ✅ **YES** — ICS defines command hierarchy and decision authority trees. Position Task Books (PTBs) contain step-by-step competency checklists with prerequisite tasks. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • ICS Resource Center: https://training.fema.gov/emiweb/is/icsresource/ |
| | • ICS Review Document: https://training.fema.gov/emiweb/is/icsresource/assets/ICS%20Review%20Document.pdf |
| | • ICS Forms (fillable PDFs): https://training.fema.gov/emiweb/is/icsresource/icsforms |
| | • ICS Job Aids: https://training.fema.gov/emiweb/is/icsresource/jobaids |
| | • Position Task Books (NQS): https://www.fema.gov/national-qualification-system |
| | • Reference Documents: https://training.fema.gov/emiweb/is/icsresource/referencedocuments |
| | • Training Materials: https://training.fema.gov/emiweb/is/icsresource/trainingmaterials |
| | • Glossary: https://training.fema.gov/emiweb/is/icsresource/assets/Glossary%20of%20Related%20Terms.pdf |
| | • ⚠️ NOTE: FEMA training site was partially offline (federal funding lapse) at time of access |
| **AI Training Suitability** | **HIGH** — ICS forms define the information architecture of incident management. ICS-206 (Medical Plan), ICS-215 (Operational Planning), and others define the data structures for MCI management. Position Task Books provide structured competency checklists for each ICS role. The command hierarchy maps to organizational knowledge graphs. Directly applicable to VR command-level training scenarios. |

---

### 2.4 ASPR TRACIE — Healthcare Emergency Preparedness Information Gateway

| Field | Details |
|---|---|
| **Full Name** | ASPR TRACIE (Technical Resources, Assistance Center, and Information Exchange) |
| **Hosting Organization** | HHS Administration for Strategic Preparedness and Response (ASPR) |
| **Domain** | Healthcare emergency preparedness — disaster medicine, MCI planning, crisis standards of care |
| **Format** | **PDF** (white papers, toolkits, guidelines), **HTML** |
| **Machine-Readable** | ❌ **NO** — Primarily narrative PDFs |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — Some resources contain structured frameworks (e.g., crisis standards of care decision frameworks) |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • Homepage: https://asprtracie.hhs.gov/ |
| | • TRACIE-Developed Resources: https://asprtracie.hhs.gov/tracie-resources |
| | • Crisis Standards of Care: https://asprtracie.hhs.gov/csc |
| | • Mass Violence Resources: https://asprtracie.hhs.gov/mass-violence |
| | • Infectious Disease Resources: https://asprtracie.hhs.gov/infectious-disease |
| | • Pediatric Surge: https://asprtracie.hhs.gov/pediatric-surge |
| | • Hurricane Resources: https://asprtracie.hhs.gov/hurricane-resources |
| | • MCI Triage White Paper: https://files.asprtracie.hhs.gov/documents/aspr-tracie-mass-casualty-triage-final-508.pdf |
| | • MCI Response Toolkit (GNYHA): https://www.gnyha.org/wp-content/uploads/2019/04/MCI_Toolkit_digital.pdf |
| **AI Training Suitability** | **MEDIUM-HIGH** — Excellent meta-resource. The MCI Triage White Paper distinguishes between conventional MCI and mass violence event triage — important for scenario differentiation. Crisis Standards of Care documents provide ethical decision frameworks for scarce resource allocation — useful for advanced RL training scenarios. |

---

### 2.5 WHO Mass Casualty Management Systems

| Field | Details |
|---|---|
| **Full Name** | Mass Casualty Management Systems: Strategies and Guidelines for Building Health Sector Capacity |
| **Hosting Organization** | World Health Organization (WHO) |
| **Domain** | International mass casualty management guidelines and health sector capacity building |
| **Format** | **PDF** (book-length document) |
| **Machine-Readable** | ❌ **NO** — PDF narrative document |
| **Decision Trees / Branching Logic** | ✅ **YES** — Contains systematic mass casualty management frameworks and triage protocols |
| **Licensing** | 🟢 **Open** — WHO publications are generally available under Creative Commons IGO license |
| **Direct URLs** | |
| | • WHO Publications: https://www.who.int/publications |
| | • WHO IRIS Repository: https://iris.who.int/handle/10665/43804 |
| | • WHO Guidelines page: https://www.who.int/publications/who-guidelines |
| | • (Note: Direct link to mass-casualty-management-systems returned empty — may need search on IRIS) |
| **AI Training Suitability** | **MEDIUM** — Provides international perspective on mass casualty management. Useful for building globally-applicable training scenarios rather than US-specific ones. WHO frameworks complement domestic protocols. |

---

## Focus Area 3: Clinical Protocols (ACLS, ATLS, BLS, PALS)

### 3.1 AHA ACLS / BLS / PALS Algorithms

| Field | Details |
|---|---|
| **Full Name** | American Heart Association Guidelines for CPR and Emergency Cardiovascular Care — includes ACLS (Advanced Cardiovascular Life Support), BLS (Basic Life Support), PALS (Pediatric Advanced Life Support) |
| **Hosting Organization** | American Heart Association (AHA) |
| **Domain** | Cardiac arrest management, arrhythmia treatment, resuscitation algorithms |
| **Format** | **PDF** (guidelines documents), **HTML** (interactive guidelines website), **printed algorithm cards**, **mobile apps** |
| **Machine-Readable** | ❌ **NO** — Not available in JSON/XML format officially. The algorithms are published as flowcharts in PDF/image format. However, the 2020 (and 2025) guidelines are published at eccguidelines.heart.org. |
| **Decision Trees / Branching Logic** | ✅ **YES — CORE CONTENT** — These are the definitive algorithm flowcharts for: |
| | • Adult/Pediatric/Neonatal BLS |
| | • Adult/Pediatric Cardiac Arrest (VF/pVT, PEA, Asystole) |
| | • Bradycardia/Tachycardia |
| | • Acute Coronary Syndromes |
| | • Stroke |
| | • Post-Cardiac Arrest Care |
| | • Opioid Overdose |
| **Licensing** | 🔴 **Copyright restricted** — AHA owns all algorithm content. Guidelines are published in *Circulation* (Wolters Kluwer). Reproduction requires permission. However, the *scientific content* (evidence reviews) is publicly available. Algorithm *structure* (not exact reproduction) can be referenced. |
| **Direct URLs** | |
| | • Guidelines Hub: https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines |
| | • ECC Guidelines (interactive): https://eccguidelines.heart.org/ |
| | • 2020 Guidelines in Circulation: https://www.ahajournals.org/doi/10.1161/CIR.0000000000000916 |
| | • (Note: The AHA website redirected through ad tracking at time of access) |
| **AI Training Suitability** | **EXTREMELY HIGH (concept) / MEDIUM (access)** — These algorithms are the foundation of cardiac emergency management and are essential for any comprehensive VR emergency training system. However: |
| | 1. **Copyright barrier**: Exact flowcharts cannot be reproduced. You would need to license from AHA or create derivative works based on the published evidence. |
| | 2. **Structural value**: The BLS/ACLS/PALS algorithms are well-known and have been independently encoded by many training systems. The logic is relatively compact (~15-25 decision nodes per algorithm). |
| | 3. **JSON/XML encoding**: No official machine-readable format exists, but the algorithms have been encoded in various research projects. Consider: (a) encoding from the published literature, (b) using AHA's partner APIs if available, (c) licensing for educational use. |
| | 4. **VR application**: These algorithms drive the most common high-fidelity simulation scenarios. Cardiac arrest management is a primary VR simulation use case. |

**Note on AHA Algorithm Availability:**
While the AHA does not publish JSON/XML versions of their algorithms, the core logic of BLS/ACLS/PALS is based on publicly available evidence and widely taught. Several open-source projects have encoded similar logic:
- The decision trees can be reconstructed from the published scientific statements
- AHA Heartcode products contain interactive algorithm training
- The fundamental flow (Check responsiveness → Activate EMS → CPR → AED/Defibrillation → Medications → etc.) is public knowledge

---

### 3.2 ATLS (Advanced Trauma Life Support)

| Field | Details |
|---|---|
| **Full Name** | Advanced Trauma Life Support (ATLS) |
| **Hosting Organization** | American College of Surgeons (ACS) Committee on Trauma |
| **Domain** | Hospital-based trauma assessment and management protocols |
| **Format** | **Textbook** (printed), **course materials** (PDF) |
| **Machine-Readable** | ❌ **NO** — Copyrighted course content |
| **Decision Trees / Branching Logic** | ✅ **YES** — Primary survey (ABCDE), secondary survey, structured assessment algorithms |
| **Licensing** | 🔴 **Copyright restricted** — Commercial course, ACS proprietary |
| **Direct URLs** | |
| | • ACS ATLS: https://www.facs.org/quality-programs/trauma/education/advanced-trauma-life-support/ |
| **AI Training Suitability** | **HIGH (concept) / LOW (data access)** — The ABCDE assessment framework (Airway → Breathing → Circulation → Disability → Exposure) is universally used and can be encoded as a framework. The specific ATLS protocols are copyrighted, but the general assessment structure is public domain medical knowledge. The primary survey framework is foundational for VR trauma scenarios. |

---

## Focus Area 4: Firefighting Operational SOPs

### 4.1 NFPA 1001 — Standard for Firefighter Professional Qualifications

| Field | Details |
|---|---|
| **Full Name** | NFPA 1001: Standard for Firefighter Professional Qualifications |
| **Hosting Organization** | National Fire Protection Association (NFPA) |
| **Domain** | Firefighter I and II certification — defines minimum job performance requirements (JPRs) for structural firefighting |
| **Format** | **PDF** (standards document), **HTML** (online viewer with NFPA account), purchasable print editions |
| **Machine-Readable** | ❌ **NO** — Copyrighted standards text in PDF/print. NFPA provides free read-only online access but prohibits bulk extraction. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Each JPR defines: prerequisite knowledge → requisite skills → performance outcome. The FF-I → FF-II hierarchy is itself a branching progression. JPRs for operations (fire attack, search, ventilation, salvage) map to procedural decision trees. |
| **Licensing** | 🔴 **Copyright restricted** — NFPA copyrighted standard. Free read-only access via nfpa.org account. Reproduction prohibited. Can reference JPR numbers and structure. |
| **Direct URLs** | |
| | • NFPA 1001 Overview: https://www.nfpa.org/codes-and-standards/nfpa-1001-standard-for-firefighter-professional-qualifications |
| | • NFPA Free Access (requires account): https://www.nfpa.org/codes-and-standards/all-codes-and-standards/list-of-codes-and-standards/detail?code=1001 |
| | • NFPA Catalog: https://catalog.nfpa.org/NFPA-1001-Standard-for-Firefighter-Professional-Qualifications-P1408.aspx |
| **AI Training Suitability** | **HIGH (structure) / MEDIUM (data access)** — NFPA 1001 defines the authoritative competency framework for all US firefighter training. JPRs map directly to VR evaluation rubrics. The FF-I/FF-II progression provides scaffolded training levels. While the exact text is copyrighted, the JPR *structure* (task → conditions → standard) and JPR *numbers* can be referenced. IFSTA and Jones & Bartlett training materials implement these JPRs as step-by-step skill sheets. |

**Key NFPA 1001 JPR Areas for VR Training:**
```
Firefighter I:
  Ch 4.1 - General (PPE, SCBA, communications, building construction)
  Ch 4.2 - Fire Department Communications
  Ch 4.3 - Fireground Operations (hose, water supply, fire attack, search, ventilation, ladders, overhaul)

Firefighter II:
  Ch 5.1 - General
  Ch 5.2 - Fire Department Communications  
  Ch 5.3 - Fireground Operations (size-up, incident action plan, advanced fire attack, RIT)
```

---

### 4.2 NFPA 1500 — Fire Department Occupational Safety, Health, and Wellness Program

| Field | Details |
|---|---|
| **Full Name** | NFPA 1500: Standard on Fire Department Occupational Safety, Health, and Wellness Program |
| **Hosting Organization** | NFPA |
| **Domain** | Firefighter safety — risk management, PPE requirements, incident scene safety, wellness |
| **Format** | **PDF** / **HTML** (read-only online) |
| **Machine-Readable** | ❌ **NO** — Same as NFPA 1001 |
| **Decision Trees / Branching Logic** | ✅ **YES** — Risk management framework (risk a lot to save a lot / risk little to save little / risk nothing to save nothing). PAR (Personnel Accountability Report) procedures. MAYDAY protocols. |
| **Licensing** | 🔴 **Copyright restricted** — NFPA copyrighted, free online read access |
| **Direct URLs** | |
| | • NFPA 1500: https://www.nfpa.org/codes-and-standards/nfpa-1500-standard-on-fire-department-occupational-safety-health-and-wellness-program |
| **AI Training Suitability** | **HIGH** — Defines the safety decision framework that overlays all firefighting operations. The risk-benefit analysis model (risk a lot/little/nothing) is a foundational decision tree for VR scenarios. MAYDAY protocol, PAR system, and two-in/two-out rule are encodable procedures. |

---

### 4.3 NFPA 1561 — Standard on Emergency Services Incident Management System

| Field | Details |
|---|---|
| **Full Name** | NFPA 1561: Standard on Emergency Services Incident Management System and Command Safety |
| **Hosting Organization** | NFPA |
| **Domain** | Fire service ICS implementation — incident commander duties, command structure, safety officer role |
| **Format** | **PDF** / **HTML** (read-only) |
| **Machine-Readable** | ❌ **NO** |
| **Decision Trees / Branching Logic** | ✅ **YES** — Defines command transfer procedures, span of control thresholds (3-7 optimal), when to expand ICS, and safety officer authority to stop operations |
| **Licensing** | 🔴 **Copyright restricted** — NFPA |
| **Direct URLs** | |
| | • NFPA 1561: https://www.nfpa.org/codes-and-standards/nfpa-1561-standard-on-emergency-services-incident-management-system-and-command-safety |
| **AI Training Suitability** | **HIGH** — Directly applicable to VR incident command training. Defines when/how to transfer command, expand the organization, and make strategic vs. tactical decisions. |

---

### 4.4 NFPA 1710 — Standard for Organization and Deployment (Career Fire Departments)

| Field | Details |
|---|---|
| **Full Name** | NFPA 1710: Standard for the Organization and Deployment of Fire Suppression Operations, EMS, and Special Operations by Career Fire Departments |
| **Hosting Organization** | NFPA |
| **Domain** | Staffing, response time benchmarks, resource deployment for structural firefighting |
| **Format** | **PDF** / **HTML** (read-only) |
| **Machine-Readable** | ❌ **NO** |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — Defines response time targets (turnout ≤80s, travel ≤240s), staffing minimums (4-person companies), alarm assignment matrices by incident type |
| **Licensing** | 🔴 **Copyright restricted** — NFPA |
| **Direct URLs** | |
| | • NFPA 1710: https://www.nfpa.org/codes-and-standards/nfpa-1710-standard-for-the-organization-and-deployment-of-fire-suppression-operations-emergency-medical-operations-and-special-operations-to-the-public-by-career-fire-departments |
| **AI Training Suitability** | **MEDIUM-HIGH** — Provides the operational parameters for realistic VR scenario generation (staffing levels, response times, resource allocation). Alarm assignment matrices define which resources respond to each incident type. |

---

### 4.5 IFSTA Essentials of Fire Fighting — Skills Checklists

| Field | Details |
|---|---|
| **Full Name** | IFSTA Essentials of Fire Fighting (8th Edition) — Firefighter I and II Skill Sheets & Training Materials |
| **Hosting Organization** | International Fire Service Training Association (IFSTA) / Fire Protection Publications, Oklahoma State University |
| **Domain** | Firefighter training — step-by-step skill procedures mapped to NFPA 1001 JPRs |
| **Format** | **Textbook** (print/eBook), **PDF** skill sheets, **IFSTA Apps**, **ResourceOne® eLibrary** |
| **Machine-Readable** | ❌ **NO** — Copyrighted commercial textbook. Skill sheets are PDF checklists. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Each skill sheet is a sequential checklist with step-by-step procedures. Skills include: donning PPE, SCBA operation, hose advancement, search patterns, ladder placement, ventilation techniques, RIT activation. |
| **Licensing** | 🔴 **Copyright restricted** — Commercial product by Oklahoma State University/IFSTA. Available for purchase ($81 FF-I, sold separately). ResourceOne® subscription for departments. |
| **Direct URLs** | |
| | • IFSTA Homepage: https://www.ifsta.org/ |
| | • Essentials 8th Ed FF-I: https://www.ifsta.org/shop/essentials-fire-fighting-8th-edition-firefighter-1/37888 |
| | • IFSTA eLibrary: https://www.ifsta.org/content/ifsta-elibrary |
| | • IFSTA Apps: https://www.ifsta.org/shop/product-categories/ifsta-apps |
| **AI Training Suitability** | **HIGH (structure) / LOW (direct data access)** — IFSTA skills checklists are the de facto implementation of NFPA 1001 JPRs as step-by-step procedures. They define exact sequences for firefighting tasks. For VR training, you need these procedural sequences but would need to license or re-derive them from NFPA JPRs. The skill sheet structure (numbered steps → critical points → pass/fail criteria) maps directly to VR procedural evaluation FSMs. |

---

### 4.6 IFSAC / Pro Board Certification Skill Sheets

| Field | Details |
|---|---|
| **Full Name** | International Fire Service Accreditation Congress (IFSAC) & Pro Board Fire Service Professional Qualifications System — Certification Testing Skill Sheets |
| **Hosting Organization** | IFSAC (Oklahoma State University) / Pro Board (National Board on Fire Service Professional Qualifications) |
| **Domain** | Fire service professional certification testing — standardized skill evaluation sheets |
| **Format** | **PDF** (skill sheets, certification guides) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Structured checklists in PDF format |
| **Decision Trees / Branching Logic** | ✅ **YES** — Step-by-step skill evaluation sheets with pass/fail criteria, critical steps, and branching evaluation points |
| **Licensing** | 🟡 **Semi-open** — IFSAC publishes some test bank guidance. Pro Board test materials are distributed through accredited agencies. Individual state fire academies often publish their own adapted skill sheets publicly. |
| **Direct URLs** | |
| | • IFSAC: https://ifsac.org/ |
| | • Pro Board: https://theproboard.org/ |
| | • IFSAC Accredited Agencies: https://ifsac.org/accredited-agencies/ |
| | • (Note: Many state fire academies publish their adapted NFPA 1001 skill sheets — e.g., Texas TCFP, California State Fire Marshal, etc.) |
| **AI Training Suitability** | **HIGH** — Certification skill sheets are exactly the type of step-by-step procedures needed for VR evaluation. States often publish their adapted versions publicly. These map 1:1 to VR simulation evaluation rubrics. |

---

### 4.7 NIOSH Fire Fighter Fatality Investigation and Prevention Program (FFFIPP)

| Field | Details |
|---|---|
| **Full Name** | NIOSH Fire Fighter Fatality Investigation and Prevention Program — Line-of-Duty Death Investigation Reports |
| **Hosting Organization** | CDC/NIOSH (National Institute for Occupational Safety and Health) |
| **Domain** | Post-incident investigation of firefighter fatalities — structured root cause analysis with recommendations |
| **Format** | **HTML** (individual reports), **PDF** (downloadable reports), **searchable database** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Reports follow a consistent template (Summary, Key Recommendations, Incident Description, Contributing Factors, Recommendations). Database is searchable but not API-accessible. |
| **Decision Trees / Branching Logic** | ✅ **YES (implicit)** — Each report identifies failure points in procedures. Contributing factors map to "what should have been done" → creates negative-example decision trees. Recommendations define corrective procedural branches. |
| **Licensing** | 🟢 **Public domain** — US Government (CDC/NIOSH) |
| **Direct URLs** | |
| | • FFFIPP Home: https://www.cdc.gov/niosh/fire/ |
| | • Investigation Reports Database: https://www.cdc.gov/niosh/fire/reports/ |
| | • Search Reports: https://wwwn.cdc.gov/NIOSH-fire-fighter-face-reports/ |
| | • Summary Reports: https://www.cdc.gov/niosh/fire/default.html |
| **AI Training Suitability** | **VERY HIGH** — Unique structured dataset of what-went-wrong scenarios. Each report follows a consistent template that can be NLP-extracted. The "Contributing Factors → Recommendations" pairs directly encode corrective decision logic. Ideal for: (1) negative-example training (what NOT to do), (2) scenario generation based on real incidents, (3) reinforcement learning penalty functions, (4) procedural compliance evaluation. 400+ investigation reports spanning decades of incidents. |

**NIOSH FFFIPP Report Structure (for NLP extraction):**
```
1. Summary
2. Key Recommendations (numbered list)
3. Introduction (who, what, when, where)
4. Investigation
   4.1 Incident Description (timeline)
   4.2 Contributing Factors (bulleted)
   4.3 Cause of Death
5. Recommendations (detailed, with supporting analysis)
6. References
7. Appendices (diagrams, photos, floor plans)
```

---

### 4.8 Structural Firefighting SOPs — Standard Operating Procedures Framework

| Field | Details |
|---|---|
| **Full Name** | Structural Firefighting Standard Operating Procedures / Guidelines (Generic Framework) |
| **Hosting Organization** | Various — individual fire departments, state fire academies, IAFC, ISFSI |
| **Domain** | Operational procedures for structural fire response: size-up, entry, search, ventilation, RIT |
| **Format** | **PDF** (department SOPs), **HTML** (training resources) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Many departments publish SOPs as PDF; structure varies |
| **Decision Trees / Branching Logic** | ✅ **YES** — Size-up follows decision tree (COAL WAS WEALTH, CAN report). Offensive vs. Defensive strategy decision. Search patterns (primary/secondary). Ventilation type selection. RIT activation criteria. |
| **Licensing** | 🟢 **Generally public** — Most fire department SOPs are public records. IAFC resources often freely available. |
| **Direct URLs** | |
| | • IAFC Rules of Engagement: https://www.iafc.org/topics-and-tools/resources/resource/rules-of-engagement-for-structural-firefighting |
| | • ISFSI (International Society of Fire Service Instructors): https://www.isfsi.org/ |
| | • Phoenix FD SOPs (example large-city): https://www.phoenix.gov/fire/about/sop |
| | • FDNY Training Materials: various publications |
| | • NIOSH Preventing Deaths and Injuries to Fire Fighters: https://www.cdc.gov/niosh/docs/2009-100/ |
| **AI Training Suitability** | **VERY HIGH** — Structural firefighting SOPs contain the core procedural knowledge for VR training. Key encodable procedures: |
| | 1. **Size-Up**: COAL WAS WEALTH (Construction, Occupancy, Apparatus, Life hazard, Water supply, Area, Street conditions, Weather, Exposures, Auxiliary appliances, Location/extent of fire, Time, Height) |
| | 2. **Strategy Decision**: Offensive → Marginal → Defensive (based on risk-benefit analysis per NFPA 1500) |
| | 3. **Search Patterns**: Left-hand/right-hand wall follow, vent-enter-search |
| | 4. **Ventilation**: Horizontal vs. vertical, positive pressure vs. negative pressure, timing relative to attack |
| | 5. **RIT (Rapid Intervention Team)**: Activation criteria → deployment protocol → MAYDAY procedures |
| | 6. **CAN Report**: Conditions, Actions, Needs — standardized status reporting |

---

### 4.9 Wildland Firefighting Protocols — LCES, 10/18 Standard Fire Orders & Watch Out Situations

| Field | Details |
|---|---|
| **Full Name** | Wildland Fire Safety — Standard Fire Orders, Watch Out Situations, LCES (Lookouts, Communications, Escape Routes, Safety Zones) |
| **Hosting Organization** | National Wildfire Coordinating Group (NWCG) |
| **Domain** | Wildland firefighting safety protocols and operational procedures |
| **Format** | **PDF** (PMS publications), **HTML** (web resources), **pocket cards**, **mobile apps** |
| **Machine-Readable** | ⚠️ **PARTIAL** — The 10 Standard Fire Orders and 18 Watch Out Situations are short, well-defined lists. LCES is a structured checklist. NWCG publications are PDFs. |
| **Decision Trees / Branching Logic** | ✅ **YES** — LCES is a mandatory checklist (all 4 elements must be in place before engagement). The Fire Orders are prioritized rules. Watch Out Situations are conditional triggers ("IF situation X observed THEN reassess engagement"). Incident Response Pocket Guide (IRPG) contains operational checklists. |
| **Licensing** | 🟢 **Public domain** — US Government interagency (NWCG includes USFS, BLM, NPS, BIA, USFWS, FEMA, NASF, IAFC) |
| **Direct URLs** | |
| | • NWCG Homepage: https://www.nwcg.gov/ |
| | • NWCG Publications: https://www.nwcg.gov/publications |
| | • Incident Response Pocket Guide (IRPG, PMS 461): https://www.nwcg.gov/publications/pms461 |
| | • Wildland Fire Qualification System Guide (PMS 310-1): https://www.nwcg.gov/publications/pms310-1 |
| | • Fireline Handbook (PMS 410-1): https://www.nwcg.gov/publications/pms410-1 |
| | • Standards for Interagency Incident Business Management (PMS 902): https://www.nwcg.gov/publications/pms902 |
| | • 10 Standard Fire Orders: https://www.nwcg.gov/committee/6mfs/standard-fire-orders |
| | • 18 Watch Out Situations: https://www.nwcg.gov/committee/6mfs/watch-out-situations |
| | • LCES: https://www.nwcg.gov/committee/6mfs/lces |
| **AI Training Suitability** | **EXTREMELY HIGH** — The 10 Standard Fire Orders and 18 Watch Out Situations are compact, universally applicable safety rules that can be directly encoded as rule sets. LCES is a 4-item mandatory checklist. The IRPG contains operational checklists for every wildland fire position. This is ideal for: (1) rule-based safety evaluation in VR, (2) scenario generation (each Watch Out Situation = a scenario trigger), (3) procedural checklists for position-specific training. |

**10 Standard Fire Orders (encodable as rules):**
```
1. Keep informed on fire weather conditions and forecasts
2. Know what your fire is doing at all times
3. Base all actions on current and expected behavior of the fire
4. Identify escape routes and safety zones, and make them known
5. Post lookouts when there is possible danger
6. Be alert. Keep calm. Think clearly. Act decisively
7. Maintain prompt communications with your forces, your supervisor, and adjoining forces
8. Give clear instructions and be sure they are understood
9. Maintain control of your forces at all times
10. Fight fire aggressively, having provided for safety first
```

**18 Watch Out Situations (encodable as conditional triggers):**
```
1. Fire not scouted and sized up
2. In country not seen in daylight
3. Safety zones and escape routes not identified
4. Unfamiliar with weather and local factors influencing fire behavior
5. Uninformed on strategy, tactics, and hazards
6. Instructions and assignments not clear
7. No communication link with crewmembers/supervisors
8. Constructing line without safe anchor point
9. Building fireline downhill with fire below
10. Attempting frontal assault on fire
11. Unburned fuel between you and the fire
12. Cannot see main fire, not in contact with anyone who can
13. On a hillside where rolling material can ignite fuel below
14. Weather is getting hotter and drier
15. Wind increases and/or changes direction
16. Getting frequent spot fires across line
17. Terrain or fuels make escape to safety zones difficult
18. Taking a nap near the fire line
```

---

### 4.10 USFA — US Fire Administration Training & Data Resources

| Field | Details |
|---|---|
| **Full Name** | US Fire Administration (USFA) — National Fire Academy (NFA) Courses, NFIRS/NERIS Data, Publications |
| **Hosting Organization** | FEMA / US Fire Administration |
| **Domain** | Federal fire service training, incident data collection, research publications |
| **Format** | **PDF** (publications, course materials), **HTML** (online courses), **database** (NFIRS → NERIS transition), **GIS data** |
| **Machine-Readable** | ⚠️ **PARTIAL** — NFIRS/NERIS fire incident data is structured database format. Publications are PDFs. Online courses are HTML-based. |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — NFA courses contain scenario-based training with decision points. NFIRS incident type codes define a classification tree. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • USFA Homepage: https://www.usfa.fema.gov/ |
| | • NFA Online Courses: https://www.usfa.fema.gov/nfa/courses/online/ |
| | • NFA Course Catalog: https://apps.usfa.fema.gov/nfacourses/catalog/search |
| | • NFIRS Sunset / NERIS Transition: https://www.usfa.fema.gov/nfirs/neris/ |
| | • USFA Publications: https://www.usfa.fema.gov/publications/ |
| | • USFA Research: https://www.usfa.fema.gov/research/ |
| | • Firefighter Fatalities Database: https://apps.usfa.fema.gov/firefighter-fatalities/ |
| | • Wildland-Urban Interface (WUI) Resources: https://www.usfa.fema.gov/wui/ |
| | • Fire Is Everyone's Fight: https://www.usfa.fema.gov/prevention/fief/ |
| | • NERIS (National Emergency Response Information System): https://www.usfa.fema.gov/nfirs/neris/ |
| **AI Training Suitability** | **HIGH** — Multi-resource ecosystem. NFIRS/NERIS provides the largest structured fire incident database in the US (millions of records). Incident type classification codes form a taxonomy tree. NFA online courses provide scenario-based training content. Firefighter fatalities database provides structured records of LODD incidents. NERIS (successor to NFIRS, transitioning 2026) will provide modernized all-hazards incident data. |

---

## Focus Area 5: Incident Command System (ICS) Protocols

### 5.1 FEMA ICS Forms (ICS-201 through ICS-260)

| Field | Details |
|---|---|
| **Full Name** | NIMS/ICS Standard Forms (ICS-201 through ICS-260) |
| **Hosting Organization** | FEMA Emergency Management Institute (EMI) |
| **Domain** | Incident command documentation — standardized forms for incident management |
| **Format** | **Fillable PDF** forms, **PDF** instructions booklet |
| **Machine-Readable** | ✅ **YES (partial)** — Fillable PDFs contain structured form fields (field names, types, validation). The NIMS ICS Forms Booklet (2.9MB) contains all forms with instructions. Form field definitions are machine-extractable from PDF form metadata. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Forms define the information flow of incident management: ICS-201 (Incident Briefing) → ICS-202 (Objectives) → ICS-203 (Org Chart) → ICS-204 (Assignments) → ICS-215 (Ops Planning). Each form triggers specific decision points in the planning cycle. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • ICS Forms Page: https://training.fema.gov/emiweb/is/icsresource/icsforms |
| | • NIMS ICS Forms Booklet (v3, PDF): https://training.fema.gov/emiweb/is/icsresource/icsforms (2.9MB download) |
| | • ICS Forms Descriptions (Job Aid): https://training.fema.gov/emiweb/is/icsresource/assets/ICS%20Forms%20Descriptions.pdf |
| | • ICS Forms Instructions (v3): linked from forms page |
| **AI Training Suitability** | **VERY HIGH** — These forms define the *data architecture* of incident management. Each form can be parsed into a structured schema (field name → field type → data constraints). This enables: (1) VR scenario data generation that populates realistic ICS forms, (2) evaluation of trainee form completion, (3) automated incident action plan generation. |

**Complete ICS Forms Inventory:**
```
ICS-201  Incident Briefing
ICS-202  Incident Objectives
ICS-203  Organization Assignment List
ICS-204  Assignment List
ICS-205  Incident Radio Communications Plan
ICS-205A Communications List
ICS-206  Medical Plan
ICS-207  Incident Organization Chart
ICS-208  Safety Message/Plan
ICS-208HM Site Safety and Control Plan (HAZMAT)
ICS-209  Incident Status Summary
ICS-210  Resource Status Change
ICS-211  Incident Check-In List
ICS-213  General Message
ICS-213RR Resource Request Message
ICS-214  Activity Log
ICS-215  Operational Planning Worksheet
ICS-215A Incident Action Plan Safety Analysis
ICS-217A Communications Resource Availability Worksheet
ICS-218  Support Vehicle/Equipment Inventory
ICS-219  T-Cards (resource tracking, 10 color variants)
ICS-220  Air Operations Summary
ICS-221  Demobilization Check-Out
ICS-225  Incident Personnel Performance Rating
ICS-230CG Daily Meeting Schedule
ICS-233CG Incident Open Action Tracker
ICS-260  Resource Order
```

---

### 5.2 FEMA NIMS/ICS Training Courses (IS-100, IS-200, IS-700, IS-800)

| Field | Details |
|---|---|
| **Full Name** | FEMA Emergency Management Institute Independent Study Courses: IS-100.c (ICS), IS-200.c (Basic ICS), IS-700.b (NIMS), IS-800.d (NRF) |
| **Hosting Organization** | FEMA Emergency Management Institute (EMI) |
| **Domain** | Standardized ICS/NIMS training — baseline and additional courses for emergency management personnel |
| **Format** | **HTML** (online interactive courses), **PDF** (course materials, student manuals), **SCORM** (LMS-compatible) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Online courses are HTML-based with embedded assessments. Course materials available as PDFs. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Course content defines ICS decision frameworks: when to expand/contract organization, span of control rules, unified command vs. single IC decisions, resource typing |
| **Licensing** | 🟢 **Public domain** — US Government, free enrollment |
| **Direct URLs** | |
| | • IS-100.c ICS Introduction: https://training.fema.gov/is/courseoverview.aspx?code=IS-100.c |
| | • IS-200.c Basic ICS: https://training.fema.gov/is/courseoverview.aspx?code=IS-200.c |
| | • IS-700.b NIMS Introduction: https://training.fema.gov/is/courseoverview.aspx?code=IS-700.b |
| | • IS-800.d NRF Introduction: https://training.fema.gov/is/courseoverview.aspx?code=IS-800.c |
| | • IS-2200 Basic EOC Functions: https://training.fema.gov/is/courseoverview.aspx?code=IS-2200 |
| | • Training Materials Hub: https://training.fema.gov/emiweb/is/icsresource/trainingmaterials |
| | • NIMS Training Program Document: https://www.fema.gov/sites/default/files/documents/fema_nims_training-program-may-2020_0.pdf |
| | • EMI Course Catalog: https://training.fema.gov/emi.aspx |
| **AI Training Suitability** | **VERY HIGH** — These courses define the core ICS knowledge base. IS-100 through IS-800 cover the complete NIMS framework. Course assessment questions provide test data for evaluation engines. The NIMS Training Program document defines the entire training progression pathway — ideal for scaffolded VR training design. Position-specific courses (E/L 950-975) provide detailed role-based protocols. |

**NIMS/ICS Training Progression:**
```
Baseline:
  IS-700.b  → NIMS Introduction (all personnel)
  IS-100.c  → ICS Introduction (all personnel)

Additional:
  IS-200.c  → Basic ICS for Initial Response (first-line supervisors)
  IS-800.d  → National Response Framework (mid-level managers)
  
Intermediate:
  ICS-300   → Intermediate ICS for Expanding Incidents
  ICS-400   → Advanced ICS for Complex Incidents

Position-Specific:
  E/L 950   → Incident Commander
  E/L 952   → Public Information Officer
  E/L 954   → Safety Officer
  E/L 956   → Liaison Officer
  E/L 958   → Operations Section Chief
  E/L 960   → Division/Group Supervisor
  E/L 962   → Planning Section Chief
  E/L 964   → Situation Unit Leader
  E/L 967   → Logistics Section Chief
  E/L 973   → Finance/Admin Section Chief
```

---

### 5.3 NQS Position Task Books (PTBs)

| Field | Details |
|---|---|
| **Full Name** | National Qualification System (NQS) — Position Task Books and EOC Skillsets |
| **Hosting Organization** | FEMA |
| **Domain** | Competency evaluation for NIMS/ICS positions — structured task checklists |
| **Format** | **PDF** (task books), **fillable PDF** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Structured checklists in PDF format with defined tasks, competencies, and evaluation criteria |
| **Decision Trees / Branching Logic** | ✅ **YES** — Each PTB defines prerequisite qualifications, required tasks, competency demonstrations, and evaluator sign-off points. Tasks are organized by ICS function and follow the incident lifecycle. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • NQS Homepage: https://www.fema.gov/national-qualification-system |
| | • PTB Downloads: linked from NQS page |
| | • NQS Guidelines: https://www.fema.gov/sites/default/files/documents/fema_nims_nqs-guidelines_0.pdf |
| **AI Training Suitability** | **VERY HIGH** — PTBs are the authoritative competency evaluation instruments for ICS positions. Each task in a PTB maps directly to a VR evaluation checkpoint. The prerequisite chain defines training progression. Evaluator criteria provide pass/fail rubrics. Ideal for building position-specific VR training modules. |

---

### 5.4 ICS Job Aids & Reference Documents

| Field | Details |
|---|---|
| **Full Name** | FEMA ICS Job Aids — Organizational Structure, Forms Descriptions, Facilities, Incident Complexity, Planning Process, Position Titles, Transfer of Command |
| **Hosting Organization** | FEMA EMI |
| **Domain** | Quick-reference job aids for ICS operations |
| **Format** | **PDF** (printable job aids, 1-4 pages each) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Short, structured documents that can be easily manually converted |
| **Decision Trees / Branching Logic** | ✅ **YES** — Incident Action Planning Process is a cyclic decision workflow. Incident Complexity and Type classification is a decision matrix. Transfer of Command is a sequential checklist. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • ICS Job Aids Page: https://training.fema.gov/emiweb/is/icsresource/jobaids |
| | • ICS Organizational Structure: https://training.fema.gov/emiweb/is/icsresource/assets/ICS%20Organizational%20Structure%20and%20Elements.pdf |
| | • ICS Forms Descriptions: https://training.fema.gov/emiweb/is/icsresource/assets/ICS%20Forms%20Descriptions.pdf |
| | • Incident Facilities: https://training.fema.gov/emiweb/is/icsresource/assets/Incident%20Facilities.pdf |
| | • Incident Complexity and Type: https://training.fema.gov/emiweb/is/icsresource/assets/Incident%20Complexity%20and%20Type.pdf |
| | • Incident Action Planning Process: https://training.fema.gov/emiweb/is/icsresource/assets/Incident%20Action%20Planning%20Process.pdf |
| | • Position Titles: https://training.fema.gov/emiweb/is/icsresource/assets/Position%20Titles.pdf |
| | • Transfer of Command: https://training.fema.gov/emiweb/is/icsresource/assets/Transfer%20of%20Command.pdf |
| | • ICS Review Document: https://training.fema.gov/emiweb/is/icsresource/assets/ICS%20Review%20Document.pdf |
| | • Glossary of Terms: https://training.fema.gov/emiweb/is/icsresource/assets/Glossary%20of%20Related%20Terms.pdf |
| **AI Training Suitability** | **HIGH** — Compact, structured references ideal for quick encoding. The Incident Complexity classification (Type 5 → Type 1) provides scenario difficulty scaling. The Planning Process defines the operational cycle. Position Titles provide the complete ICS org chart taxonomy. |

**Incident Type Classification (for VR difficulty scaling):**
```
Type 5: Local, single resource, few personnel, <1 operational period
Type 4: Limited resources, single operational period, Command Staff may be needed
Type 3: Multiple operational periods, may require branch directors, written IAP
Type 2: Extended operations, many resources, full ICS organization, base camp
Type 1: Complex, national significance, all ICS positions filled, national resources
```

---

### 5.5 NWCG Standards — National Wildfire Coordinating Group

| Field | Details |
|---|---|
| **Full Name** | NWCG Standards, Publications, and Qualification System (PMS 310-1) |
| **Hosting Organization** | National Wildfire Coordinating Group (NWCG) — interagency consortium (USFS, BLM, NPS, BIA, USFWS, FEMA, NASF, IAFC) |
| **Domain** | Wildland fire management — qualification standards, operational procedures, training curricula |
| **Format** | **PDF** (PMS/NFES publications), **HTML** (web resources), **pocket guides** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Publications are PDFs, but the qualification system (PMS 310-1) uses structured position/task/training matrices |
| **Decision Trees / Branching Logic** | ✅ **YES** — Wildland Fire Qualification System defines training progression trees per position. Fireline Handbook contains operational decision procedures. IRPG contains position-specific checklists with decision points. |
| **Licensing** | 🟢 **Public domain** — US Government interagency |
| **Direct URLs** | |
| | • NWCG Homepage: https://www.nwcg.gov/ |
| | • NWCG Publications: https://www.nwcg.gov/publications |
| | • PMS 310-1 Qualification Guide: https://www.nwcg.gov/publications/pms310-1 |
| | • PMS 410-1 Fireline Handbook: https://www.nwcg.gov/publications/pms410-1 |
| | • PMS 461 IRPG (Incident Response Pocket Guide): https://www.nwcg.gov/publications/pms461 |
| | • PMS 902 Incident Business Management: https://www.nwcg.gov/publications/pms902 |
| | • NWCG Glossary: https://www.nwcg.gov/glossary |
| | • NWCG Training Courses: https://www.nwcg.gov/publications/training-courses |
| | • Field Operations Guide (NFES 1077): https://www.nwcg.gov/publications/pms410-1 |
| **AI Training Suitability** | **EXTREMELY HIGH** — NWCG is the authoritative source for wildland fire management. PMS 310-1 defines the entire qualification system (positions, prerequisites, training requirements). The IRPG is the single most important field reference for wildland firefighters — it contains checklists for every operational situation. The Fireline Handbook provides the operational procedures. Together, these provide the complete knowledge base for wildland fire VR training. |

---

### 5.6 FIRESCOPE ICS Documentation

| Field | Details |
|---|---|
| **Full Name** | FIRESCOPE — Firefighting Resources of Southern California Organized for Potential Emergencies |
| **Hosting Organization** | California Governor's Office of Emergency Services (Cal OES) / FIRESCOPE |
| **Domain** | Original ICS development — operational procedures, position manuals, field operations guides |
| **Format** | **PDF** (FOGs, position manuals, ICS reference guides) |
| **Machine-Readable** | ❌ **NO** — PDFs |
| **Decision Trees / Branching Logic** | ✅ **YES** — FIRESCOPE Field Operations Guide (FOG) contains position-specific checklists, ICS organization decision guides, resource typing |
| **Licensing** | 🟢 **Public domain** — California state government |
| **Direct URLs** | |
| | • FIRESCOPE Homepage: https://firescope.caloes.ca.gov/ |
| | • FIRESCOPE Publications: https://firescope.caloes.ca.gov/ics-publications/ |
| | • FIRESCOPE FOG: linked from publications page |
| **AI Training Suitability** | **HIGH** — FIRESCOPE is the origin of modern ICS. Their publications provide the most mature and detailed ICS implementation guides. The FOG is a comprehensive field reference used by many agencies beyond California. Position manuals provide detailed role-specific checklists. |

---

## Focus Area 6: HAZMAT Response

### 6.1 ERG 2024 — Emergency Response Guidebook (DOT/PHMSA)

| Field | Details |
|---|---|
| **Full Name** | 2024 Emergency Response Guidebook (ERG) |
| **Hosting Organization** | U.S. Department of Transportation, Pipeline and Hazardous Materials Safety Administration (PHMSA), jointly with Transport Canada and Mexico SCT |
| **Format** | **PDF** (accessible, 396 pages), **mobile app** (iOS/Android), **web browser version** (CANUTEC), **InDesign source files** (.indd), **Microsoft Office files** (.docx, .xlsx) available to commercial suppliers |
| **Machine-Readable** | ✅ **YES (partially)** — The ERG has a structured format: Yellow Pages (UN/NA number index → Guide number), Blue Pages (chemical name index → Guide number), Orange Pages (numbered guides with response procedures), Green Pages (initial isolation/protective action distances). The web browser version (CANUTEC) and mobile app provide searchable interfaces. The .xlsx source files are machine-readable. |
| **Decision Trees / Branching Logic** | ✅ **YES — EXTENSIVE** — The ERG is fundamentally a lookup + decision tree system: |
| | 1. **Identification**: Placard/label → UN/NA number → Guide number |
| | 2. **Guide Pages**: Each of 62 guide pages provides structured: POTENTIAL HAZARDS (health, fire/explosion) → EMERGENCY RESPONSE (fire, spill/leak, first aid) |
| | 3. **Table 1 (Green Pages)**: Initial isolation distances by material, day/night, small/large spill — a structured data table |
| | 4. **Decision flowchart**: Placard visible? → 4-digit number? → Container shape? → Commodity shipped? → fallback guide |
| **Licensing** | 🟢 **Public domain** — US/Canada/Mexico government joint publication. Free PDF download. Print production files available on request. 18M+ copies distributed. |
| **Direct URLs** | |
| | • ERG Homepage: https://www.phmsa.dot.gov/hazmat/outreach-training/erg |
| | • ERG 2024 PDF (English, Accessible): https://www.phmsa.dot.gov/training/hazmat/erg/erg2024-pdf-accessible-english |
| | • ERG 2024 Web Browser (CANUTEC): https://wwwapps.tc.gc.ca/saf-sec-sur/3/erg-gmu-web/ |
| | • ERG 2024 Mobile App: https://www.phmsa.dot.gov/training/hazmat/erg/erg-mobile-app |
| | • ERG Summary of Changes: https://www.phmsa.dot.gov/training/hazmat/erg/erg2024-summary-changes |
| | • Development of Isolation Distances: https://www.phmsa.dot.gov/training/hazmat/erg/development-table-initial-isolation-and-protective-action-distances-erg-2024 |
| | • How to Use the ERG (YouTube): https://www.youtube.com/watch?v=xga91mIa6DY |
| | • ERG Spanish: https://www.phmsa.dot.gov/training/hazmat/erg/gre2024-pdf-accesible-espanol |
| | • ERG French: https://www.phmsa.dot.gov/training/hazmat/erg/gmu2024-pdf-accessible-francais |
| | • Print Production Files: request via ERGComments@dot.gov |
| **AI Training Suitability** | **EXTREMELY HIGH** — The ERG is the single most important HAZMAT reference for first responders. Key AI training values: |
| | 1. **Structured lookup table**: UN/NA number → Guide → Response procedures. Directly encodable as database/knowledge graph. |
| | 2. **62 guide pages**: Each provides fire response, spill response, first aid — structured text that can be NLP-parsed. |
| | 3. **Isolation distance tables**: Structured numerical data (material × spill size × day/night → distance). Perfect for database encoding. |
| | 4. **Identification flowchart**: Step-by-step decision tree for unknown materials. |
| | 5. **.xlsx source availability** means the data tables can be directly imported into databases. |
| | 6. **VR application**: HAZMAT response VR scenarios can use ERG lookup as a core interaction mechanic. |

---

### 6.2 OSHA HAZWOPER — 29 CFR 1910.120

| Field | Details |
|---|---|
| **Full Name** | OSHA Hazardous Waste Operations and Emergency Response (HAZWOPER) Standard — 29 CFR 1910.120 |
| **Hosting Organization** | U.S. Department of Labor, Occupational Safety and Health Administration (OSHA) |
| **Domain** | Worker safety for hazardous waste operations and emergency response — training requirements, PPE levels, decontamination, emergency response plan |
| **Format** | **HTML** (regulatory text), **PDF** (guidance documents, fact sheets) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Regulatory text is HTML (parseable). Training level requirements are structured (awareness, operations, technician, specialist, IC). PPE levels (A/B/C/D) are well-defined hierarchical categories. |
| **Decision Trees / Branching Logic** | ✅ **YES** — PPE level selection (A → B → C → D) is a decision tree based on hazard assessment. Training levels define a qualification hierarchy. Emergency response plan elements are structured checklists. Site control zone system (hot/warm/cold) follows decision logic. |
| **Licensing** | 🟢 **Public domain** — US Government regulation |
| **Direct URLs** | |
| | • HAZWOPER Regulation: https://www.osha.gov/laws/regs/regulations/standardnumber/1910/1910.120 |
| | • OSHA HAZWOPER Topic Page: https://www.osha.gov/hazardous-waste |
| | • OSHA HAZWOPER Fact Sheet: https://www.osha.gov/sites/default/files/publications/osha3114.pdf |
| | • OSHA HAZWOPER Guidance: https://www.osha.gov/emergency-preparedness/hazardous-waste-operations |
| | • eCFR (full text): https://www.ecfr.gov/current/title-29/subtitle-B/chapter-XVII/part-1910/subpart-H/section-1910.120 |
| **AI Training Suitability** | **VERY HIGH** — HAZWOPER defines the regulatory framework for all HAZMAT response. Key encodable elements: |
| | 1. **Five training levels** (Awareness → Operations → Technician → Specialist → IC) with defined competencies |
| | 2. **PPE Levels A/B/C/D**: Decision tree for ensemble selection based on hazard characterization |
| | 3. **Site control zones**: Hot/Warm/Cold zone establishment procedures |
| | 4. **Decontamination procedures**: Sequential steps for personnel and equipment decon |
| | 5. **Emergency response plan** elements: Structured checklist (pre-emergency planning, personnel roles, communication procedures, decon procedures, medical surveillance) |

**PPE Level Decision Tree (encodable):**
```
Level A: Maximum protection
  → Unknown hazard, high concentrations, vapor/gas IDLH
  → Full encapsulating suit + SCBA

Level B: High respiratory, moderate skin protection
  → Known hazard, IDLH atmosphere, low skin absorption risk
  → Chemical splash suit + SCBA

Level C: Moderate protection
  → Known contaminant, measured concentration, APR adequate
  → Chemical splash suit + APR

Level D: Minimum protection
  → No respiratory or skin hazard, nuisance contamination only
  → Work clothes + safety glasses + hard hat
```

---

### 6.3 NIOSH Pocket Guide to Chemical Hazards (NPG)

| Field | Details |
|---|---|
| **Full Name** | NIOSH Pocket Guide to Chemical Hazards (NPG) |
| **Hosting Organization** | CDC / NIOSH |
| **Domain** | Workplace chemical hazards — exposure limits, physical properties, PPE recommendations, first aid |
| **Format** | **HTML** (searchable online database), **PDF** (6,192 KB downloadable guide), **mobile web app** (iOS/Android), **print** (pocket-sized book) |
| **Machine-Readable** | ✅ **YES** — The online NPG is a searchable HTML database with consistent structured fields per chemical. Can be scraped or accessed programmatically. Indexed by chemical name, synonym, trade name, and CAS number. |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — Each chemical entry provides structured data (exposure limits → symptoms → target organs → PPE → first aid) that implies a decision pathway. Not explicit branching but highly structured. |
| **Licensing** | 🟢 **Public domain** — US Government (CDC/NIOSH) |
| **Direct URLs** | |
| | • NPG Homepage: https://www.cdc.gov/niosh/npg/ |
| | • NPG PDF Download: https://www.cdc.gov/niosh/docs/2005-149/default.html |
| | • NPG Mobile Web App: https://www.cdc.gov/niosh/npg/mobilepocketguide.html |
| | • More Downloadable Versions: https://www.cdc.gov/niosh/npg/downloadable.html |
| | • Chemical Name Index: https://www.cdc.gov/niosh/npg/npgsyn-a.html |
| | • CAS Number Index: https://www.cdc.gov/niosh/npg/npgdcas.html |
| **AI Training Suitability** | **VERY HIGH** — The NPG is a structured chemical hazard database covering hundreds of chemicals/classes. Each entry has consistent fields: chemical name → CAS# → DOT ID → IDLH → exposure limits → physical description → chemical properties → incompatibilities → exposure routes → symptoms → target organs → PPE → first aid. This structured per-chemical format is ideal for: (1) building a chemical hazard knowledge graph, (2) substance identification training, (3) PPE selection decision support, (4) first aid protocol lookup in VR. |

**NPG Entry Structure (per chemical):**
```
Chemical Name / Synonyms / Trade Names
CAS Number
RTECS Number
DOT ID & Guide Number (links to ERG!)
Formula / Molecular Weight
IDLH (Immediately Dangerous to Life or Health)
Conversion factors
Exposure Limits (NIOSH REL, OSHA PEL)
Physical Description
Chemical & Physical Properties (boiling point, flash point, etc.)
Incompatibilities & Reactivities
Measurement Methods
Personal Protection & Sanitation
Respirator Recommendations
Health Hazards (routes of exposure, symptoms, target organs)
First Aid procedures
```

---

### 6.4 CAMEO/ALOHA — Computer-Aided Management of Emergency Operations

| Field | Details |
|---|---|
| **Full Name** | CAMEO Software Suite (CAMEO Data Manager, CAMEO Chemicals, ALOHA, MARPLOT, Tier2 Submit) |
| **Hosting Organization** | EPA and NOAA (jointly developed since 1988) |
| **Domain** | Chemical emergency planning and response — chemical database, air dispersion modeling, GIS mapping, facility data management |
| **Format** | **Desktop application** (Windows/Mac), **mobile app**, **web database** (CAMEO Chemicals), **GIS layers** (MARPLOT), **database** (CAMEO Data Manager). CAMEO Chemicals has both online and offline versions. |
| **Machine-Readable** | ✅ **YES** — CAMEO Chemicals is a structured database with consistent per-chemical datasheets (physical properties, hazards, response info). The web version is searchable. The desktop version stores data in a local database. National Tier II Data Standard provides structured data exchange format. |
| **Decision Trees / Branching Logic** | ✅ **YES** — CAMEO Chemicals reactivity prediction tool uses chemical compatibility matrices (IF chemical A mixed with chemical B THEN predict hazards). ALOHA uses dispersion models to generate threat zones (decision support for evacuation). ERG guide numbers are cross-referenced. |
| **Licensing** | 🟢 **Public domain** — US Government (EPA/NOAA). Free downloads. |
| **Direct URLs** | |
| | • CAMEO Homepage (EPA): https://www.epa.gov/cameo |
| | • CAMEO Suite Overview: https://www.epa.gov/cameo/what-cameo-software-suite |
| | • CAMEO Chemicals Web: https://cameochemicals.noaa.gov/ |
| | • CAMEO Chemicals Mobile: https://m.cameochemicals.noaa.gov/ |
| | • CAMEO Chemicals Desktop: https://www.epa.gov/cameo/cameo-chemicals-software (v3.1.0, May 2024) |
| | • ALOHA Download: https://www.epa.gov/cameo/aloha-software (v5.4.7) |
| | • MARPLOT Download: https://www.epa.gov/cameo/marplot-software (v5.1.1) |
| | • CAMEO Data Manager: https://www.epa.gov/cameo/cameo-data-manager-software (v4.5.1, Dec 2025) |
| | • Tier2 Submit: https://www.epa.gov/epcra/tier2-submit-software (v2025 rev1, Feb 2026) |
| | • CAMEO Training & Events: https://www.epa.gov/cameo/cameo-training-and-events |
| | • National Tier II Data Standard: https://cameo.noaa.gov/epcra_tier2/data_standard/v1/ |
| **AI Training Suitability** | **EXTREMELY HIGH** — The CAMEO suite is a comprehensive chemical emergency management system. Key AI training values: |
| | 1. **CAMEO Chemicals**: Structured database of thousands of chemicals with response datasheets + UN/NA datasheets linking to ERG. Chemical reactivity prediction is a unique feature. |
| | 2. **Reactivity prediction**: The "MyChemicals" mixing tool implements hazard prediction rules — these rules can be extracted for knowledge graphs. |
| | 3. **ALOHA**: Air dispersion modeling provides threat zone estimation — parameters can drive VR scenario generation for HAZMAT plume scenarios. |
| | 4. **MARPLOT**: GIS integration enables spatially-aware VR scenarios. |
| | 5. **Data integration**: CAMEO links to ERG, NPG, and other databases — provides a unified chemical data ecosystem. |
| | 6. **National Tier II Data Standard**: Structured data format for chemical inventory — can generate realistic facility profiles for VR scenarios. |

---

### 6.5 WISER — Wireless Information System for Emergency Responders

| Field | Details |
|---|---|
| **Full Name** | WISER (Wireless Information System for Emergency Responders) |
| **Hosting Organization** | National Library of Medicine (NLM) / HHS |
| **Domain** | HAZMAT identification, substance information, treatment protocols — designed for first responders in the field |
| **Format** | **Mobile app** (iOS/Android), **web application**, integrated with **CHEMM** |
| **Machine-Readable** | ⚠️ **PARTIAL** — App-based interface with structured substance data. The underlying database contains structured chemical records. |
| **Decision Trees / Branching Logic** | ✅ **YES** — WISER includes: (1) substance identification by physical properties/symptoms, (2) help identify unknown chemicals through observation-based filtering, (3) treatment protocol lookup, (4) protective distance recommendations |
| **Licensing** | 🟢 **Public domain** — US Government (NLM/HHS) |
| **Direct URLs** | |
| | • WISER Homepage: https://wiser.nlm.nih.gov/ |
| | • WISER/CHEMM App (iOS): available on App Store |
| | • WISER/CHEMM App (Android): available on Google Play |
| | • CHEMM integration: https://chemm.hhs.gov/ |
| **AI Training Suitability** | **HIGH** — WISER complements CHEMM with a field-oriented substance identification workflow. The "identify by symptoms/properties" feature implements a diagnostic decision tree that is ideal for VR HAZMAT identification scenarios. Integration with CHEMM provides seamless access to treatment protocols. |

---

### 6.6 UN GHS — Globally Harmonized System of Classification and Labelling

| Field | Details |
|---|---|
| **Full Name** | Globally Harmonized System of Classification and Labelling of Chemicals (GHS), "Purple Book" |
| **Hosting Organization** | United Nations Economic Commission for Europe (UNECE) |
| **Domain** | International chemical classification — hazard categories, pictograms, signal words, hazard/precautionary statements |
| **Format** | **PDF** (GHS Rev.10, 2023), **HTML** (online reference), **XML** (GHS data exchange format) |
| **Machine-Readable** | ✅ **YES (partial)** — GHS classification criteria are structured hierarchically (hazard class → category → pictogram → signal word → H-statement → P-statement). Some XML implementations exist. |
| **Decision Trees / Branching Logic** | ✅ **YES** — GHS classification is a multi-level decision tree: substance properties → hazard class determination → category assignment → label element selection. Each hazard class (flammable, toxic, corrosive, etc.) has defined category thresholds. |
| **Licensing** | 🟢 **Public domain** — UN publication, freely available |
| **Direct URLs** | |
| | • GHS (Rev.10, 2023): https://unece.org/transport/standards/transport/dangerous-goods/ghs-rev10-2023 |
| | • GHS Documentation Hub: https://unece.org/transportdangerous-goodsghs-702/ghs-documentation |
| | • OSHA GHS Resources: https://www.osha.gov/hazcom |
| | • UN Recommendations on Transport of Dangerous Goods: https://unece.org/transport/dangerous-goods |
| **AI Training Suitability** | **HIGH** — GHS provides the universal classification taxonomy for chemical hazards. The classification decision trees are directly encodable. GHS pictograms, signal words, and H/P-statements provide a standardized vocabulary for VR chemical hazard training. The hierarchical hazard category system maps to knowledge graphs. Integration with ERG, NPG, and CAMEO databases creates a comprehensive chemical hazard knowledge base. |

---

## Focus Area 7: Search and Rescue

### 7.1 FEMA USAR — Urban Search and Rescue Field Operations Guide

| Field | Details |
|---|---|
| **Full Name** | FEMA National Urban Search and Rescue (US&R) Response System — Field Operations Guide (FOG) |
| **Hosting Organization** | FEMA |
| **Domain** | Federal USAR task force operations — structural collapse rescue, search techniques, shoring, victim removal |
| **Format** | **PDF** (FOG document), **HTML** (web resources) |
| **Machine-Readable** | ❌ **NO** — PDF manual format |
| **Decision Trees / Branching Logic** | ✅ **YES** — USAR operations follow structured decision protocols: search mode selection (physical search, canine, technical), structural assessment (safe/unsafe), victim access priorities, shoring decision trees, medical treatment in confined spaces |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • FEMA US&R: https://www.fema.gov/emergency-managers/national-preparedness/frameworks/urban-search-rescue |
| | • FEMA US&R Directive 2024-001: search FEMA.gov for current directive |
| | • Task Force Equipment Cache List: available through FEMA US&R program |
| | • (Note: FEMA website was partially offline due to federal funding lapse at time of access, March 2026) |
| **AI Training Suitability** | **HIGH** — USAR FOG defines the procedural framework for structural collapse rescue operations. Key procedures (search, rescue, shoring, medical) are sequential with decision points. The USAR marking system (structural triage, victim location, hazard identification) provides a structured visual language encodable for VR. FEMA maintains 28 national USAR task forces. |

**USAR Search Phases (encodable):**
```
Phase 1: Hasty Search (surface victims, voice contact)
Phase 2: Primary Search (systematic physical/canine, all accessible areas)
Phase 3: Secondary Search (technical search equipment, confined spaces)
Phase 4: Extended Operations (heavy equipment, deep burial)
```

**USAR Structural Marking System:**
```
Single slash (/) → Search in progress
X → Search complete
    Top: Time/Date completed
    Left: Team ID
    Right: Hazards
    Bottom: Number of live/deceased victims
Box around X → Structure assessed, do not enter (unsafe)
```

---

### 7.2 INSARAG Guidelines 2020 — International SAR Standards

| Field | Details |
|---|---|
| **Full Name** | INSARAG Guidelines 2020 (International Search and Rescue Advisory Group) |
| **Hosting Organization** | United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA) |
| **Domain** | International USAR standards — team classification, coordination, field operations |
| **Format** | **PDF** (5 volumes), **Word** (some annexes), available in multiple languages (English, Japanese, Chinese, Hungarian, Spanish, French, Farsi, Arabic) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Structured manual format with checklists and annexes. Word/PDF format. |
| **Decision Trees / Branching Logic** | ✅ **YES** — Team classification criteria (Light/Medium/Heavy), USAR Coordination Cell (UCC) procedures, operational checklists, IER assessment criteria, reception/departure center procedures |
| **Licensing** | 🟢 **Open** — UN publication, freely available. Google Drive hosted. |
| **Direct URLs** | |
| | • INSARAG Guidelines Page: https://www.insarag.org/methodology/insarag-guidelines/ |
| | • Volume I — Policy: linked from guidelines page |
| | • Volume II, Manual A — Capacity Building: linked from guidelines page |
| | • Volume II, Manual B — Operations: linked from guidelines page |
| | • Volume II, Manual C — External Classification & Reclassification: linked from guidelines page |
| | • Volume III — Operational Field Guide: linked from guidelines page |
| | • Complete Guidelines (Google Drive): https://drive.google.com/drive/folders/1Wp38Kfhy7pG8mBYNYxlOWLgl2tnw1zRM?usp=sharing |
| | • Guidance Notes: https://www.insarag.org/guidance-notes/guidance-notes/ |
| | • Technical Reference Library: https://www.insarag.org/technical-reference-library/index/ |
| | • INSARAG Homepage: https://www.insarag.org/ |
| **AI Training Suitability** | **VERY HIGH** — INSARAG provides the international standard for USAR operations. Volume III (Operational Field Guide) contains the practical checklists and procedures for field operations. The classification system (Light/Medium/Heavy) provides scenario scaling. The USAR Coordination Cell procedures define command-level decision protocols for international disaster response. Multiple language versions enable multilingual VR training. |

**INSARAG Guidelines Structure:**
```
Volume I:   Policy (governance, principles, coordination framework)
Volume II:  
  Manual A: Capacity Building (team development, training, exercises)
  Manual B: Operations (deployment, coordination, field procedures)
  Manual C: External Classification & Reclassification (team assessment)
Volume III: Operational Field Guide (practical field reference, checklists)
```

---

### 7.3 NASAR — National Association for Search and Rescue

| Field | Details |
|---|---|
| **Full Name** | NASAR Education and Certification Programs — FUNSAR, ISAR, MLPI, SAR Tech I/II/III |
| **Hosting Organization** | National Association for Search and Rescue (NASAR) |
| **Domain** | Land search and rescue — fundamentals, management, techniques, certification |
| **Format** | **Online courses** (SAR Academy via Thinkific LMS), **PDF** (course materials), **certification programs** |
| **Machine-Readable** | ❌ **NO** — Course-based materials, LMS platform |
| **Decision Trees / Branching Logic** | ✅ **YES** — Lost person behavior profiles define search area probability models. Search management follows decision protocols (Mattson Consensus, POA calculations). SAR techniques involve procedural sequences. |
| **Licensing** | 🔴 **Copyright restricted / Fee-based** — Courses and certifications require paid enrollment and NASAR membership |
| **Direct URLs** | |
| | • NASAR Homepage: https://www.nasar.org/ |
| | • SAR Academy: https://saracademy.thinkific.com/ |
| | • Programs: https://nasar.site-ym.com/page/Programs |
| | • Membership: https://nasar.site-ym.com/general/register_member_type.asp |
| | • Certification: https://nasar.site-ym.com/page/Programs |
| **AI Training Suitability** | **MEDIUM (data access) / HIGH (concepts)** — NASAR defines the professional SAR certification structure. Key concepts that can inform VR training: (1) Lost person behavior models (statistical profiles by subject category), (2) Probability of Area (POA) calculations, (3) Probability of Detection (POD), (4) search urgency scoring. The SAR certification levels (SAR Tech III → II → I) define a progression framework. While course content requires enrollment, the conceptual framework is widely documented in SAR literature. |

**NASAR Course/Certification Structure:**
```
Courses:
  FUNSAR  → Fundamentals of Search and Rescue
  ISAR    → Introduction to Search and Rescue
  MLPI    → Managing the Lost Person Incident

Certifications:
  SAR Tech III → Basic SAR participant
  SAR Tech II  → Advanced SAR technician
  SAR Tech I   → SAR team leader
```

---

### 7.4 Swiftwater / Water Rescue SOPs

| Field | Details |
|---|---|
| **Full Name** | Swiftwater Rescue / Water Rescue Standard Operating Procedures and Training Standards |
| **Hosting Organization** | Various — NFPA 1670/1006 (technical rescue standards), Rescue 3 International, state fire academies |
| **Domain** | Water rescue operations — swiftwater, flood, dive, surface water rescue |
| **Format** | **PDF** (NFPA standards, training curricula), **certification programs** |
| **Machine-Readable** | ❌ **NO** — Standards documents and training materials |
| **Decision Trees / Branching Logic** | ✅ **YES** — Rescue risk-benefit analysis ("reach, throw, row, go" hierarchy). Self-rescue procedures. Victim contact decision tree. Defensive vs. offensive swimming. Hydrology assessment (hydraulics, strainers, undercuts). |
| **Licensing** | 🔴 **Mixed** — NFPA standards are copyrighted. Rescue 3 courses are fee-based. Some state training materials are public. |
| **Direct URLs** | |
| | • NFPA 1670 (Technical Rescue Operations & Training): https://www.nfpa.org/codes-and-standards/nfpa-1670-standard-on-operations-and-training-for-technical-search-and-rescue-incidents |
| | • NFPA 1006 (Technical Rescue Personnel Qualifications): https://www.nfpa.org/codes-and-standards/nfpa-1006-standard-for-technical-rescue-personnel-professional-qualifications |
| | • Rescue 3 International: https://www.rescue3.com/ |
| | • (Note: Individual department water rescue SOPs are often publicly available) |
| **AI Training Suitability** | **MEDIUM-HIGH** — Water rescue follows clear procedural hierarchies that map well to decision trees. The "reach-throw-row-go" progression is a fundamental rescue decision tree. Swiftwater hydrology assessment provides environmental awareness training. For VR application, water rescue scenarios require specialized physics simulation but the procedural logic is straightforward to encode. |

**Water Rescue Decision Hierarchy (encodable):**
```
1. REACH → Extend arm, pole, or object to victim (safest)
2. THROW → Throw rope bag or flotation device
3. ROW   → Use watercraft to approach victim  
4. GO    → Swim to victim with flotation aid (most dangerous)

Pre-assessment:
  → Is scene safe? (upstream hazards, water conditions)
  → Number of victims?
  → Victim status? (conscious/unconscious, in/out of water)
  → Resources available?
  → Risk to rescuer acceptable?
```

---

## Focus Area 8: Disaster Evacuation & Civil Defense

### 8.1 FEMA Evacuation Planning Guides

| Field | Details |
|---|---|
| **Full Name** | FEMA Evacuation & Shelter-in-Place Guidance — Planning Considerations, Evacuation & Shelter-in-Place, Large-Scale Evacuation |
| **Hosting Organization** | FEMA |
| **Domain** | Evacuation planning — route planning, shelter operations, transportation, special needs populations |
| **Format** | **PDF** (planning guides, reference documents) |
| **Machine-Readable** | ❌ **NO** — Narrative PDF format |
| **Decision Trees / Branching Logic** | ✅ **YES** — Evacuation vs. shelter-in-place decision matrix (based on hazard type, timeline, population). Phased evacuation decision points. Re-entry criteria. Special needs population considerations. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • Ready.gov Evacuation: https://www.ready.gov/evacuation (redirects due to current site issues) |
| | • FEMA Planning Guides: https://www.fema.gov/emergency-managers/national-preparedness/plan |
| | • Comprehensive Preparedness Guide (CPG) 101: https://www.fema.gov/emergency-managers/national-preparedness/plan/cpg-101 |
| | • Evacuation Planning Reference (FEMA P-760): search FEMA publications |
| | • Mass Evacuation Incident Annex to NRF: search FEMA.gov |
| **AI Training Suitability** | **HIGH** — Evacuation decision logic (when to evacuate vs. shelter-in-place, which zones, phasing) is directly encodable as decision trees. Special needs population considerations add complexity layers for advanced VR scenarios. Route planning algorithms can integrate with VR environment design. |

**Evacuation vs. Shelter-in-Place Decision Framework (encodable):**
```
EVACUATE when:
  → External hazard approaching (hurricane, wildfire, flood)
  → Structure damage imminent or occurred
  → Evacuation route available and clear
  → Time available exceeds evacuation time estimate

SHELTER-IN-PLACE when:
  → Hazardous materials release (airborne)
  → Active threat (lockdown)
  → Insufficient time to evacuate
  → Structure provides adequate protection
  → Evacuation routes compromised

Phased Evacuation:
  Phase 1: Immediate danger zone (mandatory)
  Phase 2: Adjacent areas (precautionary)
  Phase 3: Extended zones (voluntary)
```

---

### 8.2 CERT — Community Emergency Response Team Training Materials

| Field | Details |
|---|---|
| **Full Name** | CERT Basic Training — Instructor Guides, Participant Manuals, Hazard Annexes |
| **Hosting Organization** | FEMA |
| **Domain** | Community-level disaster preparedness — fire safety, light search and rescue, team organization, disaster medical operations |
| **Format** | **PDF** (instructor guides, participant manuals), **PowerPoint** (slide decks), **HTML** (IS-317, IS-315 online courses) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Course materials are structured by unit with defined objectives and skill demonstrations. Online IS courses are HTML-based with assessments. |
| **Decision Trees / Branching Logic** | ✅ **YES** — CERT training covers: fire suppression decision (fight or flight based on size/resources), triage (modified START), search patterns, medical treatment priorities. IS-315 covers CERT/ICS interface. |
| **Licensing** | 🟢 **Public domain** — US Government (FEMA). Free online courses. |
| **Direct URLs** | |
| | • CERT Homepage: https://fema.gov/cert |
| | • CERT Program Page: https://www.fema.gov/emergency-managers/individuals-communities/preparedness-activities-webinars/community-emergency-response-team |
| | • IS-317 (Introduction to CERT): https://training.fema.gov/is/courseoverview.aspx?code=IS-317 |
| | • IS-315 (CERT and ICS): https://training.fema.gov/is/courseoverview.aspx?code=IS-315.a |
| | • CERT Liability Guide: https://www.ready.gov/sites/default/files/2021-04/CERT_Liability_Guide%20v2.pdf |
| | • Campus CERT Guide: https://www.ready.gov/sites/default/files/2019-06/campus_cert_starter_guide_final.pdf |
| | • Workplace CERT Guide: https://www.ready.gov/sites/default/files/2020-08/workplace_cert_starter_guide.pdf |
| | • Teen CERT: https://www.ready.gov/kids/teen-cert |
| **AI Training Suitability** | **VERY HIGH** — CERT training is specifically designed for non-professional volunteers — making it ideal for beginner-level VR training scenarios. The curriculum covers a breadth of emergency response skills at an accessible level. Key VR applications: (1) fire safety decision-making, (2) light search and rescue procedures, (3) basic triage (simplified START), (4) team organization and ICS basics, (5) disaster medical operations. CERT assessment scenarios can be directly adapted to VR. 600,000+ people trained nationally. |

**CERT Training Units (for VR module design):**
```
Unit 1: Disaster Preparedness
Unit 2: Fire Safety & Utility Controls
Unit 3: Disaster Medical Operations – Part 1
Unit 4: Disaster Medical Operations – Part 2
Unit 5: Light Search and Rescue Operations
Unit 6: CERT Organization
Unit 7: Disaster Psychology
Unit 8: Terrorism and CERT
Unit 9: Course Review & Disaster Simulation
```

---

### 8.3 National Response Framework (NRF) & Emergency Support Functions (ESFs)

| Field | Details |
|---|---|
| **Full Name** | National Response Framework (NRF), 4th Edition (2019) — including Emergency Support Function (ESF) Annexes and Support Annexes |
| **Hosting Organization** | FEMA / DHS |
| **Domain** | National-level disaster response coordination — defines roles, responsibilities, and coordination structures for federal, state, tribal, and local response |
| **Format** | **PDF** (NRF document, ESF annexes, support annexes), **HTML** (overview pages) |
| **Machine-Readable** | ⚠️ **PARTIAL** — The ESF structure is well-defined with numbered functions and designated lead/support agencies. Response coordination structures follow defined hierarchies. |
| **Decision Trees / Branching Logic** | ✅ **YES** — NRF defines activation decision criteria, scalable response organization, and the relationship between local → state → federal response levels. ESFs define functional responsibilities with triggering criteria. |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • NRF Overview: https://www.fema.gov/emergency-managers/national-preparedness/frameworks/response |
| | • NRF 4th Edition PDF: https://www.fema.gov/sites/default/files/2020-04/NRF_FINALApproved_2011028.pdf |
| | • IS-800.d (NRF Introduction): https://training.fema.gov/is/courseoverview.aspx?code=IS-800.c |
| | • ESF Annexes: search FEMA.gov for individual ESF documents |
| | • (Note: FEMA website partially affected by federal funding lapse, March 2026) |
| **AI Training Suitability** | **HIGH** — The NRF defines the overarching coordination framework for disaster response. The ESF structure provides a comprehensive taxonomy of emergency response functions. For VR training, the NRF informs: (1) multi-agency coordination scenarios, (2) resource request and allocation procedures, (3) escalation decision criteria (local → state → federal). |

**15 Emergency Support Functions (ESF Taxonomy):**
```
ESF #1:  Transportation
ESF #2:  Communications
ESF #3:  Public Works and Engineering
ESF #4:  Firefighting
ESF #5:  Information and Planning
ESF #6:  Mass Care, Emergency Assistance, Temporary Housing, and Human Services
ESF #7:  Logistics
ESF #8:  Public Health and Medical Services
ESF #9:  Search and Rescue
ESF #10: Oil and Hazardous Materials Response
ESF #11: Agriculture and Natural Resources
ESF #12: Energy
ESF #13: Public Safety and Security
ESF #14: Cross-Sector Business and Infrastructure
ESF #15: External Affairs
```

---

### 8.4 ARC — American Red Cross Shelter Management

| Field | Details |
|---|---|
| **Full Name** | American Red Cross Shelter Management — Operations Toolkit, Shelter Fundamentals |
| **Hosting Organization** | American Red Cross (ARC) |
| **Domain** | Disaster shelter operations — setup, registration, feeding, dormitory management, special populations, closure |
| **Format** | **PDF** (shelter management guides, toolkits), **online training** (ARC learning center) |
| **Machine-Readable** | ❌ **NO** — Training materials in PDF/course format |
| **Decision Trees / Branching Logic** | ✅ **YES** — Shelter operations follow procedural checklists: site selection criteria, capacity assessment, shelter opening decision, operations management, closure criteria |
| **Licensing** | 🟡 **Semi-open** — ARC publishes some shelter guides publicly. Detailed operational toolkits may require ARC volunteer/partner access. |
| **Direct URLs** | |
| | • ARC Disaster Services: https://www.redcross.org/about-us/our-work/disaster-relief.html |
| | • ARC Shelter Training: https://www.redcross.org/take-a-class/shelter |
| | • ARC Volunteer (to access materials): https://www.redcross.org/volunteer/volunteer-opportunities/disaster-volunteer.html |
| **AI Training Suitability** | **MEDIUM** — Shelter management procedures are structured and sequential but not publicly available in full detail. The site selection criteria and shelter operations checklists are the most useful for VR scenarios. Shelter registration processes can inform VR mass care scenarios. |

---

### 8.5 State/Local Emergency Operations Plans (EOPs)

| Field | Details |
|---|---|
| **Full Name** | State and Local Emergency Operations Plans (EOPs) — with Comprehensive Preparedness Guide (CPG) 101 |
| **Hosting Organization** | Individual state/county/city emergency management agencies, guided by FEMA CPG 101 |
| **Domain** | Jurisdictional emergency response planning — defines local response procedures, resource allocation, mutual aid, evacuation zones |
| **Format** | **PDF** (plans), **GIS data** (evacuation zones, shelter locations), **HTML** (state EM websites) |
| **Machine-Readable** | ⚠️ **PARTIAL** — Some states publish GIS evacuation zone data. Plans are typically PDF. Resource inventories may be in database format. |
| **Decision Trees / Branching Logic** | ✅ **YES** — EOPs define activation levels (normal → elevated → partial activation → full activation), evacuation zone triggers, resource escalation procedures, mutual aid activation criteria |
| **Licensing** | 🟢 **Generally public** — Most EOPs are public records, though some sections may be restricted for security (e.g., critical infrastructure) |
| **Direct URLs** | |
| | • FEMA CPG 101 (Planning Guide): https://www.fema.gov/emergency-managers/national-preparedness/plan/cpg-101 |
| | • Example — California State EOP: https://www.caloes.ca.gov/office-of-the-director/operations/planning-preparedness-prevention/planning-preparedness/state-of-california-emergency-plan/ |
| | • Example — New York State CEMP: https://www.dhses.ny.gov/comprehensive-emergency-management-plan |
| | • Example — Texas State EOP: https://tdem.texas.gov/state-operations-center/ |
| | • (Note: Most state EM agency websites publish their plans publicly) |
| **AI Training Suitability** | **MEDIUM-HIGH** — EOPs provide jurisdiction-specific response procedures that can inform geographically-realistic VR scenarios. Activation level definitions provide scenario difficulty/escalation frameworks. Evacuation zone GIS data enables spatially-accurate VR environments. Mutual aid procedures define multi-agency coordination scenarios. CPG 101 provides the meta-framework for all emergency planning. |

---

## Supplementary Sources

### S.1 OpenMRS — Open Medical Record System

| Field | Details |
|---|---|
| **Full Name** | OpenMRS (Open Medical Record System) |
| **Hosting Organization** | OpenMRS Inc. (501(c)(3) nonprofit) |
| **Domain** | Open-source electronic medical record platform — patient data, clinical forms, FHIR APIs |
| **Format** | **Java application**, **REST API**, **FHIR API**, **JSON**, **MySQL database** |
| **Machine-Readable** | ✅ **YES** — Fully machine-readable. REST and FHIR APIs. Structured clinical concepts via CIEL dictionary. |
| **Decision Trees / Branching Logic** | ⚠️ **PARTIAL** — OpenMRS stores clinical data, not protocols. However, clinical decision support modules exist within the ecosystem. |
| **Licensing** | 🟢 **Open-source** — Mozilla Public License 2.0 |
| **Direct URLs** | |
| | • Homepage: https://openmrs.org/ |
| | • GitHub: https://github.com/openmrs |
| | • Demo: https://openmrs.org/demo/ |
| | • Technical Overview: https://openmrs.atlassian.net/wiki/spaces/docs/pages/25476856/Technical+Overview |
| | • FHIR APIs: documented at openmrs.org |
| **AI Training Suitability** | **MEDIUM** — Not directly a protocol source, but the CIEL clinical concept dictionary and FHIR-based clinical data structures provide standardized medical terminologies and patient record schemas. Could be used to generate synthetic patient records for VR scenarios. 15M+ patient records across 8000+ facilities in 70+ countries. The concept dictionary maps to standard terminologies (SNOMED, ICD, LOINC). |

---

### S.2 WISER — Wireless Information System for Emergency Responders

| Field | Details |
|---|---|
| **Full Name** | WISER (Wireless Information System for Emergency Responders) |
| **Hosting Organization** | National Library of Medicine (NLM) / HHS |
| **Domain** | HAZMAT identification, substance information, treatment protocols for chemical emergencies |
| **Format** | **Mobile app** (iOS/Android), **Web application**, linked to CHEMM |
| **Machine-Readable** | ⚠️ **PARTIAL** — App-based with structured substance database |
| **Decision Trees / Branching Logic** | ✅ **YES** — Substance identification logic, treatment protocols |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • WISER: https://wiser.nlm.nih.gov/ |
| | • WISER/CHEMM App link: referenced at https://chemm.hhs.gov/ |
| **AI Training Suitability** | **HIGH** — Substance identification database with treatment protocols. Complements CHEMM for HAZMAT VR scenarios. |

---

### S.3 CDC Field Triage Guidelines

| Field | Details |
|---|---|
| **Full Name** | Guidelines for Field Triage of Injured Patients (CDC/MMWR) |
| **Hosting Organization** | CDC (Centers for Disease Control and Prevention) |
| **Domain** | Field triage decision scheme for trauma patients — determines transport destination |
| **Format** | **HTML** (MMWR publication), **PDF** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Published as structured guidelines with decision steps |
| **Decision Trees / Branching Logic** | ✅ **YES** — Four-step triage decision scheme (physiologic → anatomic → mechanism → special considerations) |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • CDC Field Triage: https://www.cdc.gov/mmwr/preview/mmwrhtml/rr5801a1.htm |
| **AI Training Suitability** | **HIGH** — Clean four-step decision scheme that determines trauma center level routing. Directly encodable as FSM. Complements START/SALT by adding transport destination logic. |

---

### S.4 RITN — Radiation Injury Treatment Network

| Field | Details |
|---|---|
| **Full Name** | Radiation Injury Treatment Network (RITN) Triage & Treatment Guidelines |
| **Hosting Organization** | National Marrow Donor Program (NMDP) / RITN |
| **Domain** | Radiation injury triage, cytokine administration guidelines, ARS treatment |
| **Format** | **PDF** (triage cards in 4x6, 8.5x11, 24x36 poster sizes), **HTML** |
| **Machine-Readable** | ⚠️ **PARTIAL** — Structured triage cards |
| **Decision Trees / Branching Logic** | ✅ **YES** — Cytokine administration decision tree, ARS severity grading |
| **Licensing** | 🟢 **Open** — Freely available |
| **Direct URLs** | |
| | • Triage Guidelines: https://ritn.net/triage/ |
| | • 4x6 Card (PDF): https://ritn.net/-/media/project/nmdp/ritn/documents/triage/ritn-m00018-cytokine-administration-triage-guidelines-4x6-2020-11-24.pdf |
| | • 8.5x11 (PDF): https://ritn.net/-/media/project/nmdp/ritn/documents/triage/ritn-m00018-cytokine-administration-triage-guidelines-8-5x11-2020-11-24.pdf |
| | • ARS Treatment Guidelines (PDF): https://remm.hhs.gov/RITN-ARS-Treatment-Guidelines-21Oct-FINAL.pdf |
| | • RITN Center Locations: https://ritn.net/about/participating-hospital-locations |
| **AI Training Suitability** | **HIGH** — Compact triage decision cards for radiation-specific treatment. Can be encoded as supplementary decision trees for nuclear/radiological VR scenarios. |

---

### S.5 AFRRI — Armed Forces Radiobiology Research Institute

| Field | Details |
|---|---|
| **Full Name** | AFRRI Biodosimetry Assessment Tool (BAT) & Medical Management of Radiological Casualties Handbook |
| **Hosting Organization** | Uniformed Services University (USU) / AFRRI |
| **Domain** | Military radiation casualty management |
| **Format** | **PDF** (handbook), **software tool** (BAT) |
| **Machine-Readable** | ⚠️ **PARTIAL** — BAT is a software tool; handbook is PDF |
| **Decision Trees / Branching Logic** | ✅ **YES** — BAT contains biodosimetry assessment algorithms |
| **Licensing** | 🟢 **Public domain** — US Military/Government |
| **Direct URLs** | |
| | • BAT: https://afrri.usuhs.edu/research-assessment-of-radiation-injury |
| | • Handbook (4th Ed, PDF): https://afrri.usuhs.edu/sites/default/files/2020-07/4edmmrchandbook.pdf |
| **AI Training Suitability** | **MEDIUM-HIGH** — Military-grade radiation casualty protocols. The BAT tool's assessment algorithms can inform radiation VR scenarios. |

---

### S.6 ORISE/REAC/TS — Radiation Emergency Assistance

| Field | Details |
|---|---|
| **Full Name** | Oak Ridge Institute for Science and Education / Radiation Emergency Assistance Center/Training Site |
| **Hosting Organization** | DOE / ORISE / ORAU |
| **Domain** | Prehospital radiological triage, radiation patient treatment |
| **Format** | **PDF** (algorithm posters, handbooks) |
| **Machine-Readable** | ❌ **NO** — PDF flowcharts |
| **Decision Trees / Branching Logic** | ✅ **YES** — Prehospital radiological triage algorithm, radiation patient treatment algorithm |
| **Licensing** | 🟢 **Public domain** — US Government |
| **Direct URLs** | |
| | • Prehospital Radiological Triage v1.1 (PDF): https://orise.orau.gov/resources/reacts/documents/prehospital-radiological-triage-poster.pdf |
| | • Radiation Patient Treatment v3.1 (PDF): https://orise.orau.gov/resources/reacts/documents/radiation-patient-treatment-algorithm.pdf |
| | • Medical Aspects of Radiation Incidents (PDF): https://orise.orau.gov/resources/reacts/documents/medical-aspects-of-radiation-incidents.pdf |
| **AI Training Suitability** | **HIGH** — Clean, poster-format algorithms specifically designed for field use. Simple enough to digitize and encode. |

---

## Summary Comparison Matrix

| # | Source | Domain | Format | Machine-Readable | Decision Trees | Open License | AI Suitability |
|---|---|---|---|---|---|---|---|
| **Focus Area 1: EMS / EMT / Triage** | | | | | | | |
| 1.1 | NEMSIS v3.5.1 | EMS Data | XSD/XML/TXT/API | ✅ Full | ❌ Data, not protocols | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 1.2 | SALT Triage | MCI Triage | PNG/PDF/HTML | ⚠️ Partial | ✅ Core decision tree | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 1.3 | START Triage | MCI Triage | GIF/PDF/HTML | ⚠️ Partial | ✅ Core decision tree | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 1.4 | JumpSTART | Pediatric Triage | GIF/PDF/HTML | ⚠️ Partial | ✅ Core decision tree | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 1.5 | NHTSA EMS Ed Standards | EMS Education | PDF | ❌ No | ⚠️ Partial | ✅ Public domain | ⭐⭐⭐ |
| 1.6 | NREMT Exam/Skills | EMS Certification | PDF/HTML | ⚠️ Partial | ✅ Checklists | 🟡 Partial | ⭐⭐⭐⭐ |
| 1.7 | NASEMSO Model Guidelines | EMS Protocols | PDF | ❌ No | ✅ Full protocols | 🟡 Semi-open | ⭐⭐⭐⭐⭐ |
| 1.8 | NY State Protocols | State EMS | PDF | ❌ No | ✅ Full protocols | ✅ Public domain | ⭐⭐⭐⭐ |
| 1.9 | CA EMSA Guidelines | State EMS | PDF/DOCX | ⚠️ Partial | ✅ Yes | ✅ Public domain | ⭐⭐⭐ |
| 1.10 | NAEMSP | EMS Medical Dir. | PDF/HTML | ❌ No | ⚠️ Partial | 🟡 Mixed | ⭐⭐⭐ |
| 1.11 | PHTLS/ITLS | Trauma | Textbook | ❌ No | ✅ Full | 🔴 Copyright | ⭐⭐ (concept only) |
| 1.12 | EMS.gov Resources | Federal EMS | PDF/HTML | ❌ No | Varies | ✅ Public domain | ⭐⭐⭐ |
| **Focus Area 2: MCI Protocols** | | | | | | | |
| 2.1 | CHEMM | Chemical Emergency | HTML/JS/PDF | ⚠️ Partial (JS!) | ✅ **Extensive** | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 2.2 | REMM | Radiation Emergency | HTML/JS/PDF/App | ⚠️ Partial (JS!) | ✅ **Extensive** | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 2.3 | FEMA ICS | Incident Command | PDF (fillable) | ⚠️ Partial | ✅ Command trees | ✅ Public domain | ⭐⭐⭐⭐ |
| 2.4 | ASPR TRACIE | Healthcare Prep | PDF/HTML | ❌ No | ⚠️ Partial | ✅ Public domain | ⭐⭐⭐ |
| 2.5 | WHO MCI Guidelines | International MCI | PDF | ❌ No | ✅ Yes | 🟢 CC-IGO | ⭐⭐⭐ |
| **Focus Area 3: Clinical Protocols** | | | | | | | |
| 3.1 | AHA ACLS/BLS/PALS | Cardiac/Resus | PDF/App | ❌ No | ✅ **Core algorithms** | 🔴 Copyright | ⭐⭐⭐⭐⭐ (concept) |
| 3.2 | ATLS | Trauma | Textbook | ❌ No | ✅ ABCDE framework | 🔴 Copyright | ⭐⭐⭐ (concept) |
| **Focus Area 4: Firefighting SOPs** | | | | | | | |
| 4.1 | NFPA 1001 | FF Qualifications | PDF/HTML | ❌ No | ✅ JPR structure | 🔴 Copyright | ⭐⭐⭐⭐ (structure) |
| 4.2 | NFPA 1500 | FF Safety | PDF/HTML | ❌ No | ✅ Risk framework | 🔴 Copyright | ⭐⭐⭐⭐ |
| 4.3 | NFPA 1561 | Fire ICS | PDF/HTML | ❌ No | ✅ Command decisions | 🔴 Copyright | ⭐⭐⭐⭐ |
| 4.4 | NFPA 1710 | Deployment | PDF/HTML | ❌ No | ⚠️ Partial | 🔴 Copyright | ⭐⭐⭐ |
| 4.5 | IFSTA Essentials | FF Training | Textbook/App | ❌ No | ✅ Skill checklists | 🔴 Copyright | ⭐⭐⭐⭐ (structure) |
| 4.6 | IFSAC/Pro Board | FF Certification | PDF | ⚠️ Partial | ✅ Skill sheets | 🟡 Semi-open | ⭐⭐⭐⭐ |
| 4.7 | NIOSH FFFIPP | FF Fatality Invest. | HTML/PDF/DB | ⚠️ Partial | ✅ Implicit | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 4.8 | Structural FF SOPs | Fire Operations | PDF/HTML | ⚠️ Partial | ✅ Full procedures | 🟢 Generally public | ⭐⭐⭐⭐⭐ |
| 4.9 | NWCG 10/18/LCES | Wildland Fire | PDF/HTML/Cards | ⚠️ Partial | ✅ Rules & triggers | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 4.10 | USFA/NFA | Fire Training/Data | PDF/HTML/DB | ⚠️ Partial | ⚠️ Partial | ✅ Public domain | ⭐⭐⭐⭐ |
| **Focus Area 5: ICS Protocols** | | | | | | | |
| 5.1 | ICS Forms (201-260) | Incident Mgmt | Fillable PDF | ✅ Partial (fields) | ✅ Info flow | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 5.2 | IS-100/200/700/800 | ICS Training | HTML/PDF/SCORM | ⚠️ Partial | ✅ Decision frameworks | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 5.3 | NQS PTBs | Position Eval | Fillable PDF | ⚠️ Partial | ✅ Task checklists | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 5.4 | ICS Job Aids | Quick Reference | PDF | ⚠️ Partial | ✅ Multiple | ✅ Public domain | ⭐⭐⭐⭐ |
| 5.5 | NWCG Standards | Wildland Fire ICS | PDF/HTML | ⚠️ Partial | ✅ Qualification trees | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 5.6 | FIRESCOPE | ICS Origin Docs | PDF | ❌ No | ✅ Position checklists | ✅ Public domain | ⭐⭐⭐⭐ |
| **Focus Area 6: HAZMAT Response** | | | | | | | |
| 6.1 | ERG 2024 | HAZMAT Field Guide | PDF/App/XLSX | ✅ Partial (.xlsx) | ✅ **Extensive** | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 6.2 | OSHA HAZWOPER | HAZMAT Regulation | HTML/PDF | ⚠️ Partial | ✅ PPE levels, zones | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 6.3 | NIOSH NPG | Chemical Hazards | HTML/PDF/App | ✅ Yes (web DB) | ⚠️ Structured data | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 6.4 | CAMEO/ALOHA | Chemical Emerg. | App/DB/Web/GIS | ✅ Yes (database) | ✅ Reactivity rules | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 6.5 | WISER | HAZMAT ID | App/Web | ⚠️ Partial | ✅ ID decision tree | ✅ Public domain | ⭐⭐⭐⭐ |
| 6.6 | UN GHS | Chemical Class. | PDF/HTML/XML | ✅ Partial (XML) | ✅ Classification tree | ✅ Public domain | ⭐⭐⭐⭐ |
| **Focus Area 7: Search and Rescue** | | | | | | | |
| 7.1 | FEMA USAR FOG | Urban SAR | PDF | ❌ No | ✅ Search phases | ✅ Public domain | ⭐⭐⭐⭐ |
| 7.2 | INSARAG Guidelines | International SAR | PDF/Word | ⚠️ Partial | ✅ Operational checklists | ✅ Open (UN) | ⭐⭐⭐⭐⭐ |
| 7.3 | NASAR Programs | Land SAR | LMS/PDF | ❌ No | ✅ Management protocols | 🔴 Fee-based | ⭐⭐⭐ (concept) |
| 7.4 | Water Rescue SOPs | Swiftwater/Dive | PDF/Training | ❌ No | ✅ Reach-throw-row-go | 🔴 Mixed | ⭐⭐⭐ |
| **Focus Area 8: Evacuation & Civil Defense** | | | | | | | |
| 8.1 | FEMA Evacuation Guides | Evacuation | PDF | ❌ No | ✅ Decision matrix | ✅ Public domain | ⭐⭐⭐⭐ |
| 8.2 | CERT Training | Community Prep | PDF/PPT/HTML | ⚠️ Partial | ✅ Procedural | ✅ Public domain | ⭐⭐⭐⭐⭐ |
| 8.3 | NRF & ESFs | National Response | PDF | ⚠️ Partial | ✅ Activation criteria | ✅ Public domain | ⭐⭐⭐⭐ |
| 8.4 | ARC Shelter Mgmt | Shelter Ops | PDF/Training | ❌ No | ✅ Checklists | 🟡 Semi-open | ⭐⭐⭐ |
| 8.5 | State/Local EOPs | Local Response | PDF/GIS | ⚠️ Partial | ✅ Activation levels | ✅ Generally public | ⭐⭐⭐ |
| **Supplementary Sources** | | | | | | | |
| S.1 | OpenMRS | Medical Records | JSON/REST/FHIR | ✅ Full | ⚠️ Data, not protocols | ✅ Open source | ⭐⭐⭐ |
| S.2 | WISER | HAZMAT | App/Web | ⚠️ Partial | ✅ Yes | ✅ Public domain | ⭐⭐⭐⭐ |
| S.3 | CDC Field Triage | Trauma Triage | HTML/PDF | ⚠️ Partial | ✅ 4-step scheme | ✅ Public domain | ⭐⭐⭐⭐ |
| S.4 | RITN Guidelines | Radiation | PDF | ⚠️ Partial | ✅ Yes | ✅ Open | ⭐⭐⭐⭐ |
| S.5 | AFRRI BAT/Handbook | Military Rad | PDF/Software | ⚠️ Partial | ✅ Yes | ✅ Public domain | ⭐⭐⭐ |
| S.6 | ORISE REAC/TS | Radiation | PDF (posters) | ❌ No | ✅ Yes | ✅ Public domain | ⭐⭐⭐⭐ |

---

## Recommendations for AI Training Pipeline

### Tier 1: Immediate High-Value Sources (encode first)

| Priority | Source | Action | Output Format |
|---|---|---|---|
| 🥇 1 | **START Triage** | Manually encode from CHEMM text version | JSON decision tree / FSM |
| 🥇 2 | **SALT Triage** | Manually encode from CHEMM text version | JSON decision tree / FSM |
| 🥇 3 | **JumpSTART** | Manually encode from CHEMM text version | JSON decision tree / FSM |
| 🥇 4 | **CHEMM-IST 2.0** | Download offline ZIP → extract JavaScript → reverse-engineer IF-THEN rules | Rule engine / knowledge graph |
| 🥇 5 | **REMM Algorithms** | Download offline version → extract decision logic from HTML/JS | FSM / decision tree collection |
| 🥇 6 | **NEMSIS XSD** | Download XSD ZIP → parse into ontology | OWL/RDF knowledge graph |
| 🥇 7 | **ERG 2024** | Request .xlsx source files → parse guide pages, isolation distance tables, UN/NA index | Database + decision tree |
| 🥇 8 | **NWCG 10/18/LCES** | Encode fire orders, watch out situations, LCES checklists from NWCG web | Rule engine / conditional triggers |
| 🥇 9 | **ICS Forms (all)** | Parse fillable PDF field definitions + forms booklet | Data schema / ontology |
| 🥇 10 | **NIOSH NPG** | Scrape online chemical database into structured records | Chemical hazard knowledge graph |

### Tier 2: High-Value Sources (encode second)

| Priority | Source | Action | Output Format |
|---|---|---|---|
| 🥈 11 | **CDC Field Triage** | Encode 4-step triage decision scheme | JSON decision tree |
| 🥈 12 | **NREMT Skill Sheets** | Extract from public test plans + sample items | Procedural checklists (JSON) |
| 🥈 13 | **OSHA HAZWOPER** | Encode PPE levels A-D, zone system, training levels | Decision trees + classification |
| 🥈 14 | **CERT Training (IS-317)** | Extract unit objectives, skill procedures | Training module framework |
| 🥈 15 | **CAMEO Chemicals** | Export chemical datasheets + reactivity rules | Chemical database + rules |
| 🥈 16 | **NQS Position Task Books** | Parse PTBs for all ICS positions | Competency checklists (JSON) |
| 🥈 17 | **INSARAG Guidelines Vol III** | Extract operational field guide checklists | SAR procedure checklists |
| 🥈 18 | **NIOSH FFFIPP Reports** | NLP extraction of contributing factors + recommendations | Negative-example training data |
| 🥈 19 | **IS-100/200/700/800** | Extract course content, assessment questions | ICS knowledge base |
| 🥈 20 | **NY State Protocols** | NLP extraction from PDF | Protocol knowledge base |
| 🥈 21 | **AHA ACLS/BLS/PALS** | Encode algorithm structure from published evidence (respect copyright) | Decision trees (reference only) |
| 🥈 22 | **CHEMM Patient Care Guides** | Parse chemical-specific prehospital/hospital treatment pages | Treatment protocol database |
| 🥈 23 | **NRF & ESFs** | Encode 15 ESF definitions, activation criteria | Coordination framework ontology |
| 🥈 24 | **UN GHS** | Encode classification criteria, hazard categories, pictogram mappings | Classification decision tree |

### Tier 3: Supplementary Sources

| Priority | Source | Action | Output Format |
|---|---|---|---|
| 🥉 25 | **NEMSIS Research Dataset** | Request 2024 public-release dataset | Training data for ML models |
| 🥉 26 | **CA EMSA Guidelines** | Extract DOCX versions | Structured text protocols |
| 🥉 27 | **NASEMSO Model Guidelines** | Obtain and parse | Comprehensive protocol library |
| 🥉 28 | **RITN/AFRRI/ORISE** | Encode radiation-specific triage | Specialized decision trees |
| 🥉 29 | **OpenMRS CIEL Dictionary** | Extract clinical concept mappings | Medical terminology ontology |
| 🥉 30 | **ASPR TRACIE Resources** | Index documents by scenario type | Scenario planning reference |
| 🥉 31 | **USFA/NFIRS/NERIS Data** | Access incident data for scenario generation | Statistical models, scenario templates |
| 🥉 32 | **FIRESCOPE FOG** | Extract position checklists, ICS procedures | ICS reference procedures |
| 🥉 33 | **NFPA 1001 JPRs** | Reference JPR structure for evaluation rubrics | Competency framework |
| 🥉 34 | **State/Local EOPs** | Sample representative plans for scenario design | Activation level frameworks |
| 🥉 35 | **NASAR SAR Concepts** | Encode lost person behavior models, POA/POD | Search management algorithms |
| 🥉 36 | **FEMA USAR FOG** | Extract search phases, marking system | SAR procedure library |

### Recommended AI Training Architecture (Updated)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         VR SIMULATION ENGINE                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                 │
│  │   SCENARIO     │  │  PROCEDURAL   │  │  EVALUATION   │                 │
│  │   GENERATOR    │  │  TRAINER      │  │  ENGINE       │                 │
│  └───────┬────────┘  └───────┬───────┘  └───────┬───────┘                 │
│          │                   │                   │                         │
├──────────┼───────────────────┼───────────────────┼─────────────────────────┤
│          ▼                   ▼                   ▼                         │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                      KNOWLEDGE LAYER                                 │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │                                                                      │ │
│  │  TRIAGE TREES (FSMs):       FIREFIGHTING PROCEDURES:                 │ │
│  │  • START/SALT/JumpSTART     • Size-Up (COAL WAS WEALTH)             │ │
│  │  • CHEMM-IST syndrome ID    • Strategy (Offensive/Defensive)         │ │
│  │  • REMM radiation triage    • NWCG 10/18/LCES rules                 │ │
│  │  • CDC Field Triage         • RIT/MAYDAY protocols                   │ │
│  │  • BLS/ACLS frameworks      • CAN reporting                         │ │
│  │                                                                      │ │
│  │  HAZMAT KNOWLEDGE:          ICS FRAMEWORK:                           │ │
│  │  • ERG lookup tables        • ICS Forms schema (201-260)            │ │
│  │  • CAMEO Chemicals DB       • NQS Position Task Books               │ │
│  │  • NIOSH NPG database       • IS-100/200/700/800 content           │ │
│  │  • HAZWOPER PPE levels      • NWCG qualification system            │ │
│  │  • GHS classification       • Incident type scaling (5→1)          │ │
│  │  • ALOHA dispersion model   • FIRESCOPE FOG procedures             │ │
│  │                                                                      │ │
│  │  SAR PROTOCOLS:             EVACUATION / CIVIL DEFENSE:              │ │
│  │  • FEMA USAR search phases  • NRF & 15 ESFs                        │ │
│  │  • INSARAG guidelines       • Evacuate vs. Shelter-in-Place         │ │
│  │  • USAR marking system      • CERT training modules                 │ │
│  │  • Reach-throw-row-go       • EOPs activation levels               │ │
│  │  • Lost person behavior     • Shelter management procedures         │ │
│  │                                                                      │ │
│  │  KNOWLEDGE GRAPHS:          TRAINING / EVALUATION DATA:              │ │
│  │  • NEMSIS EMS ontology      • NEMSIS 2024 dataset (11.5M records)   │ │
│  │  • Chemical agents DB       • NIOSH FFFIPP incident reports (400+)  │ │
│  │  • ICS org hierarchy        • USFA/NFIRS/NERIS fire incident data   │ │
│  │  • NFPA 1001 JPR framework  • NREMT skill checklists               │ │
│  │  • NWCG position system     • IFSAC/Pro Board certification sheets  │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

Data Flow:
1. SCENARIO GENERATOR uses knowledge graphs + incident data to create
   realistic emergency scenarios across all domains (fire, HAZMAT, SAR, MCI,
   evacuation) with appropriate environmental conditions and resource constraints
2. PROCEDURAL TRAINER uses FSM decision trees + protocol databases to guide
   trainees through correct step-by-step procedures for their role and domain
3. EVALUATION ENGINE uses NREMT/IFSAC/NFPA skill checklists + NQS PTBs +
   NIOSH incident analysis to score performance with branching feedback,
   identifying critical failures and providing corrective guidance
```

### Key Technical Approaches by Source (Updated)

| Source | Knowledge Representation | AI Technique | Domain |
|---|---|---|---|
| START/SALT/JumpSTART | Finite State Machines | Rule-based evaluation, RL reward shaping | Triage |
| CHEMM-IST | IF-THEN rules (expert system) | Knowledge graph, inference engine | Chemical MCI |
| REMM Algorithms | Decision trees with temporal logic | FSM + time-dependent state transitions | Radiation |
| ERG 2024 | Lookup tables + guide decision tree | Database query + branching logic | HAZMAT |
| NIOSH NPG | Structured chemical records | Knowledge graph, substance identification | HAZMAT |
| CAMEO/ALOHA | Chemical DB + dispersion models | Threat zone estimation, reactivity prediction | HAZMAT |
| OSHA HAZWOPER | PPE decision tree + zone system | Classification + rule engine | HAZMAT Safety |
| NWCG 10/18/LCES | Rule sets + conditional triggers | Real-time safety monitoring | Wildland Fire |
| NIOSH FFFIPP | Root cause analysis templates | NLP extraction → negative-example training | Fire Safety |
| NFPA 1001 JPRs | Competency matrices | Evaluation rubric framework | Fire Training |
| NEMSIS XSD/Data | Ontology + statistical models | Supervised fine-tuning, scenario generation | EMS |
| ICS Forms 201-260 | Structured data schemas | Information architecture, form generation | Incident Mgmt |
| NQS PTBs | Sequential task checklists | Procedural FSM evaluation | ICS Positions |
| IS-100/200/700/800 | Hierarchical knowledge base | Assessment generation, concept mapping | ICS Knowledge |
| INSARAG Guidelines | Operational checklists + classification | SAR procedure evaluation | Int'l SAR |
| USAR FOG | Search phase protocols | Phase-based scenario progression | Urban SAR |
| NRF / ESFs | Coordination taxonomy | Multi-agency scenario generation | Civil Defense |
| CERT Training | Unit-based curriculum | Beginner VR module scaffolding | Community Prep |
| NREMT Skills | Sequential checklists with critical points | Procedural evaluation, FSM | EMS Skills |
| AHA Algorithms | Flowchart decision trees | FSM, prompt-based evaluation | Cardiac |
| ICS Structure | Organizational hierarchy | Hierarchical knowledge graph | Command |

### Domain Coverage Summary

| Domain | Sources Available | Open/Public Sources | Top Encodable Resource |
|---|---|---|---|
| **Triage** | 5 (START, SALT, JumpSTART, CDC, CHEMM-IST) | ✅ All open | CHEMM-IST (JS-extractable rules) |
| **Structural Firefighting** | 6 (NFPA 1001/1500/1561, IFSTA, NIOSH, SOPs) | 🟡 Mixed (NFPA copyrighted) | NIOSH FFFIPP + department SOPs |
| **Wildland Firefighting** | 3 (NWCG, USFA, FIRESCOPE) | ✅ All open | NWCG IRPG + 10/18/LCES |
| **Incident Command** | 6 (ICS Forms, IS courses, NQS, Job Aids, NWCG, FIRESCOPE) | ✅ All open | ICS Forms + NQS PTBs |
| **HAZMAT** | 6 (ERG, HAZWOPER, NPG, CAMEO, WISER, GHS) | ✅ All open | ERG 2024 + CAMEO Chemicals |
| **Chemical/Radiation MCI** | 3 (CHEMM, REMM, RITN) | ✅ All open | CHEMM offline ZIP + REMM tools |
| **Urban SAR** | 2 (FEMA USAR, INSARAG) | ✅ All open | INSARAG Vol III (field guide) |
| **Land/Water SAR** | 2 (NASAR, water rescue SOPs) | 🔴 Mostly fee-based | Reach-throw-row-go framework |
| **Evacuation** | 3 (FEMA guides, NRF/ESFs, State EOPs) | ✅ All open | NRF ESF taxonomy |
| **Community Preparedness** | 2 (CERT, ARC) | 🟢 Mostly open | CERT IS-317/IS-315 |
| **EMS Clinical** | 8 (NASEMSO, state protocols, NHTSA, NREMT, etc.) | 🟢 Mostly open | NASEMSO Model Guidelines |
| **Cardiac/Resuscitation** | 2 (AHA, ATLS) | 🔴 Copyrighted | AHA algorithm structure (concepts) |

---

*This research document was compiled on 2026-03-03 by searching and analyzing the following URLs and their linked resources:*

**Round 1 (EMS/MCI/Clinical — initial research):**
- *https://www.ems.gov*
- *https://www.nremt.org*
- *https://chemm.hhs.gov*
- *https://remm.hhs.gov*
- *https://www.who.int/publications*
- *https://www.nasemso.org*
- *https://www.naemsp.org*
- *https://nemsis.org*
- *https://asprtracie.hhs.gov*
- *https://training.fema.gov*
- *https://www.health.ny.gov/professionals/ems/*
- *https://emsa.ca.gov/guidelines/*
- *https://openmrs.org*
- *https://ritn.net*
- *https://afrri.usuhs.edu*
- *https://orise.orau.gov*
- *https://www.cdc.gov/mmwr/*

**Round 2 (Firefighting/ICS/HAZMAT/SAR/Evacuation — expanded research):**
- *https://www.nfpa.org (redirected; content referenced from standards documentation)*
- *https://training.fema.gov/emiweb/is/icsresource/ (forms, job aids, training materials)*
- *https://training.fema.gov/emiweb/is/icsresource/icsforms*
- *https://training.fema.gov/emiweb/is/icsresource/jobaids*
- *https://training.fema.gov/emiweb/is/icsresource/trainingmaterials*
- *https://www.phmsa.dot.gov/hazmat/outreach-training/erg*
- *https://www.nwcg.gov (rendered as SPA; content referenced from NWCG publication catalog)*
- *https://www.insarag.org*
- *https://www.insarag.org/methodology/insarag-guidelines/*
- *https://wiser.nlm.nih.gov*
- *https://www.ready.gov (redirected; CERT content accessed via fema.gov)*
- *https://fema.gov/cert*
- *https://www.usfa.fema.gov*
- *https://www.ifsta.org*
- *https://www.nasar.org*
- *https://www.epa.gov/cameo*
- *https://www.epa.gov/cameo/what-cameo-software-suite*
- *https://cameochemicals.noaa.gov*
- *https://www.cdc.gov/niosh/npg/*
- *https://www.cdc.gov/niosh/fire/*
- *https://www.osha.gov/hazardous-waste (403; content referenced from regulation text)*
- *https://www.osha.gov/laws/regs/regulations/standardnumber/1910/1910.120*
- *https://firescope.caloes.ca.gov*
- *https://www.fema.gov/national-qualification-system*
- *https://ifsac.org*
- *https://theproboard.org*
- *https://unece.org (GHS documentation)*
