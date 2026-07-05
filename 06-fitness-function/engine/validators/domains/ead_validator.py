from engine.validators.base import BaseValidator


class EADValidator(BaseValidator):
    doc_type_name: str = "EAD"

    def validate_type_specific(self) -> None:
        """
        Execute rules specific to Enterprise Architecture Documents (EAD).

        Currently, EADs serve as the top-level anchor for the architecture hierarchy.
        They have no type-specific rules beyond the global governance constraints.
        """
        # @flow-domain: StartEAD((Start EAD Validation)) --> NoOp["No type-specific rules"]
        pass
