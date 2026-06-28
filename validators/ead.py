from .base import BaseValidator

class EADValidator(BaseValidator):
    doc_type_name: str = "EAD"
    @property
    def mandatory_sections(self):
        req_sec = self.rules.get('rules', {}).get('structure', {}).get('required_sections', [])
        if isinstance(req_sec, dict):
            # Resolve specific EAD type from filename (e.g., EAD-001)
            for key, sections in req_sec.items():
                if key in self.filename:
                    return sections
            return [] # Fallback if no specific template matches
        return req_sec

    def validate_type_specific(self):
        pass
