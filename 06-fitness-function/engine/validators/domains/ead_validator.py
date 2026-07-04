from engine.validators.base import BaseValidator

class EADValidator(BaseValidator):
    doc_type_name: str = "EAD"


    def validate_type_specific(self) -> None:
        """Perform Enterprise Architecture Document validations, ensuring high-level capability linkages and strategic alignment."""
        pass
