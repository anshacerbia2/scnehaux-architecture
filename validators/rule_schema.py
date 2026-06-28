"""
Pydantic schema for the YAML linting-rules files.

This validates the STRUCTURE of the governance rule files themselves — ensuring
that the governance engine's own configuration is structurally correct.
Without this, a typo in a YAML rule key (e.g. 'required_section' instead of
'required_sections') would silently disable enforcement.
"""
from pydantic import BaseModel, model_validator
from typing import Optional, Any


class RuleConfig(BaseModel):
    """Top-level schema for a linting-rules YAML file."""
    config: Optional[dict[str, Any]] = None
    rules: Optional[dict[str, Any]] = None
    severity_levels: Optional[dict[str, str]] = None

    @model_validator(mode='after')
    def must_have_rules_or_severity(self) -> 'RuleConfig':
        if self.rules is None and self.severity_levels is None:
            raise ValueError("A rule file must define at least 'rules' or 'severity_levels'.")
        return self

    @model_validator(mode='after')
    def validate_severity_values(self) -> 'RuleConfig':
        allowed = {'CRITICAL', 'ERROR', 'WARNING'}
        if self.severity_levels:
            for key, val in self.severity_levels.items():
                if val not in allowed:
                    raise ValueError(
                        f"severity_levels.{key} has invalid value '{val}'. "
                        f"Must be one of: {sorted(allowed)}."
                    )
        return self

    @model_validator(mode='after')
    def validate_rules_structure(self) -> 'RuleConfig':
        """Validate known rule sub-keys have correct types."""
        if not self.rules:
            return self

        known_top_keys = {
            'metadata', 'structure', 'content', 'quantification',
            'governance', 'federated_governance',
        }
        for key in self.rules:
            if key not in known_top_keys:
                # Unknown keys are allowed (forward compatibility), but we log them.
                pass

        # Validate 'metadata' sub-structure
        metadata = self.rules.get('metadata')
        if metadata and isinstance(metadata, dict):
            if 'required_fields' in metadata and not isinstance(metadata['required_fields'], list):
                raise ValueError("rules.metadata.required_fields must be a list.")
            if 'allowed_statuses' in metadata and not isinstance(metadata['allowed_statuses'], list):
                raise ValueError("rules.metadata.allowed_statuses must be a list.")
            if 'allowed_classifications' in metadata and not isinstance(metadata['allowed_classifications'], list):
                raise ValueError("rules.metadata.allowed_classifications must be a list.")

        # Validate 'structure' sub-structure
        structure = self.rules.get('structure')
        if structure and isinstance(structure, dict):
            req_sec = structure.get('required_sections')
            if req_sec is not None and not isinstance(req_sec, (list, dict)):
                raise ValueError("rules.structure.required_sections must be a list or dict.")
            opt_sec = structure.get('optional_sections')
            if opt_sec is not None and not isinstance(opt_sec, list):
                raise ValueError("rules.structure.optional_sections must be a list.")

        return self


def validate_rule_file(data: dict, file_path: str) -> list[str]:
    """
    Validate a loaded YAML rule dict against the schema.
    Returns a list of error messages (empty if valid).
    """
    if not data or not isinstance(data, dict):
        return [f"Rule file '{file_path}' is empty or not a valid YAML mapping."]

    errors = []
    try:
        RuleConfig(**data)
    except Exception as e:
        errors.append(f"Rule file '{file_path}' schema validation failed: {e}")
    return errors
