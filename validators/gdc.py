from .base import BaseValidator

class GDCValidator(BaseValidator):
    doc_type_name = "GDC"
    
    @property
    def mandatory_sections(self):
        return self.rules['rules'].get('structure', {}).get('gdc_sections', [])
    
    @property
    def optional_sections(self):
        return self.rules['rules'].get('structure', {}).get('gdc_optional_sections', [])
    
    @property
    def required_metadata_fields(self):
        return self.rules['rules'].get('metadata', {}).get('required_fields', [])
    
    def validate_type_specific(self):
        pass
