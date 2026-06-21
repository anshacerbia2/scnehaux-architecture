from .base import BaseValidator

class PADValidator(BaseValidator):
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

        # fulfilled_by is expected to list SADs, but can be empty/missing if SADs are not yet built
        fulfilled_by = self.doc_meta.get('fulfilled_by')
        if fulfilled_by is not None:
            if not isinstance(fulfilled_by, list) or len(fulfilled_by) == 0:
                self.add_error('cross_reference_missing',
                    "PAD 'fulfilled_by' is empty. Consider linking a SAD once implementation begins.")
            else:
                for sad_id in fulfilled_by:
                    if sad_id not in self.all_doc_ids:
                        self.add_error('cross_reference_missing',
                            f"PAD 'fulfilled_by' in metadata references SAD '{sad_id}' which does not exist in the repository.")
