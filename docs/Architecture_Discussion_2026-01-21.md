# XR First Responder Training System - Architecture Discussion

**Date:** January 21, 2026  
**Document Type:** Architecture Planning Session  
**Status:** Initial Design Phase

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Components](#2-system-components)
3. [Architecture Design](#3-architecture-design)
4. [Domain Configuration System](#4-domain-configuration-system)
5. [Patient Representation System](#5-patient-representation-system)
6. [Technology Stack Analysis](#6-technology-stack-analysis)
7. [Cost Analysis](#7-cost-analysis)
8. [Asset Generation Pipeline](#8-asset-generation-pipeline)
9. [Timeline](#9-timeline)
10. [Recommendations](#10-recommendations)
11. [Next Steps](#11-next-steps)

---

## 1. Project Overview

### 1.1 Objective

Build a Mixed Reality (MR) training system for first responders in the **disaster management preparation stage**. The system will help EMTs, firefighters, and other first responders train to handle emergency situations through immersive, AI-powered simulations.

### 1.2 Core AI Components

| Component | Purpose | Interaction Type |
|-----------|---------|------------------|
| **Scenario Generator** | Generate training scenarios (text) | Offline → feeds into system |
| **Art Generator** | Generate XR assets/environments | Offline → feeds into Unity |
| **Virtual Patient (LLM)** | Interactive NPC in MR | Real-time conversation |
| **Virtual Trainer (LLM)** | Guidance/evaluation in MR | Real-time conversation |

### 1.3 Key Requirements

- **Platform:** Microsoft HoloLens 2 (Mixed Reality)
- **Interaction:** Voice-based communication with patient and trainer
- **Modularity:** Architecture must support multiple domains (EMT, Firefighter, Police, HAZMAT)
- **Budget:** Open-source preferred; commercial solutions considered if quality impact significant
- **Timeline:** Flexible (up to 2 years)

### 1.4 Starting Domain: EMT (Medical First Responder)

**Rationale:**
- Most structured data available (triage protocols, vital signs, symptom databases)
- Clear interaction pattern (patient assessment is conversational - perfect for LLM)
- Less visual complexity (no fire simulation, physics - focus on dialogue & decisions)
- Rich datasets available (medical dialogue datasets, symptom checkers, first aid protocols)
- MR advantage (overlay vitals, instructions on real mannequin or environment)

---

## 2. System Components

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOMAIN CONFIGURATION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│   │    EMT      │   │ FIREFIGHTER │   │   POLICE    │   │   HAZMAT    │    │
│   │   Config    │   │   Config    │   │   Config    │   │   Config    │    │
│   ├─────────────┤   ├─────────────┤   ├─────────────┤   ├─────────────┤    │
│   │• Protocols  │   │• Protocols  │   │• Protocols  │   │• Protocols  │    │
│   │• Scenarios  │   │• Scenarios  │   │• Scenarios  │   │• Scenarios  │    │
│   │• Assets     │   │• Assets     │   │• Assets     │   │• Assets     │    │
│   │• LLM Prompts│   │• LLM Prompts│   │• LLM Prompts│   │• LLM Prompts│    │
│   │• Eval Rules │   │• Eval Rules │   │• Eval Rules │   │• Eval Rules │    │
│   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CORE SERVICES LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    SCENARIO ENGINE                                  │    │
│  │  Generator (LLM) → Loader (JSON/YAML) → Runtime Manager            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    LLM ORCHESTRATOR                                 │    │
│  │   ┌─────────────────┐         ┌─────────────────┐                  │    │
│  │   │ PATIENT AGENT   │         │ TRAINER AGENT   │                  │    │
│  │   │ • Symptoms      │         │ • Guidance      │                  │    │
│  │   │ • Medical Hx    │         │ • Evaluation    │                  │    │
│  │   │ • Responses     │         │ • Protocol help │                  │    │
│  │   └────────┬────────┘         └────────┬────────┘                  │    │
│  │            └───────────┬───────────────┘                           │    │
│  │                        ▼                                           │    │
│  │              ┌─────────────────┐                                   │    │
│  │              │  SHARED CONTEXT │                                   │    │
│  │              │    MANAGER      │                                   │    │
│  │              └─────────────────┘                                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    SPEECH PIPELINE                                  │    │
│  │   [User Voice] → [STT] → [LLM Agent] → [TTS] → [Avatar/Audio]      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    EVALUATION ENGINE                                │    │
│  │   • Protocol adherence scoring    • Time tracking                  │    │
│  │   • Decision tree validation      • LLM-based feedback             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  HOLOLENS 2 APPLICATION (Unity + MRTK 3)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│   │   SPATIAL   │   │   AVATAR    │   │     UI      │   │   SCENE     │    │
│   │   ANCHORS   │   │   SYSTEM    │   │   OVERLAY   │   │   MANAGER   │    │
│   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  INTERACTION: Voice commands, Hand tracking, Gaze targeting         │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│   ┌─────────────────────┐              ┌─────────────────────┐             │
│   │    LLM SERVER       │              │   ASSET SERVICE     │             │
│   │  Local or Cloud     │              │  Pre-generated +    │             │
│   │  Llama / Azure      │              │  On-demand          │             │
│   └─────────────────────┘              └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture Design

### 3.1 Design Principles

1. **Domain Agnostic Core:** The core system should work across different first responder domains
2. **Plugin-based Knowledge:** Domain-specific knowledge loaded via configuration
3. **Flexible Representation:** Support both full 3D avatars and overlay modes
4. **Offline-First Training:** Fine-tuning and asset generation happen offline
5. **Real-time Inference:** Patient/trainer interactions must be low-latency

### 3.2 Data Flow

```
1. PREPARATION PHASE (Offline)
   ├── Fine-tune LLM on first responder protocols
   ├── Generate scenarios using fine-tuned model
   ├── Generate/collect assets for scenarios
   └── Package domain configuration

2. RUNTIME PHASE (Real-time)
   ├── Load domain configuration
   ├── Initialize scenario from JSON/YAML
   ├── Spawn patient representation (3D or overlay)
   ├── Speech loop: User → STT → LLM → TTS → Avatar
   ├── Track actions and evaluate performance
   └── Provide trainer guidance when needed

3. POST-SESSION PHASE
   ├── Generate performance report
   ├── LLM-based qualitative feedback
   └── Export data for analysis
```

---

## 4. Domain Configuration System

### 4.1 Configuration Schema

```yaml
# domain_config/emt.yaml
domain:
  id: "emt_basic"
  name: "Emergency Medical Technician - Basic"
  version: "1.0"

protocols:
  - id: "patient_assessment"
    name: "Primary Patient Assessment"
    steps:
      - "Scene safety check"
      - "Determine responsiveness"
      - "Airway assessment"
      - "Breathing assessment"
      - "Circulation assessment"
    time_limit_seconds: 120
    
  - id: "start_triage"
    name: "START Triage Protocol"
    steps:
      - "Can patient walk? → Minor (Green)"
      - "Check respirations"
      - "Check perfusion"
      - "Check mental status"

scenarios:
  database: "scenarios/emt/"
  generation_prompt: |
    Generate an EMT training scenario with:
    - Patient demographics, chief complaint, medical history
    - Environmental context
    - Correct triage category
    - Expected actions and timeline

patient_agent:
  system_prompt: |
    You are a patient in an emergency medical scenario.
    Your condition: {scenario.patient_condition}
    Symptoms: {scenario.symptoms}
    Pain level: {scenario.pain_level}/10
    Medical history: {scenario.medical_history}
    
    Respond naturally to the EMT's questions.
    Show appropriate distress based on your condition.
    Only reveal information when directly asked.
    If asked about pain, describe location and intensity.

trainer_agent:
  system_prompt: |
    You are an experienced EMT instructor observing a trainee.
    Current scenario: {scenario.summary}
    Correct protocol: {scenario.protocol}
    Trainee actions so far: {session.actions}
    
    Provide guidance when:
    - Trainee seems stuck (no action for 30+ seconds)
    - Trainee makes critical error
    - Trainee asks for help
    
    Style: Supportive but realistic. Use Socratic method.

evaluation:
  scoring:
    protocol_adherence: 0.4
    time_efficiency: 0.2
    communication_quality: 0.2
    patient_outcome: 0.2
  
  critical_failures:
    - "Missed airway obstruction"
    - "Ignored scene safety"
    - "Wrong triage category"
```

### 4.2 Extensibility

To add a new domain (e.g., Firefighter):

1. Create `domain_config/firefighter.yaml`
2. Define domain-specific protocols
3. Create scenario generation prompts
4. Define patient/trainer system prompts
5. Configure evaluation criteria
6. Prepare domain-specific assets

---

## 5. Patient Representation System

### 5.1 Three Representation Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **Mode A: Full 3D Avatar** | Complete humanoid model with lip-sync, body language, wound visualization | Remote training, no physical equipment |
| **Mode B: Overlay on Mannequin** | QR/Spatial anchor on real mannequin, holographic vitals/wounds/symptoms | Skills lab, haptic feedback needed |
| **Mode C: Hybrid** | 3D avatar for upper body/face, real props for hands-on, overlay for wounds | Advanced scenarios, realism + immersion |

### 5.2 Implementation Interface

```csharp
public interface IPatientRepresentation
{
    void Initialize(PatientData patient, Transform anchor);
    void UpdateCondition(PatientCondition condition);
    void PlaySpeech(AudioClip speech, string text);
    void ShowWound(WoundData wound);
    void ShowVitals(VitalSigns vitals);
    void Dispose();
}

public class FullAvatarRepresentation : IPatientRepresentation { }
public class OverlayRepresentation : IPatientRepresentation { }
public class HybridRepresentation : IPatientRepresentation { }

public class PatientRepresentationFactory
{
    public IPatientRepresentation Create(RepresentationMode mode) { }
}
```

### 5.3 Mode Selection Criteria

Mode selected at scenario start based on:
- Training environment (classroom vs field)
- Available equipment (mannequin present?)
- Scenario type (mass casualty → overlay, single patient → 3D)
- User preference

---

## 6. Technology Stack Analysis

### 6.1 LLM Services Comparison

| Solution | Setup | Latency | Monthly Cost | Quality | Fine-tuning |
|----------|-------|---------|--------------|---------|-------------|
| **Azure OpenAI (GPT-4o)** | Low | ~500ms | $50-200 | Excellent | Limited |
| **OpenAI API (GPT-4o)** | Low | ~500ms | $50-200 | Excellent | Yes (expensive) |
| **Anthropic Claude** | Low | ~600ms | $50-150 | Excellent | No |
| **Llama 3.1 70B (cloud)** | Medium | ~800ms | $30-100 | Very Good | Yes |
| **Llama 3.1 8B (local)** | High | ~200ms | $0 | Good | Full control |
| **Mistral 7B (local)** | High | ~150ms | $0 | Good | Full control |

### 6.2 Speech Services Comparison

| Solution | STT Quality | TTS Quality | Monthly Cost | HoloLens Integration |
|----------|-------------|-------------|--------------|---------------------|
| **Azure Speech** | Excellent | Excellent | $20-80 | Native, seamless |
| **Google Cloud Speech** | Excellent | Excellent | $20-80 | Good |
| **Whisper + XTTS v2** | Excellent | Very Good | $0 | Manual integration |
| **Whisper + Coqui TTS** | Excellent | Good | $0 | Manual integration |

### 6.3 Art Generation Tools

| Solution | Output Type | Quality | Cost |
|----------|-------------|---------|------|
| **Stable Diffusion XL** | 2D textures, images | Very Good | $0 |
| **DALL-E 3** | 2D images | Excellent | $0.04-0.08/image |
| **Meshy.ai** | 3D models | Good | $20/mo or free tier |
| **Tripo3D** | 3D models | Good | Free tier |
| **Blockade Labs** | 360° Skyboxes | Very Good | Free tier |

### 6.4 Compute for Training

| Platform | GPU | Cost | Best For |
|----------|-----|------|----------|
| **Google Colab Free** | T4 | $0 | Prototyping |
| **Google Colab Pro** | T4/V100 | $10/mo | Regular training |
| **Kaggle** | P100/T4 | $0 | Training runs |
| **University GPU** | Varies | $0 | Heavy training |

---

## 7. Cost Analysis

### 7.1 Scenario A: Maximum Open Source ($0/month)

| Component | Solution |
|-----------|----------|
| LLM | Llama 3.1 8B local/Colab |
| Speech | Whisper + XTTS v2 |
| Art | Stable Diffusion + free assets |
| Compute | Kaggle + Colab Free |

**Trade-offs:** More development time, potential quality limitations in speech naturalness

### 7.2 Scenario B: Strategic Spend (~$80/month)

| Component | Solution | Cost |
|-----------|----------|------|
| LLM | Llama 3.1 (local) + Azure OpenAI fallback | ~$30 |
| Speech | Azure Speech Services | ~$40 |
| Art | Stable Diffusion + Meshy free | $0 |
| Compute | Colab Pro + Kaggle | $10 |

**Best balance:** Professional quality speech, open-source LLM with cloud backup

### 7.3 Scenario C: Quality Priority (~$210/month)

| Component | Solution | Cost |
|-----------|----------|------|
| LLM | Azure OpenAI GPT-4o | ~$100 |
| Speech | Azure Speech Services | ~$50 |
| Art | Midjourney + Meshy Pro | ~$50 |
| Compute | Colab Pro | $10 |

**2-year total:** ~$5,000

---

## 8. Asset Generation Pipeline

### 8.1 Asset Sourcing Strategy

```
PHASE 1: IDENTIFY NEEDED ASSETS
  From scenario config, extract:
  • Environment type (street, building, outdoor)
  • Required props (medical equipment, hazards)
  • Patient appearance (wounds, symptoms, demographics)
  • Ambient elements (weather, time of day)

PHASE 2: SOURCE ASSETS (Priority Order)

  1. EXISTING FREE ASSETS
     ├── Unity Asset Store (free section)
     ├── Sketchfab (CC licensed)
     ├── Poly Pizza (free 3D)
     ├── Kenney Assets (game assets)
     └── Quaternius (free characters)

  2. AI-GENERATED (for gaps)
     ├── Textures/Materials → Stable Diffusion
     ├── Wound overlays → Stable Diffusion
     ├── Skyboxes → Blockade Labs
     ├── Simple 3D props → Meshy.ai
     └── UI elements → DALL-E / SD

  3. PROCEDURAL (runtime)
     ├── Terrain variations
     ├── Debris placement
     └── Wound appearance variations

PHASE 3: PROCESSING FOR HOLOLENS
  • Optimize poly count (~100k tris/scene max)
  • Compress textures (max 1024x1024)
  • Set up LODs for complex models
  • Configure MRTK shaders
```

### 8.2 EMT Scenario Asset Needs

| Category | Free Sources | AI-Generate If Needed |
|----------|--------------|----------------------|
| Medical equipment | Unity Asset Store, Sketchfab | Meshy.ai |
| Patient avatar | Mixamo, ReadyPlayerMe | SD textures |
| Wounds/injuries | Create as 2D overlays | Stable Diffusion |
| Environment | Modular kits | Blockade Labs skyboxes |
| UI/HUD elements | Design in Unity | SD for icons |

---

## 9. Timeline

### 9.1 Phase 1: Foundation (Months 1-6)

| Period | Focus |
|--------|-------|
| Months 1-2 | Literature review, architecture finalization |
| Months 3-4 | HoloLens 2 + MRTK 3 setup, basic speech integration |
| Months 5-6 | Domain config system, scenario loader |

**Milestone:** Working MR app with basic speech interaction

### 9.2 Phase 2: Core Development (Months 7-12)

| Period | Focus |
|--------|-------|
| Months 7-8 | LLM fine-tuning for scenario generation |
| Months 9-10 | Patient agent integration, avatar system |
| Months 11-12 | Trainer agent, evaluation engine |

**Milestone:** Complete EMT training scenario playable

### 9.3 Phase 3: Polish & Evaluation (Months 13-18)

| Period | Focus |
|--------|-------|
| Months 13-14 | Asset generation pipeline, visual polish |
| Months 15-16 | User studies with EMT trainees |
| Months 17-18 | Second domain proof (optional), refinements |

**Milestone:** Validated system with user study data

### 9.4 Phase 4: Thesis (Months 19-24)

| Period | Focus |
|--------|-------|
| Months 19-21 | Thesis writing |
| Months 22-23 | Revisions |
| Month 24 | Defense preparation |

---

## 10. Recommendations

### 10.1 Recommended Technology Stack

| Component | Primary Choice | Fallback | Rationale |
|-----------|---------------|----------|-----------|
| **XR Platform** | HoloLens 2 + MRTK 3 | - | Requirement |
| **LLM (training)** | Llama 3.1 70B on Kaggle/Colab | - | Free, fine-tunable |
| **LLM (inference)** | Llama 3.1 8B local server | Azure OpenAI | Cost vs quality |
| **STT** | Whisper (local or API) | Azure Speech | Quality similar |
| **TTS** | XTTS v2 or Azure Neural | - | Test both |
| **3D Assets** | Free stores + Meshy.ai | - | Practical, low cost |
| **2D/Textures** | Stable Diffusion XL | - | Free, local |
| **Patient Avatar** | Ready Player Me | - | Free, good quality |

### 10.2 Recommended Budget: Scenario B (~$80/month)

- Provides professional quality speech (Azure)
- Maintains flexibility with open-source LLM
- Manageable cost over 2 years (~$1,920 total)

---

## 11. Next Steps

### 11.1 Immediate Actions

1. **Budget Decision:** Confirm which cost scenario to pursue
2. **Speech Quality Test:** Set up comparison between Whisper+XTTS vs Azure Speech
3. **Avatar System Design:** Design flexible avatar system interface
4. **LLM Fine-tuning Strategy:** Determine data needs and fine-tuning approach
5. **Project Structure:** Update repository to reflect new architecture

### 11.2 Open Questions

1. Access to real EMT protocols/training materials?
2. University resources for HoloLens 2 devices?
3. IRB approval timeline for user studies?
4. Collaboration with EMT training programs?

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 21, 2026 | Initial architecture discussion |

---

*This document captures the architecture planning session for the XR First Responder Training System thesis project.*
