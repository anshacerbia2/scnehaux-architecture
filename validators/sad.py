from .base import BaseValidator

class SADValidator(BaseValidator):
    def validate_type_specific(self):
        if not self.doc_meta:
            return
            
        rules_metadata = self.rules['rules'].get('metadata', {})
        allowed_statuses = rules_metadata.get('allowed_statuses', [])
        allowed_classifications = rules_metadata.get('allowed_classifications', [])
        
        status = self.doc_meta.get('status')
        if status and allowed_statuses and status not in allowed_statuses:
            self.add_error('missing_metadata', f"Status '{status}' is not in allowed list: {allowed_statuses}.")
            
        classification = self.doc_meta.get('classification')
        if classification and allowed_classifications and classification not in allowed_classifications:
            self.add_error('missing_metadata', f"Classification '{classification}' is not in allowed list: {allowed_classifications}.")

        # SAD must have parent_pad traceability
        parent_pad = self.doc_meta.get('parent_pad')
        if parent_pad is None or (isinstance(parent_pad, list) and len(parent_pad) == 0):
            self.add_error('missing_metadata',
                "SAD document is missing required traceability field: 'parent_pad'.")
        else:
            pad_ids = parent_pad if isinstance(parent_pad, list) else [parent_pad]
            for pad_id in pad_ids:
                if pad_id not in self.all_doc_ids:
                    self.add_error('cross_reference_missing',
                        f"SAD 'parent_pad' in metadata references PAD '{pad_id}' which does not exist in the repository.")
