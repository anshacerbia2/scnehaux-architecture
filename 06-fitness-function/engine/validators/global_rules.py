import re
import os
import datetime
import logging
import yaml
from urllib.parse import unquote
from .base import BaseValidator
from engine.parsing.markdown_ast import (
    parse_date,
    clean_content_for_length,
    extract_section_contents,
    extract_links,
)

logger = logging.getLogger(__name__)

# Document types that reference deployable technology surfaces.
_TECHNOLOGY_HOLD_DOC_TYPES = frozenset({"SAD", "TDD"})

# Reserved example / placeholder namespace. IDs carrying one of these segments are
# illustrative citations inside guideline documents (e.g. 'ADR-EXAMPLE-001') and
# must NOT be resolved against the live registry.
_EXAMPLE_ID_PATTERN = re.compile(
    r"-(?:EXAMPLE|SAMPLE|XXX+|NNN+|YYYY|000)\b", re.IGNORECASE
)


def _is_example_id(ref: str) -> bool:
    """True if the referenced ID belongs to the reserved example/placeholder namespace."""
    return bool(_EXAMPLE_ID_PATTERN.search(ref))


def run_common_validations(validator: BaseValidator) -> None:
    """
    Execute the suite of global governance rules (e.g. naming, review age, NFR taxonomy,
    traceability) that apply universally across all architecture document types.
    """
    # @flow-validator: subgraph GlobalRulesPhase[Global Rules Validation Suite]
    # @flow-validator: CommonRules((Start Global Rules)) --> ValNaming["<b>_validate_naming()</b>: Check filename against GDC rules"]
    _validate_naming(validator)
    # @flow-validator: ValNaming --> ValRevAge["<b>_validate_review_age()</b>: Ensure doc is not expired/too old"]
    _validate_review_age(validator)
    # @flow-validator: ValRevAge --> ValContent["<b>_validate_content_quality()</b>: Reject prohibited/vague terms"]
    _validate_content_quality(validator)
    # @flow-validator: ValContent --> ValStruct["<b>_validate_structure()</b>: Enforce minimum section lengths"]
    _validate_structure(validator)
    # @flow-validator: ValStruct --> ValCross["<b>_validate_cross_references()</b>: Validate doc-to-doc relationships"]
    _validate_cross_references(validator)
    # @flow-validator: ValCross --> ValInternal["<b>_validate_internal_links()</b>: Prevent internal markdown link rot"]
    _validate_internal_links(validator)
    # @flow-validator: ValInternal --> ValInline["<b>_validate_inline_references()</b>: Verify inline ID citations"]
    _validate_inline_references(validator)
    # @flow-validator: ValInline --> ValQuant["<b>_validate_quantification()</b>: Require metrics/keywords in sections"]
    _validate_quantification(validator)
    # @flow-validator: ValQuant --> ValNFR["<b>_validate_nfr_taxonomy()</b>: Validate NFRs against AWS WAF pillars"]
    _validate_nfr_taxonomy(validator)
    # @flow-validator: ValNFR --> ValTech["<b>_validate_technology_hold()</b>: Flag 'HOLD' status from tech radar"]
    _validate_technology_hold(validator)
    # @flow-validator: end


def validate_draft_status(doc_meta: dict, global_rules: dict) -> list[tuple[str, str]]:
    """Check if a draft document has exceeded the maximum allowed draft age."""
    draft_errs = []
    last_reviewed_raw = doc_meta.get("last_reviewed")
    if not last_reviewed_raw:
        draft_errs.append(
            (
                "ERROR",
                "Draft document is missing 'last_reviewed' date to track draft age. Drafts cannot evade governance indefinitely.",
            )
        )
    else:
        last_reviewed = parse_date(last_reviewed_raw)
        if last_reviewed:
            age_days = (datetime.date.today() - last_reviewed).days
            max_draft_age = (
                global_rules.get("rules", {})
                .get("governance", {})
                .get("max_draft_age_days", 30)
            )
            if age_days > max_draft_age:
                draft_errs.append(
                    (
                        "ERROR",
                        f"Draft document age of {age_days} days exceeds limit of {max_draft_age} days. Must be reviewed, finalized, or deleted.",
                    )
                )
    return draft_errs


def _validate_inline_references(v: BaseValidator) -> None:
    """
    Detect architecture document IDs cited inline in prose (e.g. '(**ADR-018**)')
    that do not resolve to any document in this repository. Reported as a
    non-blocking WARNING because a citation may legitimately point at an external
    or downstream document not present in this registry.
    """
    from engine.parsing.markdown_ast import extract_doc_id_references

    own_id = (v.doc_meta or {}).get("id")
    for ref in extract_doc_id_references(v.content):
        if ref == own_id:
            continue
        if _is_example_id(ref):
            # Illustrative citation in a guideline (reserved example namespace).
            continue
        if ref not in v.all_doc_ids:
            v.add_error(
                "inline_reference_missing",
                f"Inline reference to '{ref}' does not resolve to any document in this repository "
                "(possible typo, renamed ID, or an external/downstream document).",
            )


def _validate_naming(v: BaseValidator) -> None:
    """Enforce the naming convention (filename pattern) as defined in the global governance metadata rules."""
    rules_metadata = v.global_rules.get("rules", {}).get("metadata", {})
    pattern_to_check = rules_metadata.get("filename_pattern")

    if pattern_to_check:
        if not re.match(pattern_to_check, v.filename):
            v.add_error(
                "naming_style_deviation",
                f"Filename '{v.filename}' does not match expected format: {pattern_to_check}.",
            )


def _validate_review_age(v: BaseValidator) -> None:
    """Check if a document's last review date exceeds the maximum allowed age, triggering a review requirement."""
    if not v.doc_meta:
        return
    last_reviewed_raw = v.doc_meta.get("last_reviewed")
    if last_reviewed_raw:
        last_reviewed = parse_date(last_reviewed_raw)
        if last_reviewed:
            age_days = (datetime.date.today() - last_reviewed).days
            cycle_days = v.doc_meta.get("review_cycle_days")
            rules_gov = v.global_rules.get("rules", {}).get("governance", {})
            limit = (
                int(cycle_days)
                if cycle_days is not None
                else int(rules_gov.get("max_review_age_days", 365))
            )
            if age_days > limit:
                v.add_error(
                    "old_review",
                    f"Document review age of {age_days} days exceeds limit of {limit} days (last reviewed {last_reviewed}).",
                )


def _validate_internal_links(v: BaseValidator) -> None:
    """Verify that all internal markdown links resolve to existing files in the repository to prevent link rot."""
    links = extract_links(v.content)
    base_dir = os.path.dirname(v.file_path)

    for link in links:
        # Ignore external links, mailto, and fragment-only links
        if (
            not link
            or link.startswith("http")
            or link.startswith("mailto:")
            or link.startswith("#")
        ):
            continue

        link = unquote(link)

        # Strip fragment identifier if present for file existence check
        file_part = link.split("#")[0]
        if not file_part:
            continue

        # Check if local file exists
        target_path = os.path.normpath(os.path.join(base_dir, file_part))
        if not os.path.exists(target_path):
            v.add_error(
                "cross_reference_missing",
                f"Link rot detected: Internal link '{link}' points to a non-existent file.",
            )


def _validate_content_quality(v: BaseValidator) -> None:
    """Ensure the content avoids prohibited boilerplate words and vague claims based on the governance constraints."""
    text_content = clean_content_for_length(v.content)
    rules_content = v.global_rules.get("rules", {}).get("content", {})

    prohibited_words = rules_content.get("prohibited_words", [])
    for word in prohibited_words:
        if re.search(r"\b" + re.escape(word) + r"\b", text_content, re.IGNORECASE):
            v.add_error("prohibited_word", f"Found prohibited word: '{word}'")

    ambiguity = rules_content.get("ambiguity_check", {})
    if ambiguity:
        pattern = ambiguity.get("pattern")
        message = ambiguity.get("message")
        if pattern and message:
            if re.search(pattern, text_content, re.IGNORECASE):
                v.add_error("vague_claim", message)


def _validate_structure(v: BaseValidator) -> None:
    """Validate the document structural integrity, including checking minimum section content lengths."""
    sections_map = extract_section_contents(v.content)

    # Length checks
    rules_structure = v.global_rules.get("rules", {}).get("structure", {})
    min_length = rules_structure.get("min_content_length_chars", 50)

    for section_name, section_text in sections_map.items():
        clean_text = clean_content_for_length(section_text)
        if len(clean_text) < min_length:
            v.add_error(
                "stylistic_deviation",
                f"Section '{section_name}' content length ({len(clean_text)} chars) is below minimum of {min_length} chars.",
            )


def _validate_cross_references(v: BaseValidator) -> None:
    """Verify that any architecture IDs referenced in the document metadata (e.g., parent_pad, governed_by) actually exist in the registry."""
    if not v.doc_meta:
        return

    cross_ref_fields = ["parent_pad", "parent_sad", "governed_by", "fulfilled_by"]
    for field in cross_ref_fields:
        ref_ids = v.doc_meta.get(field)
        if not ref_ids:
            continue

        if not isinstance(ref_ids, list):
            ref_ids = [ref_ids]

        for ref_id in ref_ids:
            if ref_id not in v.all_doc_ids:
                v.add_error(
                    "cross_reference_missing",
                    f"Cross-reference '{field}: {ref_id}' not found in this repository. Verify it exists in an external project repo.",
                )


def _validate_quantification(v: BaseValidator) -> None:
    """Ensure that non-functional requirements and other specific sections contain quantified metrics and mandatory keywords."""
    sections_map = extract_section_contents(v.content)
    rules_quantification = v.global_rules.get("rules", {}).get("quantification", {})
    rules_content = v.global_rules.get("rules", {}).get("content", {})

    quant_req_sections = rules_quantification.get("required_for_sections", [])
    metric_pattern = rules_quantification.get("metric_pattern")
    req_sec_keywords = rules_content.get("required_section_keywords", {})
    recommended_sec_keywords = rules_content.get("recommended_section_keywords", {})
    prohibited_sec_keywords = rules_content.get("prohibited_section_keywords", {})

    for section_name, section_text in sections_map.items():
        clean_text = clean_content_for_length(section_text)

        is_quant_req = False
        for req_sec in quant_req_sections:
            if req_sec.lower() in section_name.lower():
                is_quant_req = True
                break
        if is_quant_req and metric_pattern:
            if not re.search(metric_pattern, clean_text, re.IGNORECASE):
                # We also check for vague claims (ambiguity pattern)
                # If there's no metric, and we find a vague word, it's an ERROR (vague_claim_in_nfr)
                ambiguity = rules_content.get("ambiguity_check", {})
                if ambiguity:
                    pattern = ambiguity.get("pattern")
                    if pattern and re.search(pattern, clean_text, re.IGNORECASE):
                        v.add_error(
                            "vague_claim_in_nfr",
                            f"Section '{section_name}' requires quantified metrics. Vague claim detected instead of metrics.",
                        )
                        continue  # Don't double report
                v.add_error(
                    "vague_claim",
                    f"Section '{section_name}' requires quantified metrics but none found matching pattern '{metric_pattern}'.",
                )

        for req_sec, keywords in req_sec_keywords.items():
            if req_sec.lower() in section_name.lower():
                for kw in keywords:
                    # Suffix-tolerant: a required keyword matches its inflections/plurals
                    # (e.g. 'Domain Event' satisfies 'Domain Events', 'Bounded Context' -> 'Bounded Contexts').
                    if not re.search(
                        r"\b" + re.escape(kw) + r"\w*", clean_text, re.IGNORECASE
                    ):
                        v.add_error(
                            "missing_section_keyword",
                            f"Section '{section_name}' is missing mandatory keyword: '{kw}'",
                        )

        # Recommended (non-blocking) sub-content: type-specific items that should be
        # addressed where applicable, or explicitly marked Not Applicable.
        for rec_sec, keywords in recommended_sec_keywords.items():
            if rec_sec.lower() in section_name.lower():
                for kw in keywords:
                    if not re.search(
                        r"\b" + re.escape(kw) + r"\w*", clean_text, re.IGNORECASE
                    ):
                        v.add_error(
                            "recommended_keyword_missing",
                            f"Section '{section_name}' is recommended to address '{kw}' (or mark it Not Applicable).",
                        )

        for banned_sec, keywords in prohibited_sec_keywords.items():
            if banned_sec.lower() in section_name.lower():
                for kw in keywords:
                    if re.search(
                        r"\b" + re.escape(kw) + r"\b", clean_text, re.IGNORECASE
                    ):
                        v.add_error(
                            "prohibited_word",
                            f"Section '{section_name}' contains prohibited governance boilerplate word: '{kw}'",
                        )


def _validate_nfr_taxonomy(v: BaseValidator) -> None:
    """
    Ensure NFRs strictly map to AWS WAF pillars (GDC-000 Section 2.4).
    """
    sections_map = extract_section_contents(v.content)
    rules_quantification = v.global_rules.get("rules", {}).get("quantification", {})
    aws_waf_pillars = rules_quantification.get("aws_waf_pillars", [])

    if not aws_waf_pillars:
        return

    for section_name, section_text in sections_map.items():
        if "non-functional requirements" in section_name.lower():
            # Find all ### headers in this section
            sub_headers = re.findall(r"^###\s+(.*)$", section_text, flags=re.MULTILINE)
            for header in sub_headers:
                clean_header = header.strip()
                # Check if it matches any AWS WAF Pillar (case insensitive)
                matched = any(
                    clean_header.lower() == p.lower() for p in aws_waf_pillars
                )
                if not matched:
                    v.add_error(
                        "structural_integrity_violation",
                        f"NFR taxonomy violation: '{clean_header}' is not a recognized AWS WAF Pillar. Allowed pillars: {', '.join(aws_waf_pillars)}.",
                    )


def _validate_technology_hold(v: BaseValidator) -> None:
    """
    Check if the document references technologies on HOLD status in the tech radar.
    Only fires for document types that describe deployable technology surfaces (SAD, TDD).
    Centralised here to eliminate DRY violation (previously duplicated in sad.py and tdd.py).
    """
    if v.doc_type_name not in _TECHNOLOGY_HOLD_DOC_TYPES:
        return

    tech_radar_path = os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "..",
            "01-enterprise",
            "tech-radar.yaml",
        )
    )
    if not os.path.exists(tech_radar_path):
        return

    try:
        with open(tech_radar_path, "r", encoding="utf-8") as f:
            radar = yaml.safe_load(f)
            hold_techs = radar.get("technology_radar", {}).get("hold", [])
    except Exception as e:
        logger.debug("Failed to load tech radar from '%s': %s", tech_radar_path, e)
        return

    if not hold_techs:
        return

    clean_text = clean_content_for_length(v.content)
    for tech_entry in hold_techs:
        tech = tech_entry.get("name") if isinstance(tech_entry, dict) else tech_entry
        if not tech:
            continue
        if re.search(r"\b" + re.escape(tech) + r"\b", clean_text, re.IGNORECASE):
            v.add_error(
                "technology_hold_violation",
                f"Document implements technology on HOLD status: '{tech}'.",
            )
