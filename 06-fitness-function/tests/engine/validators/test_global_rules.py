from tests.conftest import make_validator
import re
import os
import json
from engine.config.constants import (
    SCHEMA_KEY_ARTIFACT_DIRS,
    SCHEMA_KEY_STRUCTURE_RULES,
)
from engine.validators.global_rules import (
    _validate_content_quality,
    _validate_compliance_placement,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _global_rules():
    with open(
        os.path.join(ROOT, "00-governance", "schemas", "base.schema.json"),
        encoding="utf-8",
    ) as f:
        return json.load(f).get("x-global-config", {})


def test_validate_content_quality():
    rules = {
        "content_rules": {
            "prohibited_words": {
                "patterns": ["just", "basically"],
                "error_message": "Found prohibited word",
            }
        },
        "severity_levels": {},
    }
    v = make_validator(rules=rules, content="This is basically just too short.")
    _validate_content_quality(v)
    prohibited_errors = [e for e in v.errors if "found prohibited word" in e[1].lower()]
    assert len(prohibited_errors) == 2


def test_ambiguity_check():
    rules = {
        "content_rules": {
            "ambiguity_rules": {
                "patterns": ["\\b(very|extremely)\\s+(fast|good)\\b"],
                "error_message": "Vague claim",
            }
        },
        "severity_levels": {},
    }
    v = make_validator(rules=rules, content="It is very fast.")
    _validate_content_quality(v)
    assert len(v.errors) == 1


def test_ambiguity_no_message():
    rules = {
        "content_rules": {"prohibited_words": {"patterns": ["badword", "nono"]}},
        "severity_levels": {},
    }
    v = make_validator(rules=rules, content="This is a badword.")
    _validate_content_quality(v)
    assert len(v.errors) == 1


def test__validate_content_quality_ambiguity_regex():
    pat = _global_rules()["content_rules"]["ambiguity_rules"]["patterns"][0]
    assert "\x08" not in pat, "double-quote corrupted \\b into a backspace char"
    assert re.search(pat, "this design is highly scalable", re.IGNORECASE)
    assert re.search(pat, "it is very fast under load", re.IGNORECASE)
    assert not re.search(pat, "a perfectly ordinary sentence", re.IGNORECASE)


def test_validate_technologies_whitelist(monkeypatch):
    import engine.validators.global_rules as gr
    from io import StringIO

    original_exists = os.path.exists

    def mock_exists(p):
        if "tech-radar.yaml" in p:
            return True
        return original_exists(p)

    monkeypatch.setattr(os.path, "exists", mock_exists)

    mock_yaml = "technology_radar:\n  hold:\n    - React\n    - MongoDB"
    _real_open = open

    def mock_open(*args, **kwargs):
        if "tech-radar.yaml" in args[0]:
            return StringIO(mock_yaml)
        return _real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open)

    v = make_validator(
        content="We use React for the frontend",
        doc_meta={"id": "SAD-001", "technologies": [{"name": "React"}]},
    )
    v.doc_type_name = "SAD"
    gr._validate_technologies_whitelist(v)
    assert any("React" in e[1] for e in v.errors)

    def crash_open(*args, **kwargs):
        raise ValueError("mock crash")

    monkeypatch.setattr("builtins.open", crash_open)
    v2 = make_validator(
        content="We use React for the frontend",
        doc_meta={"id": "SAD-001", "technologies": [{"name": "Crash"}]},
    )
    v2.doc_type_name = "SAD"
    gr._validate_technologies_whitelist(v2)
    assert len(v2.errors) == 0

    v3 = make_validator(
        doc_meta={"technologies": [{"name": "React"}]},
    )
    v3.doc_type_name = "GDC"
    gr._validate_technologies_whitelist(v3)
    assert len(v3.errors) == 0


def test_compliance_placement_reads_the_key_the_schema_declares():
    """The wiring, which is what the test below could not see.

    This asserts against the real `base.schema.json` rather than a hand-built dict. The macro-
    directory rule sat inert for the entire life of the engine because the validator read
    `structure_rules.standard_directory` and no schema ever declared that name: the lookup
    returned {}, `expected_dir` was None, and the check silently passed every document. The test
    below built the key the validator wanted, so it proved the function and never the connection
    between the function and its configuration.

    Every doc type the schema maps must be reachable through the same path the validator uses, and
    the map must not be empty — an empty map disables the rule exactly as the typo did.
    """
    declared = (
        _global_rules()
        .get(SCHEMA_KEY_STRUCTURE_RULES, {})
        .get(SCHEMA_KEY_ARTIFACT_DIRS, {})
    )
    assert declared, (
        "base.schema.json declares no artifact_directories under the key the validator reads; "
        "the macro-directory rule is disabled"
    )

    # The map is the real one, so a renamed key or an emptied map fails here. Only the map is
    # passed through: the schema's severity_levels are grouped by domain and flattened by the
    # loader, and this test is about the structure_rules wiring rather than that plumbing.
    rules = {SCHEMA_KEY_STRUCTURE_RULES: {SCHEMA_KEY_ARTIFACT_DIRS: declared}}

    for doc_type, expected_dir in sorted(declared.items()):
        v = make_validator(
            rules=rules,
            file_path=f"/home/repo/definitely-not-here/{doc_type}-001.md",
            filename=f"{doc_type}-001.md",
            doc_meta={"id": f"{doc_type}-001"},
        )
        v.doc_type_name = doc_type
        _validate_compliance_placement(v)
        assert any(expected_dir in message for _, message in v.errors), (
            f"a {doc_type} outside {expected_dir} was accepted under the real schema"
        )


def test_macro_directory_matches_segments_not_substrings():
    """The second defect under the first, kept as an executable statement of both.

    The rule compared `f"/{expected}/"` against the path, which needs a separator before the first
    segment. The governance repository is linted with `--target .` and gets one by accident;
    every downstream repository is linted with `--target docs` and does not — so enabling the rule
    refused all twenty-three correctly placed TDDs in the estate at once.
    """
    rules = {"structure_rules": {"artifact_directories": {"TDD": "docs/designs"}}}

    def placement(path):
        v = make_validator(
            rules=rules,
            file_path=path,
            filename="TDD-x-001.md",
            doc_meta={"id": "TDD-x-001"},
        )
        v.doc_type_name = "TDD"
        _validate_compliance_placement(v)
        return [m for _, m in v.errors if "macro-directory" in m]

    # Relative, with no leading separator: the shape every downstream repository produces.
    assert placement("docs/designs/TDD-x-001.md") == []
    assert placement("docs\\designs\\TDD-x-001.md") == []
    # Absolute and dot-relative still hold.
    assert placement("/home/repo/docs/designs/TDD-x-001.md") == []
    assert placement("./docs/designs/TDD-x-001.md") == []
    # Nested per-system grouping inside the macro directory is accepted: a platform repository with
    # two deployables needs somewhere to put each system's designs.
    assert placement("docs/designs/runtime/TDD-x-001.md") == []

    # Wrong tree is refused.
    assert placement("docs/TDD-x-001.md") != []
    assert placement("TDD-x-001.md") != []
    # And a name that merely contains the expected text is not a segment run.
    assert placement("docs/designs-old/TDD-x-001.md") != []
    assert placement("notes-docs/designs-draft/TDD-x-001.md") != []


def test_compliance_placement_macro_dir():
    rules = {"structure_rules": {"artifact_directories": {"SAD": "04-system"}}}
    v_valid = make_validator(
        rules=rules,
        file_path="/home/repo/04-system/scnehaux-ui-platform/SAD-003.sad.md",
        filename="SAD-003.sad.md",
        doc_meta={"id": "SAD-003"},
    )
    v_valid.doc_type_name = "SAD"
    _validate_compliance_placement(v_valid)
    assert len(v_valid.errors) == 0

    v_invalid = make_validator(
        rules=rules,
        file_path="/home/repo/03-domain/scnehaux-ui-platform/SAD-003.sad.md",
        filename="SAD-003.sad.md",
        doc_meta={"id": "SAD-003"},
    )
    v_invalid.doc_type_name = "SAD"
    _validate_compliance_placement(v_invalid)
    assert len(v_invalid.errors) == 1
    assert (
        "must be located within the '04-system/' macro-directory"
        in v_invalid.errors[0][1]
    )


def test_compliance_placement_filename_match():
    v_valid = make_validator(
        file_path="/home/repo/04-system/scnehaux-ui-platform/SAD-003-design-tokens.sad.md",
        filename="SAD-003-design-tokens.sad.md",
        doc_meta={"id": "SAD-003"},
    )
    v_valid.doc_type_name = "SAD"
    _validate_compliance_placement(v_valid)
    assert len(v_valid.errors) == 0

    v_invalid = make_validator(
        file_path="/home/repo/04-system/scnehaux-ui-platform/design-tokens.md",
        filename="design-tokens.md",
        doc_meta={"id": "SAD-003"},
    )
    v_invalid.doc_type_name = "SAD"
    _validate_compliance_placement(v_invalid)
    assert len(v_invalid.errors) == 1
    assert "must start with the document ID 'SAD-003'" in v_invalid.errors[0][1]
