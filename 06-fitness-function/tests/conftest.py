"""
Shared test fixtures for the Scnehaux Architecture Linter test suite.

Provides a proper `make_validator()` factory that calls `BaseValidator.__init__()`
correctly, ensuring lint_disable parsing, rejected_disables, and rel_path computation
are exercised matching production execution paths.
"""

import os
import json
from engine.validators.base import BaseValidator
from engine.config.loader import validate_severity_schema, validate_blocking_severities

from functools import lru_cache

@lru_cache(maxsize=1)
def _get_real_config() -> tuple[dict, dict, tuple]:
    from engine.config.loader import parse_and_validate_global_config
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    schema_path = os.path.join(root_dir, "00-governance", "schemas", "base.schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    return parse_and_validate_global_config(schema)


def make_validator(
    cls=BaseValidator,
    file_path: str = "/fake/test.md",
    content: str = "",
    doc_meta: dict | None = None,
    rules: dict | None = None,
    domain_schema: dict | None = None,
    all_doc_ids: set | None = None,
    all_doc_metadata: dict | None = None,
    filename: str | None = None,
):
    """
    Create a validator instance that calls the REAL __init__,
    ensuring lint_disable parsing and all initialisation logic is exercised.
    It merges test rules with the real validated global schema, ensuring
    tests cannot instantiate a validator with a broken configuration.
    """
    if doc_meta is None:
        doc_meta = {}
    if rules is None:
        rules = {}
    if all_doc_ids is None:
        all_doc_ids = set()
    if all_doc_metadata is None:
        all_doc_metadata = {}

    real_global, real_severity, real_blocking = _get_real_config()
    
    # Merge rules with real defaults
    merged_rules = dict(real_global)
    merged_rules.update(rules)
    
    # Merge severity levels
    merged_severity = dict(real_severity)
    if "severity_levels" in rules:
        merged_severity.update(rules["severity_levels"])
        
    # Get blocking severities
    merged_blocking = rules.get("blocking_severities", list(real_blocking))
    merged_blocking = tuple(merged_blocking)
    
    # Validate exactly like cli.py does, ensuring tests are "pro"
    validate_severity_schema(merged_severity)
    validate_blocking_severities(merged_blocking)

    v = cls(
        file_path=file_path,
        content=content,
        doc_meta=doc_meta,
        global_rules=merged_rules,
        domain_schema=domain_schema or {},
        all_doc_ids=all_doc_ids,
        all_doc_metadata=all_doc_metadata,
        severity_levels=merged_severity,
        blocking_severities=merged_blocking,
    )
    if filename is not None:
        v.filename = filename
    return v
