# VR First Responder Thesis

A deterministic + LLM hybrid procedural training engine for first-responder
SOPs, plus the supporting VR / literature research that frames it.

## Repository layout

```
.
├── trainer/              Procedural training engine (Python)
│   ├── engine/           Deterministic core (rule engine, scoring, hints, debrief)
│   ├── llm/              LLM-facing modules (action parser, narration interface)
│   ├── rag/              Retrieval-Augmented Generation over the protocol KB
│   ├── protocols/        Protocol JSON graphs
│   ├── scenarios/        Scenario definitions (initial state + narrative)
│   ├── knowledge_base/   Retrieval corpus
│   └── web/              FastAPI admin / debug UI
│
├── docs/                 Background research (lit review, platform notes, drawio)
├── datasets/             Protocol-research source material
│
├── requirements.txt
└── .env.example
```

## Quick start (procedural trainer)

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
copy .env.example .env             # then paste your OPENAI_API_KEY

# CLI
python -m trainer
python -m trainer --scenario eq_blocked_route
python -m trainer --list-scenarios

# Web UI (admin / debug)
python -m uvicorn trainer.web.server:app --reload --port 8000
# open http://localhost:8000
```
