import re
import logging
from .base import BaseValidator
from engine.config.constants import (
    SCHEMA_KEY_ARTIFACT_DIRS,
    SCHEMA_KEY_STRUCTURE_RULES,
)
from engine.parsing.markdown_ast import (
    strip_code_fences,
)
from .metadata_rules import (
    _validate_review_age,
    _validate_approved_version_stability,
    _validate_cross_references,
    _validate_technologies_whitelist,
)
from .structure_rules import (
    _validate_structure,
    _validate_nfr_taxonomy,
    _validate_internal_links,
    _validate_inline_references,
)

logger = logging.getLogger(__name__)


def run_common_validations(validator: BaseValidator) -> None:
    """
    Execute the suite of global governance rules (e.g. naming, review age, NFR taxonomy,
    traceability) that apply universally across all architecture document types.
    """
    # @flow-validator: subgraph GlobalRulesPhase[Global Rules Validation Suite]
    # @flow-validator: direction TB

    # @flow-validator: GlobalRules --> ValCompliance["<b>_validate_compliance_placement()</b>: Check folder placement & file naming"]
    _validate_compliance_placement(validator)
    # @flow-validator: ValCompliance --> ValRevAge["<b>_validate_review_age()</b>: Check if document is expired"]
    _validate_review_age(validator)
    # @flow-validator: ValRevAge --> ValVerStab["<b>_validate_approved_version_stability()</b>: Check baseline status carries a stable version"]
    _validate_approved_version_stability(validator)
    # @flow-validator: ValVerStab --> ValContent["<b>_validate_content_quality()</b>: Check for prohibited words & vague claims"]
    _validate_content_quality(validator)
    # @flow-validator: ValContent --> ValStruct["<b>_validate_structure()</b>: Check minimum section lengths"]
    _validate_structure(validator)
    # @flow-validator: ValStruct --> ValCross["<b>_validate_cross_references()</b>: Check validity of related document IDs"]
    _validate_cross_references(validator)
    # @flow-validator: ValCross --> ValInternal["<b>_validate_internal_links()</b>: Check for broken markdown links"]
    _validate_internal_links(validator)
    # @flow-validator: ValInternal --> ValInline["<b>_validate_inline_references()</b>: Detect inline document ID mentions"]
    _validate_inline_references(validator)
    # @flow-validator: ValInline --> ValNFR["<b>_validate_nfr_taxonomy()</b>: Ensure NFRs follow AWS WAF pillars"]
    _validate_nfr_taxonomy(validator)
    # @flow-validator: ValNFR --> ValTech["<b>_validate_technologies_whitelist()</b>: Check for prohibited technologies"]
    _validate_technologies_whitelist(validator)
    # @flow-validator: end


def _within_macro_directory(file_path: str, expected_dir: str) -> bool:
    """
    Report whether the document's directories contain the expected macro-directory as a
    contiguous run of path segments.

    Segments rather than a substring. The original check asked whether `f"/{expected_dir}/"`
    appeared in the path, which requires a separator before the first segment — so it held only
    for paths that happen to begin with one. The governance repository is linted with `--target .`
    and produces `./00-governance/GDC-000...`, which supplies that leading separator by accident.
    Every downstream repository is linted with `--target docs` and produces
    `docs/designs/TDD-...`, which does not — so the moment the rule was wired up it refused all
    twenty-three correctly placed TDDs in the estate.

    Comparing segments also removes the substring trap the old form carried: a document under
    `notes-04-system-draft/` would have satisfied a `/04-system/` search only by not containing it,
    and a directory named `docs/designs-old/` would have satisfied `docs/designs` under a looser
    prefix test. Neither can match a segment run.

    A run rather than a prefix, so `docs/designs/runtime/TDD-...` is accepted. A repository holding
    several independently deployable systems needs to group designs per system, and the macro
    directory is about which tree a document belongs to rather than how deep inside it the document
    sits.
    """
    expected = [p for p in expected_dir.replace("\\", "/").split("/") if p and p != "."]
    if not expected:
        return True

    # The filename itself is not a directory, so it cannot satisfy the run.
    actual = [p for p in file_path.replace("\\", "/").split("/") if p and p != "."][:-1]
    if len(actual) < len(expected):
        return False

    return any(
        actual[i : i + len(expected)] == expected
        for i in range(len(actual) - len(expected) + 1)
    )


def _validate_compliance_placement(v: BaseValidator) -> None:
    """
    Validate that the document is placed in the correct macro-directory
    and that the filename starts with the metadata ID.
    """
    doc_type = v.doc_type_name
    file_path = v.file_path.replace("\\", "/")
    filename = v.filename
    doc_id = (v.doc_meta or {}).get("id", "")

    # 1. Macro-Directory check
    #
    # The key is read through the shared constant rather than typed here. It was typed here, as
    # "standard_directory", and no schema has ever defined that name — so the lookup returned an
    # empty map, `expected_dir` was always None, and `compliance_macro_directory` never fired for
    # any document in any repository despite carrying ERROR severity and a row in GDC-001.
    #
    # The unit test passed because it built `{"standard_directory": {...}}` itself: it proved the
    # function and never the wiring. `test_compliance_placement_reads_the_key_the_schema_declares`
    # is what closes that, and the constant is what stops the two from drifting apart again.
    macro_dir_map = v.global_rules.get(SCHEMA_KEY_STRUCTURE_RULES, {}).get(
        SCHEMA_KEY_ARTIFACT_DIRS, {}
    )
    expected_dir = macro_dir_map.get(doc_type)
    if expected_dir and not _within_macro_directory(file_path, expected_dir):
        v.add_error(
            "compliance_macro_directory",
            f"Document of type '{doc_type}' must be located within the '{expected_dir}/' macro-directory.",
        )

    # 2. Filename identity check
    if doc_id:
        if (
            not filename.endswith(".sad.md")
            and not filename.endswith(".pad.md")
            and not filename.startswith(doc_id)
        ):
            v.add_error(
                "compliance_filename_match",
                f"Filename '{filename}' must start with the document ID '{doc_id}'.",
            )


def _validate_content_quality(v: BaseValidator) -> None:
    """Ensure the content avoids prohibited boilerplate words and vague claims based on the governance constraints."""
    # Strip fences and frontmatter but preserve line numbers
    text_content = strip_code_fences(v.content)

    def replacer(m):
        return "\n" * m.group(0).count("\n")

    text_content = re.sub(r"^---\s+.*?\s+---", replacer, text_content, flags=re.DOTALL)

    rules_content = v.global_rules
    content_rules = rules_content.get("content_rules", {})

    for rule_id, rule_config in content_rules.items():
        if not isinstance(rule_config, dict):
            continue
        patterns = rule_config.get("patterns")
        if not patterns:
            continue

        message = rule_config.get(
            "error_message", f"Content rule '{rule_id}' violated."
        )

        for pattern in patterns:
            for match in re.finditer(pattern, text_content, re.IGNORECASE):
                line_num = text_content.count("\n", 0, match.start()) + 1
                v.add_error(rule_id, message, line_num=line_num)
