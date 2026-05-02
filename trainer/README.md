# Procedural Training Engine – Chat Prototype

A protocol-driven training engine with an LLM on top.  
The system is **not** just a chatbot — it generates scenarios, tracks trainee
progress through a structured protocol, validates every action against a
deterministic rule engine, and uses RAG-grounded explanations.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key
cp .env.example .env
# Edit .env and paste your key

# 3a. Run CLI chat
python -m trainer

# Or pick a specific scenario
python -m trainer --scenario eq_blocked_route

# List available scenarios
python -m trainer --list-scenarios

# 3b. Run Web UI (admin/debug interface)
python -m uvicorn trainer.web.server:app --reload --port 8000
# Then open http://localhost:8000 in your browser
```

## Virsual Env

cd "c:\Users\pcs\Desktop\Folders\Uni\Thesis\Code\VR-FirstResponder-Thesis"

# Create a virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate

# Install dependencies inside the env
pip install -r requirements.txt

## Architecture

```
trainee text
     │
     ▼
┌──────────────────┐
│  Action Parser   │  (LLM – maps text to action IDs)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Rule Engine    │  (Deterministic – validates against protocol)
│                  │  → valid / invalid / skipped / critical error
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   RAG Retriever  │  (Fetches supporting protocol text for evidence)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   LLM Response   │  (Generates natural language using rule result + RAG)
│   Generator      │  → The LLM NEVER decides protocol correctness
└──────────────────┘
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **A – Protocol Knowledge Base** | `knowledge_base/*.json` | Source paragraphs for RAG retrieval and debrief |
| **B – Structured Protocol** | `protocols/*.json` | Steps, decisions, preconditions, constraints |
| **C – Scenario State Engine** | `engine/state.py` | Tracks world state + trainee progress |
| **D – Rule Engine** | `engine/rule_engine.py` | Validates actions, detects violations |
| **E – LLM Layer** | `llm/interface.py` | Natural language generation (guided by rules) |
| **F – RAG Layer** | `rag/retriever.py` | Grounded evidence retrieval |
| **G – Evaluation Layer** | `engine/scoring.py` | Deterministic scoring across 5 dimensions |

### Supporting Modules

| Module | Purpose |
|--------|---------|
| `llm/action_parser.py` | LLM-based intent extraction from trainee text |
| `engine/hints.py` | 3-level hint system (gentle → direct → explicit) |
| `engine/debrief.py` | Structured debrief assembly for LLM generation |

## Chat Commands

| Command | Action |
|---------|--------|
| *(any text)* | Describe your action in the scenario |
| `hint` / `help` | Get a progressive hint (auto-escalates) |
| `status` | Show current progress |
| `score` | Show current scores |
| `debrief` | Generate after-action debrief |
| `quit` | End session with debrief |

## Scenarios

| ID | Name | Difficulty |
|----|------|-----------|
| `eq_standard` | Standard earthquake evacuation | Beginner |
| `eq_moderate_injury` | Earthquake with injured persons | Intermediate |
| `eq_blocked_route` | Blocked primary route + smoke | Advanced |

## Scoring Dimensions

1. **Sequence Adherence** (25%) – Did you follow the correct step order?
2. **Critical Compliance** (30%) – Did you complete mandatory safety steps?
3. **Branch Correctness** (15%) – Did you take the right path for the scenario?
4. **Hazard Awareness** (15%) – Did you assess routes, aftershocks, etc.?
5. **Completion Quality** (15%) – Did you finish end-phase steps?

## Example Interaction

```
[Trainer] A powerful earthquake strikes while you are on the 3rd floor
of the Riverside Community Center. Tables overturn, glass shatters,
decorations crash to the floor. People around you scream. The building
shakes violently. What do you do?

You > I drop under the nearest table and hold on

[Trainer] Good. You've taken cover under a sturdy table and are holding
on. The shaking continues — stay where you are until it completely stops.
What do you do next?

You > I run to the elevator to get out fast

[Trainer] Using the elevator is not permitted during an earthquake
evacuation. The protocol requires waiting for shaking to stop, assessing
surroundings, and evacuating via stairs. Elevators may become unsafe due
to power or structural failure. What would you like to do instead?
```

## Next Steps (Future Work)

- **Adaptability**: Learner model tracks per-step mastery → scenario
  generator targets weak areas in future sessions
- **VR Integration**: Replace chat interface with Unity VR events
- **Multi-protocol**: Add SALT triage, fire evacuation, HAZMAT SOPs
- **Voice Input**: NLU layer for spoken trainee commands
