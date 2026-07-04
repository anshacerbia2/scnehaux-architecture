from engine.validators.base import BaseValidator
import datetime

class ADRValidator(BaseValidator):
    doc_type_name: str = "ADR"
    
    def validate_type_specific(self) -> None:
        """Perform ADR-specific validations, including status transitions (e.g., checking expiration of Sunset statuses)."""
        if not self.doc_meta:
            return
            
        adr_type = self.doc_meta.get('adr_type')
        if adr_type == 'exception':
            exception_info = self.doc_meta.get('exception_info')
            if exception_info:
                # Expired Exception Check (only for active waivers)
                status = self.doc_meta.get('status')
                if status == 'accepted':
                    expiry_date = exception_info.get('expiry_date')
                    if isinstance(expiry_date, datetime.date) and expiry_date < datetime.date.today():
                        self.add_error('exception_expired', f"Exception waiver has expired on {expiry_date}.")
