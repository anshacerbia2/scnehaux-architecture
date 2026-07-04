from engine.validators.base import BaseValidator

class STDValidator(BaseValidator):
    doc_type_name: str = "STD"
    def validate_type_specific(self) -> None:
        """Perform Standard Document validations, ensuring enterprise standards are appropriately structured and referenced."""
        if not self.doc_meta:
            return
            
        status = str(self.doc_meta.get('status', '')).lower()
        if status == 'hold':
            self.add_error('operational_stability_violation',
                "STD document has status 'hold' (retirement phase). "
                "New implementations MUST NOT adopt this standard. "
                "Existing implementations must schedule migration.")
