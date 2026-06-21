import os
import re

class BaseValidator:
    """Base class for all document type validators."""
    
    # --- Instance Variable Type Declarations ---
    file_path: str
    content: str
    doc_meta: dict
    rules: dict
    all_doc_ids: set
    errors: list[tuple[str, str]]
    rel_path: str
    filename: str
    disabled_rules: set
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
        
    def __init__(self, file_path: str, content: str, doc_meta: dict, rules: dict, all_doc_ids: set):
        self.file_path = file_path
        self.content = content
        self.doc_meta = doc_meta
        self.rules = rules
        self.all_doc_ids = all_doc_ids
        self.errors: list[tuple[str, str]] = []
        self.rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
        self.filename = os.path.basename(file_path)
        
        # Parse lint_disable comments: <!-- lint_disable: rule_name, rule_name -->
        self.disabled_rules = set()
        for match in re.finditer(r'<!--\s*lint_disable:\s*([a-zA-Z0-9_,\s]+)\s*-->', self.content):
            rules_str = match.group(1)
            for r in rules_str.split(','):
                self.disabled_rules.add(r.strip())
    
    def add_error(self, category: str, message: str):
        if category in self.disabled_rules:
            return
        severity = self.rules.get('severity_levels', {}).get(category, 'ERROR')
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
