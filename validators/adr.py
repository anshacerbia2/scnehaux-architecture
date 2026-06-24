from .base import BaseValidator
import datetime

class ADRValidator(BaseValidator):
    
    def validate_type_specific(self):
        if not self.doc_meta:
            return
            
        rules_metadata = self.rules['rules'].get('metadata', {})

        # Existing adr_type validation
        adr_type = self.doc_meta.get('adr_type')
        allowed_types = rules_metadata.get('allowed_types', [])
        if adr_type and allowed_types:
            if adr_type not in allowed_types:
                self.add_error('missing_metadata',
                    f"adr_type '{adr_type}' is not in allowed list: {allowed_types}.")

        # Exception ADR conditional field enforcement (GDC-010 §2.4.1.2)
        if adr_type == 'exception':
            exception_info = self.doc_meta.get('exception_info')
            if not exception_info:
                self.add_error('missing_metadata', "Exception ADR is missing the required 'exception_info' object under doc_meta.")
            else:
                exception_required_fields = rules_metadata.get('exception_info_required_fields', [])
                for field in exception_required_fields:
                    if field not in exception_info:
                        self.add_error('missing_metadata',
                            f"Exception ADR is missing required waiver field: '{field}' inside 'exception_info'.")
                
                # Expired Exception Check (only for active waivers)
                status = self.doc_meta.get('status')
                if status == 'accepted':
                    expiry_date = exception_info.get('expiry_date')
                    if isinstance(expiry_date, datetime.date) and expiry_date < datetime.date.today():
                        self.add_error('exception_expired', f"Exception waiver has expired on {expiry_date}.")
