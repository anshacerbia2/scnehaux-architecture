import re
import os
import datetime
import logging
import yaml
from urllib.parse import unquote
from .base import BaseValidator
from .utils import parse_date, clean_content_for_length, extract_section_contents, normalize_section, extract_links, get_section_order
from .schema import DocMeta
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# Document types that reference deployable technology surfaces.
_TECHNOLOGY_HOLD_DOC_TYPES = frozenset({'SAD', 'TDD'})

def run_common_validations(validator: BaseValidator) -> None:
    _validate_naming(validator)
    _validate_metadata_schema(validator)
    _validate_review_age(validator)
    _validate_content_quality(validator)
    _validate_structure(validator)
    _validate_cross_references(validator)
    _validate_internal_links(validator)
    _validate_inline_references(validator)
    _validate_quantification(validator)
    _validate_technology_hold(validator)

def _validate_inline_references(v: BaseValidator) -> None:
    """
    Detect architecture document IDs cited inline in prose (e.g. '(**ADR-018**)')
    that do not resolve to any document in this repository. Reported as a
    non-blocking WARNING because a citation may legitimately point at an external
    or downstream document not present in this registry.
    """
    from .utils import extract_doc_id_references
    own_id = (v.doc_meta or {}).get('id')
    for ref in extract_doc_id_references(v.content):
        if ref == own_id:
            continue
        if ref not in v.all_doc_ids:
            v.add_error('inline_reference_missing',
                f"Inline reference to '{ref}' does not resolve to any document in this repository "
                "(possible typo, renamed ID, or an external/downstream document).")

def _validate_naming(v: BaseValidator) -> None:
    rules_metadata = v.rules.get('rules', {}).get('metadata', {})
    pattern_to_check = rules_metadata.get('filename_pattern')

    if pattern_to_check:
        if not re.match(pattern_to_check, v.filename):
            v.add_error('naming_style_deviation', f"Filename '{v.filename}' does not match expected format: {pattern_to_check}.")

def _validate_metadata_schema(v: BaseValidator) -> None:
    if not v.doc_meta:
        return
        
    # 1. Pydantic structural and type validation
    try:
        parsed_meta = DocMeta(**v.doc_meta)
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(map(str, err["loc"]))
            v.add_error('missing_metadata', f"Schema validation failed on '{loc}': {err['msg']}")
        return
        
    # 2. Check for required fields defined in governance rules dynamically
    for field in v.required_metadata_fields:
        if field not in v.doc_meta:
            v.add_error('missing_metadata', f"Missing required metadata field: '{field}' under doc_meta.")
            
    # 3. Check allowed statuses and classifications dynamically based on YAML rules
    rules_metadata = v.rules.get('rules', {}).get('metadata', {})
    allowed_statuses = rules_metadata.get('allowed_statuses', [])
    allowed_classifications = rules_metadata.get('allowed_classifications', [])
    
    status = v.doc_meta.get('status')
    if status and allowed_statuses and status not in allowed_statuses:
        v.add_error('missing_metadata', f"Status '{status}' is not in allowed list: {allowed_statuses}.")
        
    classification = v.doc_meta.get('classification')
    if classification and allowed_classifications and classification not in allowed_classifications:
        v.add_error('missing_metadata', f"Classification '{classification}' is not in allowed list: {allowed_classifications}.")
            
def _validate_review_age(v: BaseValidator) -> None:
    if not v.doc_meta:
        return
    last_reviewed_raw = v.doc_meta.get('last_reviewed')
    if last_reviewed_raw:
        last_reviewed = parse_date(last_reviewed_raw)
        if last_reviewed:
            age_days = (datetime.date.today() - last_reviewed).days
            cycle_days = v.doc_meta.get('review_cycle_days')
            rules_gov = v.rules['rules'].get('governance', {})
            limit = int(cycle_days) if cycle_days is not None else int(rules_gov.get('max_review_age_days', 365))
            if age_days > limit:
                v.add_error('old_review', f"Document review age of {age_days} days exceeds limit of {limit} days (last reviewed {last_reviewed}).")

def _validate_internal_links(v: BaseValidator) -> None:
    links = extract_links(v.content)
    base_dir = os.path.dirname(v.file_path)
    
    for link in links:
        # Ignore external links, mailto, and fragment-only links
        if not link or link.startswith('http') or link.startswith('mailto:') or link.startswith('#'):
            continue
            
        link = unquote(link)
            
        # Strip fragment identifier if present for file existence check
        file_part = link.split('#')[0]
        if not file_part:
            continue
            
        # Check if local file exists
        target_path = os.path.normpath(os.path.join(base_dir, file_part))
        if not os.path.exists(target_path):
            v.add_error('cross_reference_missing', f"Link rot detected: Internal link '{link}' points to a non-existent file.")

def _validate_content_quality(v: BaseValidator) -> None:
    text_content = clean_content_for_length(v.content)
    rules_content = v.rules['rules'].get('content', {})
    
    prohibited_words = rules_content.get('prohibited_words', [])
    for word in prohibited_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text_content, re.IGNORECASE):
            v.add_error('prohibited_word', f"Found prohibited word: '{word}'")

    ambiguity = rules_content.get('ambiguity_check', {})
    if ambiguity:
        pattern = ambiguity.get('pattern')
        message = ambiguity.get('message')
        if pattern and message:
            if re.search(pattern, text_content, re.IGNORECASE):
                v.add_error('vague_claim', message)

def _validate_structure(v: BaseValidator) -> None:
    sections_map = extract_section_contents(v.content)
    found_sections = []
    
    for section_name in v.mandatory_sections:
        normalized_mandatory = normalize_section(section_name)
        found = False
        for s_key in sections_map.keys():
            if normalized_mandatory in normalize_section(s_key):
                found_sections.append(section_name)
                found = True
                break
        if not found:
            v.add_error('missing_section', f"Missing mandatory section: '{section_name}'")

    # Order check
    ordered_sections_ast = get_section_order(v.content)
    
    section_order_indices = []
    for name in found_sections:
        idx = -1
        normalized_target = normalize_section(name)
        for i, ast_name in enumerate(ordered_sections_ast):
            if normalized_target in normalize_section(ast_name):
                idx = i
                break
        if idx != -1:
            section_order_indices.append((idx, name))

    section_order_indices.sort(key=lambda x: x[0])
    ordered_found = [name for _, name in section_order_indices]

    expected_order = {name: i for i, name in enumerate(v.mandatory_sections)}
    last_expected_idx = -1
    last_name = ""
    for name in ordered_found:
        curr_expected_idx = expected_order[name]
        if curr_expected_idx < last_expected_idx:
            v.add_error('structural_integrity_violation', f"Structure violation: section '{name}' appears after '{last_name}', violating expected order.")
        last_expected_idx = curr_expected_idx
        last_name = name

    # Unrecognized section and length checks
    rules_structure = v.rules['rules'].get('structure', {})
    min_length = rules_structure.get('min_content_length_chars', 50)
    
    for section_name, section_text in sections_map.items():
        clean_text = clean_content_for_length(section_text)
        is_recognized = False
        normalized_found = normalize_section(section_name)
        orig_name = section_name
        
        for s in list(v.mandatory_sections) + list(v.optional_sections):
            if normalize_section(s) in normalized_found:
                orig_name = s
                is_recognized = True
                break
        
        if (v.mandatory_sections or v.optional_sections) and not is_recognized:
            v.add_error('unrecognized_section', f"Unrecognized section '{section_name}' found. It is not defined in the governance template.")
            
        if len(clean_text) < min_length:
            v.add_error('stylistic_deviation', f"Section '{orig_name}' content length ({len(clean_text)} chars) is below minimum of {min_length} chars.")

def _validate_cross_references(v: BaseValidator) -> None:
    if not v.doc_meta:
        return
        
    cross_ref_fields = ['parent_pad', 'parent_sad', 'governed_by', 'fulfilled_by']
    for field in cross_ref_fields:
        ref_ids = v.doc_meta.get(field)
        if not ref_ids:
            continue
            
        if not isinstance(ref_ids, list):
            ref_ids = [ref_ids]
            
        for ref_id in ref_ids:
            if ref_id not in v.all_doc_ids:
                v.add_error('cross_reference_missing', f"Cross-reference '{field}: {ref_id}' not found in this repository. Verify it exists in an external project repo.")

def _validate_quantification(v: BaseValidator) -> None:
    sections_map = extract_section_contents(v.content)
    rules_quantification = v.rules['rules'].get('quantification', {})
    rules_content = v.rules['rules'].get('content', {})
    
    quant_req_sections = rules_quantification.get('required_for_sections', [])
    metric_pattern = rules_quantification.get('metric_pattern')
    req_sec_keywords = rules_content.get('required_section_keywords', {})
    recommended_sec_keywords = rules_content.get('recommended_section_keywords', {})
    prohibited_sec_keywords = rules_content.get('prohibited_section_keywords', {})

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
                ambiguity = rules_content.get('ambiguity_check', {})
                if ambiguity:
                    pattern = ambiguity.get('pattern')
                    if pattern and re.search(pattern, clean_text, re.IGNORECASE):
                        v.add_error('vague_claim_in_nfr', f"Section '{section_name}' requires quantified metrics. Vague claim detected instead of metrics.")
                        continue # Don't double report
                v.add_error('vague_claim', f"Section '{section_name}' requires quantified metrics but none found matching pattern '{metric_pattern}'.")

        for req_sec, keywords in req_sec_keywords.items():
            if req_sec.lower() in section_name.lower():
                for kw in keywords:
                    # Suffix-tolerant: a required keyword matches its inflections/plurals
                    # (e.g. 'Domain Event' satisfies 'Domain Events', 'Bounded Context' -> 'Bounded Contexts').
                    if not re.search(r'\b' + re.escape(kw) + r'\w*', clean_text, re.IGNORECASE):
                        v.add_error('missing_section_keyword', f"Section '{section_name}' is missing mandatory keyword: '{kw}'")

        # Recommended (non-blocking) sub-content: type-specific items that should be
        # addressed where applicable, or explicitly marked Not Applicable.
        for rec_sec, keywords in recommended_sec_keywords.items():
            if rec_sec.lower() in section_name.lower():
                for kw in keywords:
                    if not re.search(r'\b' + re.escape(kw) + r'\w*', clean_text, re.IGNORECASE):
                        v.add_error('recommended_keyword_missing', f"Section '{section_name}' is recommended to address '{kw}' (or mark it Not Applicable).")

        for banned_sec, keywords in prohibited_sec_keywords.items():
            if banned_sec.lower() in section_name.lower():
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', clean_text, re.IGNORECASE):
                        v.add_error('prohibited_word', f"Section '{section_name}' contains prohibited governance boilerplate word: '{kw}'")

def _validate_technology_hold(v: BaseValidator) -> None:
    """
    Check if the document references technologies on HOLD status in the tech radar.
    Only fires for document types that describe deployable technology surfaces (SAD, TDD).
    Centralised here to eliminate DRY violation (previously duplicated in sad.py and tdd.py).
    """
    if v.doc_type_name not in _TECHNOLOGY_HOLD_DOC_TYPES:
        return

    tech_radar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '01-enterprise', 'tech-radar.yaml')
    if not os.path.exists(tech_radar_path):
        return

    try:
        with open(tech_radar_path, 'r', encoding='utf-8') as f:
            radar = yaml.safe_load(f)
            hold_techs = radar.get('technology_radar', {}).get('hold', [])
    except Exception as e:
        logger.debug("Failed to load tech radar from '%s': %s", tech_radar_path, e)
        return

    if not hold_techs:
        return

    clean_text = clean_content_for_length(v.content)
    for tech in hold_techs:
        if re.search(r'\b' + re.escape(tech) + r'\b', clean_text, re.IGNORECASE):
            v.add_error('technology_hold_violation', f"Document implements technology on HOLD status: '{tech}'.")

