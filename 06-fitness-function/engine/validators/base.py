import os
import re
import jsonschema
from engine.parsing.markdown_ast import strip_code_fences

class BaseValidator:
    """Base class for all document type validators."""
    
    # --- Instance Variable Type Declarations ---
    file_path: str
    content: str
    doc_meta: dict | None
    global_rules: dict
    specific_schema: dict
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
    

        
    def __init__(self, file_path: str, content: str, doc_meta: dict, global_rules: dict, specific_schema: dict, all_doc_ids: set, all_doc_metadata: dict | None = None):
        self.file_path = file_path
        self.content = content
        self.doc_meta = doc_meta
        self.global_rules = global_rules
        self.specific_schema = specific_schema
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
        severity = self.global_rules.get('severity_levels', {}).get(category, 'ERROR')
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
        self._validate_schema()
        from .global_rules import run_common_validations
        run_common_validations(self)
        self.validate_type_specific()
        return self.errors
        
    def _validate_schema(self):
        from engine.parsing.markdown_ast import extract_section_contents
        import datetime
        sections = extract_section_contents(self.content).keys()
        
        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(i) for i in obj]
            elif isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return obj

        doc_instance = {
            "doc_meta": convert_dates(self.doc_meta)
        }
        for sec in sections:
            doc_instance[sec] = True
            
        try:
            jsonschema.validate(instance=doc_instance, schema=self.specific_schema)
        except jsonschema.exceptions.ValidationError as e:
            path = " -> ".join([str(p) for p in e.absolute_path])
            if not path:
                path = "root"
            
            # Map common errors to clearer categories
            if e.validator == 'required':
                if not path or path == 'root':
                    category = 'missing_section'
                else:
                    category = 'missing_metadata'
            elif e.validator == 'enum':
                category = 'missing_metadata'
            else:
                category = 'schema_validation_failed'
                
            self.add_error(category, f"Schema validation failed at {path}: {e.message}")
    
    def validate_type_specific(self):
        """Override in subclass for doc-type-specific checks."""
        pass
