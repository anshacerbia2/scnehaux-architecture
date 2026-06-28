import os
import re
from .utils import strip_code_fences

class BaseValidator:
    """Base class for all document type validators."""
    
    # --- Instance Variable Type Declarations ---
    file_path: str
    content: str
    doc_meta: dict
    rules: dict
    all_doc_ids: set
    all_doc_metadata: dict
    errors: list[tuple[str, str]]
    rel_path: str
    filename: str
    disabled_rules: set
    disable_reasons: dict
    rejected_disables: set
    # -------------------------------------------

    doc_type_name: str = "Unknown"
    
    @property
    def mandatory_sections(self):
        return self.rules.get('rules', {}).get('structure', {}).get('required_sections', [])
    
    @property
    def optional_sections(self):
        return self.rules.get('rules', {}).get('structure', {}).get('optional_sections', [])
    
    @property
    def required_metadata_fields(self):
        return self.rules.get('rules', {}).get('metadata', {}).get('required_fields', [])
        
    def __init__(self, file_path: str, content: str, doc_meta: dict, rules: dict, all_doc_ids: set, all_doc_metadata: dict = None):
        self.file_path = file_path
        self.content = content
        self.doc_meta = doc_meta
        self.rules = rules
        self.all_doc_ids = all_doc_ids
        self.all_doc_metadata = all_doc_metadata or {}
        self.errors: list[tuple[str, str]] = []
        try:
            self.rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
        except ValueError:
            self.rel_path = file_path.replace('\\', '/')
        self.filename = os.path.basename(file_path)

        # Parse lint_disable directives. Format (reason optional but recommended):
        #   <!-- lint_disable: rule_a, rule_b (reason: approved by ARB in ADR-X) -->
        # Code fences are stripped first so illustrative examples in documentation
        # (e.g. inside ```html blocks) are NOT interpreted as live directives.
        self.disabled_rules = set()
        self.disable_reasons = {}   # rule -> reason string or None
        self.rejected_disables = set()  # CRITICAL rules an author tried (and is not allowed) to silence
        scan_content = strip_code_fences(self.content)
        scan_content = re.sub(r'`[^`\n]*`', '', scan_content)  # drop inline code spans (e.g. doc examples)
        for match in re.finditer(r'<!--\s*lint_disable:\s*([^>]+?)\s*-->', scan_content):
            body = match.group(1)
            reason = None
            reason_match = re.search(r'\(reason:\s*(.*?)\)\s*$', body)
            if reason_match:
                reason = reason_match.group(1).strip()
                body = body[:reason_match.start()].strip()
            for r in body.split(','):
                name = r.strip()
                if re.fullmatch(r'[a-zA-Z0-9_]+', name):
                    self.disabled_rules.add(name)
                    self.disable_reasons[name] = reason

    def add_error(self, category: str, message: str):
        severity = self.rules.get('severity_levels', {}).get(category, 'ERROR')
        if category in self.disabled_rules:
            # CRITICAL findings can never be silenced by an inline directive.
            # The disable is rejected (recorded for the audit) and the finding still fires.
            if severity == 'CRITICAL':
                if not hasattr(self, 'rejected_disables'):
                    self.rejected_disables = set()
                self.rejected_disables.add(category)
            else:
                return
        self.errors.append((severity, message))
    
    def validate(self) -> list[tuple[str, str]]:
        """Run all validations."""
        from .common import run_common_validations
        run_common_validations(self)
        self.validate_type_specific()
        return self.errors
    
    def validate_type_specific(self):
        """Override in subclass for doc-type-specific checks."""
        pass
