import os
import re
import jsonschema
from engine.parsing.markdown_ast import strip_code_fences

from .schema_extensions import ExtendedValidator

_base_schema_cache = None


def _get_base_schema():
    global _base_schema_cache
    if _base_schema_cache is None:
        import json

        schema_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "00-governance", "schemas"
        )
        base_schema_path = os.path.abspath(os.path.join(schema_dir, "base.schema.json"))
        with open(base_schema_path, "r", encoding="utf-8") as f:
            _base_schema_cache = json.load(f)
    return _base_schema_cache


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

    def __init__(
        self,
        file_path: str,
        content: str,
        doc_meta: dict,
        global_rules: dict,
        specific_schema: dict,
        all_doc_ids: set,
        all_doc_metadata: dict | None = None,
    ):
        self.file_path = file_path
        self.content = content
        self.doc_meta = doc_meta
        self.global_rules = global_rules
        self.specific_schema = specific_schema
        self.all_doc_ids = all_doc_ids
        self.all_doc_metadata = all_doc_metadata or {}
        self.errors: list[tuple[str, str]] = []
        try:
            self.rel_path = os.path.relpath(file_path, ".").replace("\\", "/")
        except ValueError:
            self.rel_path = file_path.replace("\\", "/")
        self.filename = os.path.basename(file_path)

        # Parse lint_disable directives. Two supported forms (reason optional but
        # recommended); suppression is document-scoped in both cases:
        #   <!-- lint_disable: rule_a, rule_b (reason: approved by ARB in ADR-X) -->
        #   <!-- lint_disable_start: rule_a (reason: ...) -->  ... region ...  <!-- lint_disable_end: rule_a -->
        # The block (start/end) form is a readability convention for wrapping a
        # region whose findings are expected (e.g. a table that enumerates the
        # banned vocabulary itself); `_end` is a closing marker only. Code fences
        # and inline code are stripped first so illustrative examples in
        # documentation (e.g. inside ```html blocks) are NOT parsed as live directives.
        self.disabled_rules = set()
        self.disable_reasons = {}  # rule -> reason string or None
        self.rejected_disables = (
            set()
        )  # CRITICAL rules an author tried (and is not allowed) to silence
        scan_content = strip_code_fences(self.content)
        scan_content = re.sub(
            r"`[^`\n]*`", "", scan_content
        )  # drop inline code spans (e.g. doc examples)
        for match in re.finditer(
            r"<!--\s*lint_disable(?:_start)?:\s*([^>]+?)\s*-->", scan_content
        ):
            body = match.group(1)
            reason = None
            reason_match = re.search(r"\(reason:\s*(.*?)\)\s*$", body)
            if reason_match:
                reason = reason_match.group(1).strip()
                body = body[: reason_match.start()].strip()
            for r in body.split(","):
                name = r.strip()
                if re.fullmatch(r"[a-zA-Z0-9_]+", name):
                    self.disabled_rules.add(name)
                    self.disable_reasons[name] = reason

    def add_error(self, category: str, message: str):
        """
        Record a validation finding. Resolves the severity level from global governance rules.
        If the rule is suppressed via a `lint_disable` directive, the finding is dropped UNLESS
        its severity is CRITICAL, in which case the disable is rejected and the finding fires anyway.
        """
        # By this point, cli.py has already validated that all RuleIDs exist in severity_levels
        try:
            # We enforce that category MUST be a valid SeverityRule instance or matching string
            severity = self.global_rules["severity_levels"][category]
        except KeyError:
            raise RuntimeError(
                f"FATAL: Rule '{category}' triggered but not found in severity_levels (configuration drift!)."
            )
        if category in self.disabled_rules:
            # Blocking severity findings can never be silenced by an inline directive.
            # The disable is rejected (recorded for the audit) and the finding still fires.
            if severity in self.global_rules.get("blocking_severities", []):
                if not hasattr(self, "rejected_disables"):
                    self.rejected_disables = set()
                self.rejected_disables.add(category)
            else:
                return
        self.errors.append((severity, message))

    def validate(self) -> list[tuple[str, str]]:
        """
        Execute the complete validation lifecycle for this document.

        The lifecycle runs in three sequential phases:
        1. JSON-Schema Validation: Strict structural and pattern checking based on the domain schema.
        2. Global Rules Validation: Execution of governance rules applicable to all documents.
        3. Domain-Specific Rules: Execution of custom rules defined in the specific subclass validator.

        Returns:
            list[tuple[str, str]]: An aggregated list of (severity, message) error tuples.
        """
        # @flow-validator: Validate((Start validator.validate)) --> ExtractSections
        self._validate_schema()
        from .global_rules import run_common_validations

        run_common_validations(self)
        # @flow-validator: ValTech --> TypeSpecific["<b>validate_type_specific()</b>: Execute Domain Rules"]
        self.validate_type_specific()
        # @flow-validator: TypeSpecific --> ReturnErrors((Return aggregate errors))
        return self.errors

    def _validate_schema(self):
        """
        Execute JSON-Schema validation against the document's metadata block and section bodies.
        Translates raw jsonschema exceptions into actionable, governance-aware error messages
        (e.g., mapping pattern failures to missing keywords).
        """
        from engine.parsing.markdown_ast import extract_sections_normalized
        import datetime

        # Schemas declare required sections by Title-Case, unnumbered name, and their
        # content_rules run `pattern` checks against the section's text. Map each
        # normalized section title to its content so both presence (`required`) and
        # content patterns validate, and expose `filename` so guideline-only
        # conditional rules (if filename ~ *-guideline.md) gate correctly.
        # @flow-validator: subgraph SchemaPhase[JSON Schema Validation Phase]
        # @flow-validator: ExtractSections["<b>extract_sections_normalized()</b>: Parse sections"] --> BuildDocInstance["Build validation instance dict"]
        sections = extract_sections_normalized(self.content)

        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(i) for i in obj]
            elif isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return obj

        doc_instance = {
            "doc_meta": convert_dates(self.doc_meta),
            "filename": self.filename,
        }
        for title, body in sections.items():
            doc_instance[title] = body

        # @flow-validator: BuildDocInstance --> ExecJsonSchema["<b>ExtendedValidator.iter_errors()</b>"]
        base_schema = _get_base_schema()
        store = {
            base_schema.get(
                "$id",
                "https://scnehaux.com/codex/gov/guidelines/schemas/base.schema.json",
            ): base_schema
        }
        resolver = jsonschema.RefResolver(
            base_uri=self.specific_schema.get("$id", ""),
            referrer=self.specific_schema,
            store=store,
        )
        validator = ExtendedValidator(schema=self.specific_schema, resolver=resolver)
        for e in validator.iter_errors(doc_instance):
            # @flow-validator: ExecJsonSchema -->|ValidationError| MapError["Map jsonschema errors to category"]
            path = " -> ".join([str(p) for p in e.absolute_path]) or "root"

            # Map common errors to clearer categories.
            if e.validator == "required":
                category = "missing_section" if path == "root" else "missing_metadata"
                message = f"Schema validation failed at {path}: {e.message}"
            elif e.validator == "enum":
                category = "missing_metadata"
                message = f"Schema validation failed at {path}: {e.message}"
            elif e.validator == "pattern":
                category = "missing_section_keyword"
                message = f"Section '{path}' is missing required content (expected pattern: {e.validator_value})."
            elif e.validator == "required_subsections":
                category = "missing_section_keyword"
                message = f"Section '{path}' is missing required subsection '{e.validator_value}'."
            elif e.validator == "prohibited_keywords":
                category = "prohibited_words"
                message = f"Section '{path}' contains prohibited governance boilerplate word: '{e.validator_value}'."
            else:
                category = "schema_validation_failed"
                message = f"Schema validation failed at {path}: {e.message}"

            # @flow-validator: MapError --> AddError["<b>add_error()</b>: Record finding"]
            self.add_error(category, message)
        # @flow-validator: ExecJsonSchema -->|Done| CommonRules((Start Global Rules))

    def validate_type_specific(self):
        """Override in subclass for doc-type-specific checks."""
        pass
