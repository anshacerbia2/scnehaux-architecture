from engine.validators.base import BaseValidator


class SADValidator(BaseValidator):
    doc_type_name: str = "SAD"

    def validate_type_specific(self) -> None:
        """
        Execute rules specific to System Architecture Documents (SAD).

        Enforces upward traceability and bidirectional consistency:
        - Validates the mandatory `parent_pad` field, ensuring the system maps to a recognized platform.
        - Checks that the referenced PAD exists in the repository.
        - Checks that the referenced PAD declares this SAD in its `fulfilled_by` array (bidirectional link).
        """
        # @flow-domain: StartSAD((Start SAD Validation)) --> CheckParentPAD["Check 'parent_pad' metadata"]
        if not self.doc_meta:
            return

        # SAD must have parent_pad traceability
        parent_pad = self.doc_meta.get("parent_pad")
        # @flow-domain: CheckParentPAD --> IsParentPADMissing{"Missing or empty?"}
        if parent_pad is None or (
            isinstance(parent_pad, list) and len(parent_pad) == 0
        ):
            # @flow-domain: IsParentPADMissing -->|Yes| ErrPADMissing["Error: parent_pad required"]
            self.add_error(
                "traceability_violation",
                "SAD document is missing required traceability field: 'parent_pad'.",
            )
        else:
            # @flow-domain: IsParentPADMissing -->|No| LoopPAD{"For each PAD ID"}
            pad_ids = parent_pad if isinstance(parent_pad, list) else [parent_pad]
            for pad_id in pad_ids:
                # @flow-domain: LoopPAD --> CheckPADExist{"PAD exists?"}
                if pad_id not in self.all_doc_ids:
                    # @flow-domain: CheckPADExist -->|No| ErrPADNotFound["Error: PAD does not exist"]
                    self.add_error(
                        "traceability_violation",
                        f"SAD 'parent_pad' in metadata references PAD '{pad_id}' which does not exist in the repository.",
                    )
                else:
                    # @flow-domain: CheckPADExist -->|Yes| CheckPADBidirectional{"PAD points to this SAD?"}
                    # Bidirectional check: ensure PAD recognizes this SAD
                    pad_meta = self.all_doc_metadata.get(pad_id)
                    if pad_meta:
                        fulfilled_by = pad_meta.get("fulfilled_by")
                        fulfilled_list = (
                            fulfilled_by
                            if isinstance(fulfilled_by, list)
                            else ([fulfilled_by] if fulfilled_by else [])
                        )
                        self_id = self.doc_meta.get("id")
                        if self_id not in fulfilled_list:
                            # @flow-domain: CheckPADBidirectional -->|No| ErrPADBidir["Error: Bidirectional traceability broken"]
                            self.add_error(
                                "traceability_violation",
                                f"SAD '{self_id}' references parent PAD '{pad_id}', but PAD '{pad_id}' does not list this SAD in its 'fulfilled_by'. Bidirectional traceability is broken.",
                            )
