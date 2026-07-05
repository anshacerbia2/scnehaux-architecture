from .domains.adr_validator import ADRValidator
from .domains.sad_validator import SADValidator
from .domains.pad_validator import PADValidator
from .domains.ead_validator import EADValidator
from .domains.std_validator import STDValidator
from .domains.tdd_validator import TDDValidator
from .domains.gdc_validator import GDCValidator

VALIDATOR_REGISTRY = {
    "ADR": ADRValidator,
    "SAD": SADValidator,
    "PAD": PADValidator,
    "EAD": EADValidator,
    "STD": STDValidator,
    "TDD": TDDValidator,
    "GDC": GDCValidator,
}


def detect_doc_type(doc_id: str | None, filename: str, rel_path: str) -> str | None:
    """
    Determine the architecture document type based on cascading fallback logic.

    Resolution order:
    1. Parse the explicit `id` field from the document's YAML frontmatter (e.g. 'SAD-001').
    2. Fallback: Check if the filename uses legacy/domain extensions (e.g. `.sad.md`).
    3. Fallback: Parse the filename prefix itself (e.g. 'GDC-001.md').

    Returns:
        str | None: The 3-letter uppercase document type (e.g. 'SAD', 'PAD') or None if unknown.
    """
    prefixes = ("GDC-", "EAD-", "STD-", "PAD-", "SAD-", "ADR-", "TDD-")

    if doc_id:
        for prefix in prefixes:
            if doc_id.startswith(prefix):
                return prefix.rstrip("-")

    if filename.endswith(".pad.md"):
        return "PAD"
    if filename.endswith(".sad.md"):
        return "SAD"
    for prefix in prefixes:
        if filename.startswith(prefix):
            return prefix.rstrip("-")

    return None


def get_validator(doc_type: str):
    """
    Return the corresponding Validator subclass for the detected document type.

    Maps strings like 'SAD' to `SADValidator`, 'PAD' to `PADValidator`, etc.
    Returns None if the document type is not supported by the validation engine.
    """
    return VALIDATOR_REGISTRY.get(doc_type)
