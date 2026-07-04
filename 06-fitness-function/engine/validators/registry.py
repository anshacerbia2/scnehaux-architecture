from .domains.adr_validator import ADRValidator
from .domains.sad_validator import SADValidator
from .domains.pad_validator import PADValidator
from .domains.ead_validator import EADValidator
from .domains.std_validator import STDValidator
from .domains.tdd_validator import TDDValidator
from .domains.gdc_validator import GDCValidator

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
    prefixes = ('GDC-', 'EAD-', 'STD-', 'PAD-', 'SAD-', 'ADR-', 'TDD-')
    
    if doc_id:
        for prefix in prefixes:
            if doc_id.startswith(prefix):
                return prefix.rstrip('-')
                
    if filename.endswith('.pad.md'):
        return 'PAD'
    if filename.endswith('.sad.md'):
        return 'SAD'
    for prefix in prefixes:
        if filename.startswith(prefix):
            return prefix.rstrip('-')
            
    return None

def get_validator(doc_type: str):
    """Return the validator class for a doc type."""
    return VALIDATOR_REGISTRY.get(doc_type)
