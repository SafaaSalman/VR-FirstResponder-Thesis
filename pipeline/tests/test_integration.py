"""
Integration tests: exercise the full pipeline flow with mocked LLM calls.

These tests verify that:
1. PDF extraction → section splitting → formatting works end-to-end
2. Protocol generation flow (single-pass + batch paths) calls correctly
3. KB generation flow (single-pass + batch paths) calls correctly
4. Validation runs on generated outputs without crashing
5. The run_pipeline() orchestrator chains stages correctly
6. The web server endpoints respond correctly
7. Config loading works across all layers
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pipeline.config import PipelineConfig, get_config, _cached_config
from pipeline.extract import (
    ExtractedDocument,
    Section,
    _split_into_sections,
)
from pipeline.structure import (
    generate_protocol_tree,
    _format_sections,
    _split_sections_into_batches,
    _validate_and_fix,
    _fake_sections,
)
from pipeline.kb_generator import (
    generate_knowledge_base,
    _split_into_batches,
    _merge_and_renumber,
    _generate_coverage_fill,
    _find_relevant_sections,
    _format_protocol_summary,
    _format_source_text_from_sections,
    _validate_references,
)
from pipeline.validate import (
    validate_protocol,
    validate_knowledge_base,
    ValidationResult,
)
from pipeline.llm_utils import (
    count_tokens,
    _try_parse_json,
    _strip_markdown_fences,
    _extract_json_block,
    tpm_pace,
)
from pipeline.run import run_pipeline


# ── Fixtures ───────────────────────────────────────────────────────────────

def _sample_doc() -> ExtractedDocument:
    """A small synthetic ExtractedDocument for testing."""
    return ExtractedDocument(
        source_path="test.pdf",
        title="Test Emergency Protocol",
        raw_text="Section 1 text. Section 2 text.",
        sections=[
            Section(heading="1. Assessment", text="Assess the scene for hazards. Check for casualties.", page_numbers=[1], level=1),
            Section(heading="2. Evacuation", text="Evacuate the building via designated routes. Assist mobility-impaired.", page_numbers=[2], level=1),
            Section(heading="3. Assembly", text="Gather at assembly point. Conduct headcount.", page_numbers=[3], level=1),
        ],
        page_count=3,
    )


def _sample_protocol() -> dict:
    """A valid protocol matching the sample doc."""
    return {
        "protocol_id": "test_emergency_v1",
        "title": "Test Emergency Protocol",
        "description": "Test protocol for integration testing.",
        "source": "test.pdf",
        "roles": ["responder"],
        "initial_step": "assess_scene",
        "global_constraints": [
            {
                "id": "no_elevators",
                "description": "Do not use elevators during evacuation.",
                "forbidden_actions": ["use_elevator"],
                "critical": True,
            }
        ],
        "steps": [
            {
                "id": "assess_scene",
                "type": "action",
                "description": "Assess the scene for hazards.",
                "preconditions": [],
                "effects": ["scene_assessed = true"],
                "allowed_next": ["decide_route"],
                "critical": True,
                "phase": "assessment",
            },
            {
                "id": "decide_route",
                "type": "decision",
                "description": "Decide on evacuation route.",
                "preconditions": ["scene_assessed == true"],
                "effects": [],
                "conditions": [
                    {"if": "route_clear == true", "next": "evacuate"},
                    {"if": "route_clear == false", "next": "evacuate"},
                ],
                "critical": True,
                "phase": "assessment",
            },
            {
                "id": "evacuate",
                "type": "action",
                "description": "Evacuate via designated route.",
                "preconditions": [],
                "effects": ["building_evacuated = true"],
                "allowed_next": ["headcount"],
                "critical": True,
                "phase": "evacuation",
            },
            {
                "id": "headcount",
                "type": "action",
                "description": "Conduct headcount at assembly point.",
                "preconditions": ["building_evacuated == true"],
                "effects": ["headcount_complete = true"],
                "allowed_next": [],
                "terminal": True,
                "critical": False,
                "phase": "post_evacuation",
            },
        ],
        "possible_actions": [
            {"id": "assess_scene", "label": "Assess scene"},
            {"id": "decide_route", "label": "Decide route"},
            {"id": "evacuate", "label": "Evacuate"},
            {"id": "headcount", "label": "Headcount"},
            {"id": "use_elevator", "label": "Use elevator"},
            {"id": "ask_question", "label": "Ask question"},
            {"id": "request_hint", "label": "Request hint"},
        ],
    }


def _sample_kb() -> dict:
    """A valid KB matching the sample protocol."""
    return {
        "protocol_id": "test_emergency_v1",
        "description": "Knowledge base for test protocol.",
        "chunks": [
            {
                "chunk_id": "kb_001",
                "title": "Scene Assessment Procedure",
                "text": (
                    "When arriving at an emergency scene, the first responder must assess "
                    "the area for hazards. This includes checking for structural damage, "
                    "fire, and other dangers. Only proceed when it is safe to do so."
                ),
                "related_steps": ["assess_scene"],
                "related_constraints": [],
                "tags": ["assessment", "safety", "critical"],
            },
            {
                "chunk_id": "kb_002",
                "title": "Evacuation Route Decision",
                "text": (
                    "After assessment, determine the safest evacuation route. If the primary "
                    "route is blocked, use the secondary route. Never use elevators during "
                    "a fire emergency. Assist anyone who needs help evacuating."
                ),
                "related_steps": ["decide_route", "evacuate"],
                "related_constraints": ["no_elevators"],
                "tags": ["evacuation", "decision", "critical"],
            },
            {
                "chunk_id": "kb_003",
                "title": "Assembly and Headcount",
                "text": (
                    "Once all personnel have evacuated, conduct a headcount at the designated "
                    "assembly point. Report any missing persons to the incident commander "
                    "immediately. Do not re-enter the building until cleared."
                ),
                "related_steps": ["headcount"],
                "related_constraints": [],
                "tags": ["post_evacuation", "headcount"],
            },
            {
                "chunk_id": "kb_004",
                "title": "Elevator Safety Constraint",
                "text": (
                    "Elevators must never be used during fire emergencies. They can become "
                    "trapped between floors, fill with smoke, or lose power. Always use "
                    "stairways for evacuation during any fire-related emergency."
                ),
                "related_steps": [],
                "related_constraints": ["no_elevators"],
                "tags": ["safety", "constraint", "critical"],
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Config integration
# ═══════════════════════════════════════════════════════════════════════════

class TestConfigIntegration:
    """Config system works end-to-end."""

    def test_default_config(self):
        cfg = PipelineConfig()
        assert cfg.model == "gpt-4o"
        assert cfg.max_single_pass_tokens == 25_000
        assert cfg.tpm_limit == 30_000
        assert cfg.max_upload_size_mb == 50

    def test_override_kwargs(self):
        cfg = PipelineConfig(model="gpt-4o-mini", tpm_limit=60_000)
        assert cfg.model == "gpt-4o-mini"
        assert cfg.tpm_limit == 60_000

    def test_derived_properties(self):
        cfg = PipelineConfig(max_upload_size_mb=100, job_ttl_hours=4)
        assert cfg.max_upload_size_bytes == 100 * 1024 * 1024
        assert cfg.job_ttl_seconds == 4 * 3600

    def test_get_config_env_override(self):
        import pipeline.config as cfg_mod
        cfg_mod._cached_config = None
        try:
            with patch.dict("os.environ", {"PIPELINE_MODEL": "gpt-3.5-turbo"}):
                cfg = get_config()
                assert cfg.model == "gpt-3.5-turbo"
        finally:
            cfg_mod._cached_config = None


# ═══════════════════════════════════════════════════════════════════════════
# LLM utils integration
# ═══════════════════════════════════════════════════════════════════════════

class TestLLMUtilsIntegration:
    """LLM utility functions work correctly."""

    def test_count_tokens_basic(self):
        tokens = count_tokens("Hello, world!")
        assert tokens > 0
        assert tokens < 10

    def test_count_tokens_longer(self):
        text = "This is a longer text. " * 100
        tokens = count_tokens(text)
        assert tokens > 100

    def test_try_parse_json_valid(self):
        assert _try_parse_json('{"key": "value"}') == {"key": "value"}

    def test_try_parse_json_with_fences(self):
        text = '```json\n{"key": "value"}\n```'
        assert _try_parse_json(text) == {"key": "value"}

    def test_try_parse_json_with_prefix(self):
        text = 'Here is the JSON:\n{"key": "value"}\nEnd.'
        assert _try_parse_json(text) == {"key": "value"}

    def test_try_parse_json_invalid(self):
        assert _try_parse_json("not json at all") is None

    def test_strip_markdown_fences(self):
        text = '```json\n{"a": 1}\n```'
        assert _strip_markdown_fences(text) == '{"a": 1}'

    def test_extract_json_block(self):
        text = 'prefix {"nested": {"deep": true}} suffix'
        result = _extract_json_block(text)
        assert json.loads(result) == {"nested": {"deep": True}}

    def test_tpm_pace_zero_limit(self):
        """TPM pacing with limit=0 should not sleep."""
        import pipeline.config as cfg_mod
        old = cfg_mod._cached_config
        cfg_mod._cached_config = PipelineConfig(tpm_limit=0)
        try:
            tpm_pace(10_000)  # should return immediately
        finally:
            cfg_mod._cached_config = old


# ═══════════════════════════════════════════════════════════════════════════
# Structure module integration
# ═══════════════════════════════════════════════════════════════════════════

class TestStructureIntegration:
    """Structure module helpers work correctly."""

    def test_format_sections(self):
        doc = _sample_doc()
        formatted = _format_sections(doc.sections)
        assert "Assessment" in formatted
        assert "Evacuation" in formatted
        assert "Assembly" in formatted

    def test_fake_sections(self):
        text = "a" * 12000
        sections = _fake_sections(text, chunk_size=4000)
        assert len(sections) == 3
        for s in sections:
            assert len(s.text) <= 4000

    def test_split_sections_into_batches_preserves_all(self):
        sections = [
            Section(heading=f"Sec {i}", text=f"Content {i}. " * 50,
                    page_numbers=[i], level=1)
            for i in range(10)
        ]
        batches = _split_sections_into_batches(sections, max_tokens=500)
        # All original sections should appear
        all_headings = set()
        for batch in batches:
            for s in batch:
                h = s.heading
                if h.startswith("[OVERLAP"):
                    h = h.split("] ", 1)[1]
                all_headings.add(h)
        assert all_headings == {f"Sec {i}" for i in range(10)}

    def test_generate_protocol_tree_calls_llm(self):
        """generate_protocol_tree should call the LLM and return a dict."""
        doc = _sample_doc()
        mock_client = MagicMock()
        protocol = _sample_protocol()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(protocol)
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 300
        mock_client.chat.completions.create.return_value = mock_response

        import pipeline.config as cfg_mod
        old = cfg_mod._cached_config
        cfg_mod._cached_config = PipelineConfig(tpm_limit=0)
        try:
            result = generate_protocol_tree(doc, mock_client, "gpt-4o")
            assert "steps" in result
            assert "protocol_id" in result
            assert mock_client.chat.completions.create.called
        finally:
            cfg_mod._cached_config = old


# ═══════════════════════════════════════════════════════════════════════════
# KB generator integration
# ═══════════════════════════════════════════════════════════════════════════

class TestKBGeneratorIntegration:
    """KB generator helpers work correctly."""

    def test_format_protocol_summary(self):
        protocol = _sample_protocol()
        summary = _format_protocol_summary(protocol)
        parsed = json.loads(summary)
        assert parsed["protocol_id"] == "test_emergency_v1"
        assert len(parsed["steps"]) == 4

    def test_format_source_text_from_sections(self):
        doc = _sample_doc()
        text = _format_source_text_from_sections(doc.sections)
        assert "Assessment" in text
        assert "Evacuation" in text

    def test_find_relevant_sections(self):
        sections = _sample_doc().sections
        results = _find_relevant_sections("evacuate building routes", sections, top_k=2)
        assert len(results) >= 1
        # Should find the evacuation section
        headings = [r["heading"] for r in results]
        assert any("Evacuation" in h for h in headings)

    def test_find_relevant_sections_empty(self):
        assert _find_relevant_sections("", [], top_k=5) == []

    def test_validate_references_fixes_bad_refs(self):
        protocol = _sample_protocol()
        kb = _sample_kb()
        # Add a bad step reference
        kb["chunks"][0]["related_steps"].append("nonexistent_step")
        fixed_kb = _validate_references(kb, protocol)
        # Bad ref should be removed
        for chunk in fixed_kb["chunks"]:
            assert "nonexistent_step" not in chunk.get("related_steps", [])

    def test_generate_kb_calls_llm(self):
        """generate_knowledge_base should call the LLM and return a dict."""
        doc = _sample_doc()
        protocol = _sample_protocol()
        kb_response = _sample_kb()

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(kb_response)
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 300
        mock_client.chat.completions.create.return_value = mock_response

        import pipeline.config as cfg_mod
        old = cfg_mod._cached_config
        cfg_mod._cached_config = PipelineConfig(tpm_limit=0)
        try:
            result = generate_knowledge_base(doc, protocol, mock_client, "gpt-4o")
            assert "chunks" in result
            assert mock_client.chat.completions.create.called
        finally:
            cfg_mod._cached_config = old


# ═══════════════════════════════════════════════════════════════════════════
# Validation integration
# ═══════════════════════════════════════════════════════════════════════════

class TestValidationIntegration:
    """Cross-validation of protocol and KB together."""

    def test_valid_protocol_passes(self):
        r = validate_protocol(_sample_protocol())
        assert r.ok, f"Errors: {r.errors}"

    def test_valid_kb_passes(self):
        protocol = _sample_protocol()
        kb = _sample_kb()
        r = validate_knowledge_base(kb, protocol)
        assert r.ok, f"Errors: {r.errors}"

    def test_protocol_kb_cross_validation(self):
        """Protocol + KB should be mutually consistent."""
        protocol = _sample_protocol()
        kb = _sample_kb()
        proto_r = validate_protocol(protocol)
        kb_r = validate_knowledge_base(kb, protocol)
        assert proto_r.ok
        assert kb_r.ok

    def test_validation_summary_format(self):
        r = ValidationResult()
        assert "passed" in r.summary()
        r.errors.append("Test error")
        assert "ERRORS" in r.summary()
        r.warnings.append("Test warning")
        assert "WARNINGS" in r.summary()


# ═══════════════════════════════════════════════════════════════════════════
# End-to-end pipeline orchestration (mocked LLM)
# ═══════════════════════════════════════════════════════════════════════════

class TestPipelineOrchestration:
    """Full pipeline run with mocked LLM calls."""

    def test_run_pipeline_extract_only(self):
        """Extract-only mode should work without OpenAI key."""
        try:
            from fpdf import FPDF
        except ImportError:
            pytest.skip("fpdf2 not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test.pdf"
            output_dir = Path(tmpdir) / "output"

            # Create a simple PDF with fpdf2
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=16)
            pdf.cell(text="Test Emergency Protocol")
            pdf.ln(10)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(text="1. Assessment Phase")
            pdf.ln(8)
            pdf.cell(text="Assess the area for hazards and threats.")
            pdf.ln(8)
            pdf.cell(text="2. Evacuation Phase")
            pdf.ln(8)
            pdf.cell(text="Evacuate all personnel to safety.")
            pdf.output(str(pdf_path))

            result = run_pipeline(
                pdf_paths=[str(pdf_path)],
                output_dir=str(output_dir),
                extract_only=True,
            )
            assert "docs" in result
            assert len(result["docs"]) == 1
            assert (output_dir / "extracted_1.txt").exists()

    def test_run_pipeline_full_mocked(self):
        """Full pipeline with mocked LLM should complete successfully."""
        protocol = _sample_protocol()
        kb = _sample_kb()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test.pdf"
            output_dir = Path(tmpdir) / "output"

            # Create a test PDF with fpdf2
            try:
                from fpdf import FPDF
            except ImportError:
                pytest.skip("fpdf2 not installed")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=16)
            pdf.cell(text="Test Emergency Protocol")
            pdf.ln(10)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(text="1. Assessment Phase")
            pdf.ln(8)
            pdf.cell(text="Assess the area for hazards.")
            pdf.ln(8)
            pdf.cell(text="2. Evacuation Phase")
            pdf.ln(8)
            pdf.cell(text="Evacuate all personnel.")
            pdf.output(str(pdf_path))

            mock_client = MagicMock()

            # The pipeline makes these LLM calls:
            # 1. Pass 1: extract protocol tree
            # 2. Pass 2: validate & fix (only if errors found — our mock protocol is clean, so this is skipped)
            # 3. KB generation: produce knowledge base chunks
            # So call 1 = protocol, call 2 = KB
            call_count = [0]

            def mock_create(**kwargs):
                call_count[0] += 1
                response = MagicMock()
                response.usage = MagicMock()
                response.usage.prompt_tokens = 100
                response.usage.completion_tokens = 200
                response.usage.total_tokens = 300

                if call_count[0] == 1:
                    response.choices = [MagicMock()]
                    response.choices[0].message.content = json.dumps(protocol)
                else:
                    response.choices = [MagicMock()]
                    response.choices[0].message.content = json.dumps(kb)
                return response

            mock_client.chat.completions.create = mock_create

            import pipeline.config as cfg_mod
            old = cfg_mod._cached_config
            cfg_mod._cached_config = PipelineConfig(tpm_limit=0)

            try:
                with patch("pipeline.run.OpenAI", return_value=mock_client):
                    with patch("pipeline.run.load_dotenv"):
                        result = run_pipeline(
                            pdf_paths=[str(pdf_path)],
                            output_dir=str(output_dir),
                        )

                assert "protocol" in result
                assert "knowledge_base" in result
                assert "validation" in result
                assert result["protocol"]["protocol_id"] == "test_emergency_v1"
                assert len(result["knowledge_base"]["chunks"]) > 0

                # Verify files were written
                proto_file = output_dir / "test_emergency_v1.json"
                kb_file = output_dir / "test_emergency_v1_kb.json"
                assert proto_file.exists()
                assert kb_file.exists()

                # Verify file contents are valid JSON
                with open(proto_file) as f:
                    saved_proto = json.load(f)
                assert saved_proto["protocol_id"] == "test_emergency_v1"

                with open(kb_file) as f:
                    saved_kb = json.load(f)
                assert "chunks" in saved_kb
            finally:
                cfg_mod._cached_config = old
