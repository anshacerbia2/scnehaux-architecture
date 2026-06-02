from .adr import ADRValidator
from .sad import SADValidator
from .pad import PADValidator
from .ead import EADValidator
from .std import STDValidator
from .tdd import TDDValidator
from .gdc import GDCValidator

VALIDATOR_REGISTRY = {
    'ADR': ADRValidator,
    'SAD': SADValidator,
    'PAD': PADValidator,
    'EAD': EADValidator,
    'STD': STDValidator,
    'TDD': TDDValidator,
    'GDC': GDCValidator,
}

def detect_doc_type(doc_id: str | None, filename: str, rel_path: str) -> str | None:
    """Determine document type from metadata ID, filename, or path."""
    if doc_id:
        for prefix in ('GDC-', 'ADR-', 'STD-', 'TDD-', 'EAD-', 'DOC-E'):
            if doc_id.startswith(prefix):
                return prefix.rstrip('-').replace('DOC-E', 'EAD')
        for prefix in ('DOC-P', 'PAD-'):
            if doc_id.startswith(prefix):
                return 'PAD'
        for prefix in ('DOC-S', 'APP-', 'SAD-'):
            if doc_id.startswith(prefix):
                return 'SAD'
    
    # Fallback to filename/path detection
    lower_fn = filename.lower()
    if 'pad' in lower_fn: return 'PAD'
    if 'sad' in lower_fn: return 'SAD'
    if 'adr' in lower_fn: return 'ADR'
    if 'std' in lower_fn: return 'STD'
    if 'tdd' in lower_fn: return 'TDD'
    if rel_path.startswith('00-governance/'): return 'GDC'
    if rel_path.startswith('01-enterprise/'): return 'EAD'
    
    return None

def get_validator(doc_type: str):
    """Return the validator class for a doc type."""
    return VALIDATOR_REGISTRY.get(doc_type)
