import os
import yaml
import logging
import datetime
from .base import BaseValidator
from engine.parsing.markdown_ast import parse_date

logger = logging.getLogger(__name__)

# Document types that reference deployable technology surfaces.
_TECHNOLOGY_HOLD_DOC_TYPES = frozenset({"SAD", "TDD"})


def validate_exempt_age(doc_meta: dict, doc_status: str, violation_severity: str, global_rules: dict) -> list[tuple[str, str]]:
    """
    Check if an exempt document (like a draft) has exceeded the maximum allowed age.
    This prevents documents from indefinitely evading governance while holding an exempt status.

    <pre>Args:
        - doc_meta (dict): Parsed frontmatter metadata of the document.
        - doc_status (str): The normalized document status evaluated by the CLI orchestrator.
        - violation_severity (str): The severity level to assign if a violation is found.
        - global_rules (dict): The global governance rules containing 'max_draft_age_days'.

    Returns:
        list[tuple[str, str]]: A list of (severity, error_message) tuples. Returns an empty list if no violations are found.

    Raises:
        None: Does not raise exceptions; missing or unparseable dates are safely handled and appended as errors.
    </pre>
    """
    draft_errs = []
    created_date_raw = doc_meta.get("created_date")
    
    if not created_date_raw:
        draft_errs.append(
            (
                violation_severity,
                f"Document with status '{doc_status}' is missing 'created_date'. It cannot evade governance indefinitely.",
            )
        )
    else:
        created_date = parse_date(created_date_raw)
        if created_date:
            age_days = (datetime.date.today() - created_date).days
            try:
                max_draft_age = global_rules["content_rules"]["max_draft_age_days"]["value"]
                err_msg_template = global_rules["content_rules"]["max_draft_age_days"]["error_message"]
            except KeyError as e:
                raise KeyError(f"Missing required configuration in base.schema.json: {e}")
            
            if age_days > max_draft_age:
                err_msg = err_msg_template.format(doc_status=doc_status, age_days=age_days, limit=max_draft_age)
                draft_errs.append(
                    (
                        violation_severity,
                        err_msg,
                    )
                )
    return draft_errs


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
            rules_meta = v.global_rules.get("content_rules", {})
            rule_config = rules_meta.get("max_review_age_days", {})
            default_limit = rule_config.get("value", 365)

            limit = int(cycle_days) if cycle_days is not None else int(default_limit)
            if age_days > limit:
                error_msg = rule_config.get(
                    "error_message",
                    "Document review age of {age_days} days exceeds limit of {limit} days.",
                ).format(age_days=age_days, limit=limit, last_reviewed=last_reviewed)

                v.add_error(
                    "review_age_violation",
                    error_msg,
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
                    f"Cross-referenced document '{ref_id}' not found in this repository.",
                )


def _validate_technologies_whitelist(v: BaseValidator) -> None:
    """
    Enforce strict whitelist technology validation based on structured metadata.
    Instead of full-text scanning, this rule checks the 'technologies' array in doc_meta.
    Every technology (and its 'base') MUST exist in the Enterprise Tech Radar.
    If it exists but is on HOLD, a violation is thrown.
    """
    if v.doc_type_name not in _TECHNOLOGY_HOLD_DOC_TYPES:
        return

    if not v.doc_meta:
        return

    technologies = v.doc_meta.get("technologies")
    if not technologies:
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
            tech_radar = radar.get("technology_radar", {})
    except Exception as e:
        logger.debug("Failed to load tech radar from '%s': %s", tech_radar_path, e)
        return

    # Build maps of approved and hold technologies
    approved_techs = set()
    hold_techs = set()

    for category in ["adopt", "trial", "assess"]:
        for entry in tech_radar.get(category, []):
            name = entry.get("name") if isinstance(entry, dict) else entry
            if name:
                approved_techs.add(name.lower())

    for entry in tech_radar.get("hold", []):
        name = entry.get("name") if isinstance(entry, dict) else entry
        if name:
            hold_techs.add(name.lower())

    for tech in technologies:
        if not isinstance(tech, dict):
            continue

        tech_name = tech.get("name")
        tech_base = tech.get("base")

        items_to_check = []
        if tech_name:
            items_to_check.append(tech_name)
        if tech_base:
            items_to_check.append(tech_base)

        for item in items_to_check:
            item_lower = item.lower()
            if item_lower in hold_techs:
                v.add_error(
                    "technology_hold_violation",
                    f"Document implements technology on HOLD status: '{item}'.",
                )
            elif item_lower not in approved_techs:
                v.add_error(
                    "unapproved_technology",
                    f"Technology '{item}' is not defined in the Enterprise Tech Radar. It must be assessed before use.",
                )
