from .base import BaseValidator

class ADRValidator(BaseValidator):
    doc_type_name = "ADR"
    
    @property
    def mandatory_sections(self):
        return self.rules['rules'].get('structure', {}).get('adr_sections', [])
    
    @property
    def optional_sections(self):
        return self.rules['rules'].get('structure', {}).get('adr_optional_sections', [])
    
    @property
    def required_metadata_fields(self):
        return self.rules['rules'].get('metadata', {}).get('adr_required_fields', [])
    
    def validate_type_specific(self):
        if not self.doc_meta:
            return
            
        rules_metadata = self.rules['rules'].get('metadata', {})
        
        # Wire up allowed_adr_statuses
        adr_status = self.doc_meta.get('status')
        allowed_statuses = rules_metadata.get('allowed_adr_statuses', [])
        if adr_status and allowed_statuses:
            if adr_status not in allowed_statuses:
                self.add_error('missing_metadata',
                    f"ADR status '{adr_status}' is not in allowed list: {allowed_statuses}.")
        
        # Existing adr_type validation
        adr_type = self.doc_meta.get('adr_type')
        allowed_types = rules_metadata.get('allowed_adr_types', [])
        if adr_type and allowed_types:
            if adr_type not in allowed_types:
                self.add_error('missing_metadata',
                    f"adr_type '{adr_type}' is not in allowed list: {allowed_types}.")
