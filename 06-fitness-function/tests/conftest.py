"""
Shared test fixtures for the Scnehaux Architecture Linter test suite.

Provides a proper `make_validator()` factory that calls `BaseValidator.__init__()`
correctly, ensuring lint_disable parsing, rejected_disables, and rel_path computation
are exercised — matching production execution paths.
"""
import os
import json
from engine.validators.registry import get_validator
from engine.validators.base import BaseValidator
from engine.validators.domains.adr_validator import ADRValidator
from engine.validators.domains.sad_validator import SADValidator
from engine.validators.domains.pad_validator import PADValidator
from engine.validators.domains.ead_validator import EADValidator
from engine.validators.domains.std_validator import STDValidator
from engine.validators.domains.tdd_validator import TDDValidator
from engine.validators.domains.gdc_validator import GDCValidator


def make_validator(
    cls=BaseValidator,
    file_path: str = "/fake/test.md",
    content: str = "",
    doc_meta: dict | None = None,
    rules: dict | None = None,
    specific_schema: dict | None = None,
    all_doc_ids: set | None = None,
    all_doc_metadata: dict | None = None,
    filename: str | None = None,
):
    """
    Create a validator instance that calls the REAL __init__,
    ensuring lint_disable parsing and all initialisation logic is exercised.
    """
    if doc_meta is None:
        doc_meta = {}
    if rules is None:
        rules = {'rules': {}, 'severity_levels': {}}
    if all_doc_ids is None:
        all_doc_ids = set()
    if all_doc_metadata is None:
        all_doc_metadata = {}

    v = cls(
        file_path=file_path,
        content=content,
        doc_meta=doc_meta,
        global_rules=rules,
        specific_schema=specific_schema or {},
        all_doc_ids=all_doc_ids,
        all_doc_metadata=all_doc_metadata,
    )
    # Allow callers to override filename for tests that need specific naming patterns.
    if filename is not None:
        v.filename = filename
    return v
