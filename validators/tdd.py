from .base import BaseValidator


class TDDValidator(BaseValidator):
    doc_type_name: str = "TDD"

    def validate_type_specific(self):
        if not self.doc_meta:
            return

        # TDD must have parent_sad traceability
        parent_sad = self.doc_meta.get('parent_sad')
        if parent_sad is None or (isinstance(parent_sad, list) and len(parent_sad) == 0):
            self.add_error('traceability_violation',
                "TDD document is missing required traceability field: 'parent_sad'.")
        else:
            sad_ids = parent_sad if isinstance(parent_sad, list) else [parent_sad]
            for sad_id in sad_ids:
                if sad_id not in self.all_doc_ids:
                    self.add_error('traceability_violation',
                        f"TDD 'parent_sad' in metadata references SAD '{sad_id}' which does not exist in the repository.")
