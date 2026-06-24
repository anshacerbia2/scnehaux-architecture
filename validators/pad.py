from .base import BaseValidator

class PADValidator(BaseValidator):
    def validate_type_specific(self):
        if not self.doc_meta:
            return

        # fulfilled_by is expected to list SADs, but can be empty/missing if SADs are not yet built
        fulfilled_by = self.doc_meta.get('fulfilled_by')
        if fulfilled_by is not None:
            if not isinstance(fulfilled_by, list) or len(fulfilled_by) == 0:
                # Warning if fulfilled_by is empty, not a hard block
                self.add_error('cross_reference_missing',
                    "PAD 'fulfilled_by' is empty. Consider linking a SAD once implementation begins.")
            else:
                self_id = self.doc_meta.get('id')
                for sad_id in fulfilled_by:
                    if sad_id not in self.all_doc_ids:
                        self.add_error('traceability_violation',
                            f"PAD 'fulfilled_by' in metadata references SAD '{sad_id}' which does not exist in the repository.")
                    else:
                        # Bidirectional check: ensure SAD points back to this PAD
                        sad_meta = self.all_doc_metadata.get(sad_id)
                        if sad_meta:
                            parent_pad = sad_meta.get('parent_pad')
                            parent_list = parent_pad if isinstance(parent_pad, list) else ([parent_pad] if parent_pad else [])
                            if self_id not in parent_list:
                                self.add_error('traceability_violation',
                                    f"PAD '{self_id}' lists SAD '{sad_id}' in 'fulfilled_by', but SAD '{sad_id}' does not reference this PAD as its 'parent_pad'. Bidirectional traceability is broken.")
