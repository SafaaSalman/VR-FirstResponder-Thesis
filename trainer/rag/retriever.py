"""
RAG retriever – fetches grounding text from the protocol knowledge base.

Two retrieval modes:
 1. **Step-based** (primary) – given step IDs from the rule engine, return
    all chunks whose ``related_steps`` overlap.
 2. **Semantic** (fallback) – given free-text, rank chunks by cosine
    similarity using OpenAI embeddings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from openai import OpenAI

from trainer import config


class RAGRetriever:
    """Lightweight retriever over the protocol knowledge-base JSON."""

    def __init__(
        self,
        kb_path: Optional[Path] = None,
        client: Optional[OpenAI] = None,
    ) -> None:
        self.client = client or OpenAI(api_key=config.OPENAI_API_KEY)
        kb_path = kb_path or (
            config.KNOWLEDGE_BASE_DIR / "earthquake_evacuation_kb.json"
        )
        with open(kb_path, encoding="utf-8") as f:
            data = json.load(f)
        self.chunks: List[dict] = data["chunks"]
        self._chunk_index: Dict[str, dict] = {
            c["chunk_id"]: c for c in self.chunks
        }
        # Lazy-loaded embeddings (only computed on first semantic query)
        self._embeddings: Optional[np.ndarray] = None

    # ── Step-based retrieval (deterministic) ───────────────────────────────

    def retrieve_by_steps(
        self, step_ids: List[str], top_k: int = 0
    ) -> List[dict]:
        """Return chunks whose ``related_steps`` overlap with *step_ids*."""
        step_set = set(step_ids)
        hits = [
            c
            for c in self.chunks
            if step_set & set(c.get("related_steps", []))
        ]
        if top_k > 0:
            hits = hits[:top_k]
        return hits

    def retrieve_by_constraint(self, constraint_id: str) -> List[dict]:
        """Return chunks tagged with a specific global constraint."""
        return [
            c
            for c in self.chunks
            if constraint_id in c.get("related_constraints", [])
        ]

    def retrieve_by_action(self, action_id: str) -> List[dict]:
        """Return chunks that reference a forbidden/special action."""
        return [
            c
            for c in self.chunks
            if action_id in c.get("related_actions", [])
        ]

    # ── Semantic retrieval (embedding-based) ───────────────────────────────

    def _ensure_embeddings(self) -> None:
        """Compute and cache embeddings for all chunks (one API call)."""
        if self._embeddings is not None:
            return
        texts = [c["text"] for c in self.chunks]
        resp = self.client.embeddings.create(
            model=config.EMBEDDING_MODEL, input=texts
        )
        vecs = [item.embedding for item in resp.data]
        self._embeddings = np.array(vecs, dtype=np.float32)

    def retrieve_by_query(
        self, query: str, top_k: int = 0
    ) -> List[dict]:
        """Rank chunks by cosine similarity to *query*."""
        top_k = top_k or config.RAG_TOP_K
        self._ensure_embeddings()
        resp = self.client.embeddings.create(
            model=config.EMBEDDING_MODEL, input=[query]
        )
        q_vec = np.array(resp.data[0].embedding, dtype=np.float32)

        # Cosine similarity
        norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(
            q_vec
        )
        norms = np.where(norms == 0, 1e-10, norms)
        sims = (self._embeddings @ q_vec) / norms

        top_indices = np.argsort(sims)[::-1][:top_k]
        return [self.chunks[i] for i in top_indices]

    # ── Combined retrieval (used by the chat pipeline) ─────────────────────

    def retrieve_for_result(
        self,
        step_ids: Optional[List[str]] = None,
        constraint_id: Optional[str] = None,
        action_id: Optional[str] = None,
        query: Optional[str] = None,
        top_k: int = 0,
    ) -> List[dict]:
        """
        Smart retrieval: try step-based first, fall back to constraint,
        action, then semantic.  De-duplicates by chunk_id.
        """
        top_k = top_k or config.RAG_TOP_K
        seen: set[str] = set()
        results: List[dict] = []

        def _add(chunks: List[dict]) -> None:
            for c in chunks:
                cid = c["chunk_id"]
                if cid not in seen:
                    seen.add(cid)
                    results.append(c)

        if step_ids:
            _add(self.retrieve_by_steps(step_ids, top_k=top_k))
        if constraint_id:
            _add(self.retrieve_by_constraint(constraint_id))
        if action_id:
            _add(self.retrieve_by_action(action_id))
        if query and len(results) < top_k:
            _add(self.retrieve_by_query(query, top_k=top_k - len(results)))

        return results[:top_k] if top_k else results

    # ── Helpers ────────────────────────────────────────────────────────────

    def format_chunks_for_prompt(self, chunks: List[dict]) -> str:
        """Format retrieved chunks into a string the LLM can consume."""
        if not chunks:
            return "(No supporting protocol text retrieved.)"
        parts = []
        for c in chunks:
            parts.append(
                f"[{c['chunk_id']}] {c['title']}\n{c['text']}"
            )
        return "\n\n".join(parts)
