from .base import BaseValidator

class STDValidator(BaseValidator):
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

        status = str(self.doc_meta.get('status', '')).lower()
        if status == 'hold':
            self.add_error('operational_stability_violation',
                "STD document has status 'hold' (retirement phase). "
                "New implementations MUST NOT adopt this standard. "
                "Existing implementations must schedule migration.")
