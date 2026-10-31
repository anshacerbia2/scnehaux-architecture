from tests.conftest import make_validator
import datetime
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, ".."))

from engine.validators.domains.isms_validator import ISMSValidator


def _isms_schema():
    with open(
        os.path.join(REPO_ROOT, "00-governance", "schemas", "isms.schema.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f)


def _meta(**overrides):
    meta = {
        "id": "ISMS-001",
        "title": "ISMS Scope and Context",
        "owner": "ISMS Owner",
        "version": "1.0.0",
        "status": "approved",
        "classification": "public",
        "governed_by": ["GDC-012"],
        "review_cycle_days": 365,
        "created_date": datetime.date.today(),
        "last_reviewed": datetime.date.today(),
        "isms_record": "scope-and-context",
        "iso_clauses": ["4.1", "4.3"],
        "annex_a_controls": ["A.5.9"],
    }
    meta.update(overrides)
    return meta


MAPPING = (
    "## 2. ISO/IEC 27001 Mapping\n\n"
    "This record is aligned with ISO/IEC 27001:2022. It answers clause 4.1 (Understanding "
    "the organization and its context), clause 4.3 (Determining the scope of the information "
    "security management system), and control A.5.9 (Inventory of information and other "
    "associated assets).\n\n"
)


def _content(meta, record_body, mapping=MAPPING):
    today = datetime.date.today().isoformat()
    return (
        "---\n"
        "doc_meta:\n"
        f"  id: {meta['id']}\n"
        f"  title: {meta['title']}\n"
        f"  owner: {meta['owner']}\n"
        "  version: 1.0.0\n"
        "  status: approved\n"
        "  classification: public\n"
        "  governed_by: [GDC-012]\n"
        "  review_cycle_days: 365\n"
        f"  created_date: {today}\n"
        f"  last_reviewed: {today}\n"
        "  isms_record: scope-and-context\n"
        '  iso_clauses: ["4.1", "4.3"]\n'
        '  annex_a_controls: ["A.5.9"]\n'
        "---\n\n"
        "# ISMS Scope and Context\n\n"
        "## 1. Purpose & Scope\n\n"
        "This record states the boundaries of the information security management system "
        "and the interfaces it shares with suppliers and cloud services.\n\n"
        f"{mapping}"
        "## 3. Record\n\n"
        f"{record_body}\n\n"
        "## 4. Review & Change Control\n\n"
        "The ISMS Owner reviews this record every 365 days and whenever the scope, a supplier, "
        "or a cloud service changes.\n"
    )


VALID_TABLE = (
    "| Control | Control status | Evidence | Justification |\n"
    "| :--- | :--- | :--- | :--- |\n"
    "| A.5.9 Inventory of information and other associated assets | `implemented` | "
    "[asset list](https://github.com/example/repo/blob/main/assets.md) | Scope boundary |\n"
    "| A.7.1 Physical security perimeters | not applicable | | No premises are in scope; "
    "all processing runs on cloud services. |"
)


def _validator(meta=None, record_body=VALID_TABLE, mapping=MAPPING, **kwargs):
    meta = meta or _meta()
    return make_validator(
        cls=ISMSValidator,
        file_path="/fake/07-isms/ISMS-001-scope-and-context.md",
        content=_content(meta, record_body, mapping),
        doc_meta=meta,
        domain_schema=_isms_schema(),
        filename="ISMS-001-scope-and-context.md",
        **kwargs,
    )


def _messages(v, rule_fragment=""):
    return [msg for sev, msg in v.errors if rule_fragment in msg]


# ---------- Full lifecycle against the real schema ----------


def test_isms_valid_record_passes_full_validation():
    v = _validator(
        all_doc_ids={"ISMS-001", "GDC-012"},
        all_doc_metadata={"ISMS-001": _meta()},
    )
    errors = v.validate()
    blocking = [(sev, msg) for sev, msg in errors if sev in ("CRITICAL", "ERROR")]
    assert blocking == []


def test_isms_schema_rejects_person_owner_and_non_public_classification():
    meta = _meta(
        owner="Jane Citizen",
        classification="internal",
        iso_clauses=[4.1],
        annex_a_controls=["A.5.38"],
        id="ISMS-1",
    )
    v = _validator(meta=meta, all_doc_ids={"GDC-012"})
    v._validate_schema()
    joined = " ".join(msg for _, msg in v.errors)
    assert "Jane Citizen" in joined
    assert "internal" in joined
    assert "A.5.38" in joined or "annex_a_controls" in joined
    assert "iso_clauses" in joined
    assert "ISMS-1" in joined or "id" in joined


def test_isms_schema_declares_lifecycle_and_classification():
    schema = _isms_schema()
    props = schema["definitions"]["metadata_rules"]["properties"]["doc_meta"]["allOf"][
        1
    ]["properties"]
    assert props["status"]["enum"] == ["draft", "proposed", "approved", "deprecated"]
    assert props["classification"]["enum"] == ["public"]
    kinds = props["isms_record"]["enum"]
    cadence = schema["x-isms-rules"]["record_review_cycle_max_days"]
    assert set(kinds) == set(cadence)


# ---------- Mapping ----------


def test_isms_requires_a_clause_or_control():
    v = _validator(meta=_meta(iso_clauses=[], annex_a_controls=[]))
    v.validate_type_specific()
    assert _messages(v, "declares neither")


def test_isms_mapping_ignores_non_list_values():
    v = _validator(meta=_meta(iso_clauses="4.1"))
    v.validate_type_specific()
    assert not _messages(v, "declares neither")
    assert not _messages(v, "not cited")


def test_isms_declared_reference_must_be_cited_exactly():
    mapping = (
        "## 2. ISO/IEC 27001 Mapping\n\n"
        "This record is aligned with ISO/IEC 27001:2022 and cites clause 4.10, clause 4.3, "
        "and control A.5.90 for illustration of prefix handling only.\n\n"
    )
    v = _validator(mapping=mapping)
    v.validate_type_specific()
    missing = _messages(v, "not cited")
    assert any("'4.1'" in m for m in missing)
    assert any("'A.5.9'" in m for m in missing)
    assert not any("'4.3'" in m for m in missing)


def test_isms_mapping_section_missing_is_left_to_schema():
    v = _validator(mapping="")
    v.validate_type_specific()
    assert not _messages(v, "not cited")


# ---------- Review cadence ----------


def test_isms_review_cadence_exceeded():
    v = _validator(meta=_meta(isms_record="risk-register", review_cycle_days=180))
    v.validate_type_specific()
    assert _messages(v, "at least every 90 days")


def test_isms_review_cadence_within_limit_and_non_integer_ignored():
    v = _validator(meta=_meta(isms_record="risk-register", review_cycle_days=90))
    v.validate_type_specific()
    assert not _messages(v, "at least every")

    v = _validator(meta=_meta(review_cycle_days=True))
    v.validate_type_specific()
    assert not _messages(v, "at least every")


# ---------- Single home ----------


def test_isms_single_home_conflict():
    registry = {
        "ISMS-001": _meta(),
        "ISMS-002": _meta(id="ISMS-002"),
        "ISMS-003": _meta(id="ISMS-003", status="deprecated"),
        "ISMS-004": _meta(id="ISMS-004", isms_record="other"),
        "GDC-012": {"id": "GDC-012"},
        "ISMS-005": "not-a-dict",
    }
    v = _validator(all_doc_metadata=registry)
    v.validate_type_specific()
    conflicts = _messages(v, "already has an active home")
    assert len(conflicts) == 1
    assert "ISMS-002" in conflicts[0]


def test_isms_single_home_skips_other_kind_and_deprecated_self():
    registry = {"ISMS-001": _meta(), "ISMS-002": _meta(id="ISMS-002")}
    v = _validator(meta=_meta(isms_record="other"), all_doc_metadata=registry)
    v.validate_type_specific()
    assert not _messages(v, "already has an active home")

    v = _validator(meta=_meta(status="deprecated"), all_doc_metadata=registry)
    v.validate_type_specific()
    assert not _messages(v, "already has an active home")


# ---------- Publication rules ----------


def test_isms_certification_claim_detected():
    body = VALID_TABLE + "\n\nThe organisation is ISO/IEC 27001:2022 certified."
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert _messages(v, "no certification claim")


def test_isms_alignment_wording_allowed():
    body = (
        VALID_TABLE
        + "\n\nThis ISMS is aligned with ISO/IEC 27001:2022 and prepared for an "
        "ISO/IEC 27001:2022 certification audit."
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert not _messages(v, "no certification claim")


def test_isms_personal_identifiers_detected():
    body = VALID_TABLE + "\n\nContact alice@example.com or @alice for questions."
    v = _validator(record_body=body)
    v.validate_type_specific()
    found = _messages(v, "never people")
    assert any("alice@example.com" in m for m in found)
    assert any("'@alice'" in m for m in found)


def test_isms_team_handle_is_not_a_personal_identifier():
    body = VALID_TABLE + "\n\nReviews route to @scnehaux/arb-team through CODEOWNERS."
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert not _messages(v, "never people")


def test_isms_reproduced_requirement_text_detected_outside_code():
    body = (
        VALID_TABLE
        + "\n\nThe organization shall determine external issues.\n\n"
        + "```text\nshall appears here only as an example\n```"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    found = _messages(v, "never reproduce")
    assert len(found) == 1


# ---------- Control status tables ----------


def test_isms_valid_control_table_has_no_findings():
    v = _validator()
    v.validate_type_specific()
    assert v.errors == []


def test_isms_invalid_control_status_value():
    body = (
        "| Control | Control status | Evidence |\n"
        "| --- | --- | --- |\n"
        "| A.5.9 | done | [x](https://github.com/example/repo) |\n"
        "| A.5.10 | |  |"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    found = _messages(v, "is not one of")
    assert len(found) == 2


def test_isms_control_table_requires_evidence_column():
    body = (
        "| Control | Control status | Justification |\n"
        "| --- | --- | --- |\n"
        "| A.5.9 | planned | Treatment action open |"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert _messages(v, "no 'Evidence' column")


def test_isms_implemented_requires_repository_evidence():
    body = (
        "| Control | Control status | Evidence |\n"
        "| --- | --- | --- |\n"
        "| A.5.9 | implemented | Asset list kept by operations |\n"
        "| A.5.10 | implemented | [old](http://example.com/policy) |\n"
        "| A.5.12 | implemented | [mail](mailto:security@example.com) |\n"
        "| A.5.13 | implemented | [anchor](#record) |\n"
        "| A.5.14 | implemented | [repo file](../04-system/inventory.md) |\n"
        "| A.5.15 | implemented | <https://github.com/example/repo/actions/runs/1> |\n"
        "| A.5.16 | partial | |\n"
        "| A.5.17 | implemented |"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    missing = _messages(v, "links no repository evidence")
    assert len(missing) == 5


def test_isms_not_applicable_requires_justification():
    body = (
        "| Control | Control status | Evidence | Justification |\n"
        "| --- | --- | --- | --- |\n"
        "| A.7.1 | not applicable | | n/a |\n"
        "| A.7.2 | **Not Applicable** | | No premises are in scope. |"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert len(_messages(v, "has no 'Justification'")) == 1

    body_without_column = (
        "| Control | Control status | Evidence |\n"
        "| --- | --- | --- |\n"
        "| A.7.1 | not applicable | |"
    )
    v = _validator(record_body=body_without_column)
    v.validate_type_specific()
    assert len(_messages(v, "has no 'Justification'")) == 1


def test_isms_tables_without_control_status_are_ignored():
    body = (
        "| Risk | Likelihood | Impact |\n"
        "| --- | --- | --- |\n"
        "| Credential leak in a public repository | 3 | 4 |"
    )
    v = _validator(record_body=body)
    v.validate_type_specific()
    assert v.errors == []
