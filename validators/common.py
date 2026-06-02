import re
import datetime
from .base import BaseValidator, parse_date, clean_content_for_length, extract_section_contents, normalize_section

def run_common_validations(validator: BaseValidator):
    _validate_naming(validator)
    _validate_metadata(validator)
    _validate_exceptions(validator)
    _validate_review_age(validator)
    _validate_content_quality(validator)
    _validate_structure(validator)
    _validate_cross_references(validator)
    _validate_quantification(validator)

def _validate_naming(v: BaseValidator):
    rules_fed = v.rules['rules'].get('federated_governance', {})
    naming_conventions = rules_fed.get('naming_conventions', {})
    pattern_to_check = None
    expected_format_desc = ""

    if v.rel_path.startswith('05-decisions/'):
        if '/_global/' in v.rel_path:
            pattern_to_check = naming_conventions.get('global_adr_pattern')
            expected_format_desc = "Global ADR (ADR-GLB-###-slug.md)"
        else:
            pattern_to_check = naming_conventions.get('domain_adr_pattern')
            expected_format_desc = "Domain ADR (ADR-[DOM]-[CAP]-###-slug.md)"
    elif v.rel_path.startswith('02-standards/'):
        if '/_global/' in v.rel_path:
            pattern_to_check = naming_conventions.get('global_std_pattern')
            expected_format_desc = "Global Standard (STD-GLB-###-slug.md)"
        else:
            pattern_to_check = naming_conventions.get('domain_std_pattern')
            expected_format_desc = "Domain Standard (STD-[DOM]-[CAP]-###[letter]-slug.md)"
    elif v.rel_path.startswith('03-platform/'):
        pattern_to_check = r'^[a-z0-9-]+\.pad\.md$'
        expected_format_desc = "PAD ([domain]-platform.pad.md)"
    elif v.rel_path.startswith('04-application/'):
        pattern_to_check = r'^[a-z0-9-]+\.sad\.md$'
        expected_format_desc = "SAD ([system-name].sad.md)"
    elif v.rel_path.startswith('00-governance/'):
        pattern_to_check = r'^GDC-\d{3}-[a-z0-9-]+\.md$'
        expected_format_desc = "Governance (GDC-###-slug.md)"
    elif v.rel_path.startswith('01-enterprise/'):
        pattern_to_check = r'^EAD-\d{3}-[a-z0-9-]+\.md$'
        expected_format_desc = "Enterprise Architecture (EAD-###-slug.md)"

    if pattern_to_check:
        if not re.match(pattern_to_check, v.filename):
            v.add_error('naming_style_deviation', f"Filename '{v.filename}' does not match expected format for {expected_format_desc}.")

def _validate_metadata(v: BaseValidator):
    if not v.doc_meta:
        return
    rules_metadata = v.rules['rules'].get('metadata', {})
    
    # Required metadata fields are checked via the property
    for field in v.required_metadata_fields:
        if field not in v.doc_meta:
            v.add_error('missing_metadata', f"Missing required metadata field: '{field}' under doc_meta.")
            
    # Version Semver Check
    version = v.doc_meta.get('version')
    if version and rules_metadata.get('version_format') == 'semver':
        if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
            v.add_error('missing_metadata', f"Version '{version}' is not in valid semver format (X.Y.Z).")

    # Allowed Classifications Check
    classification = v.doc_meta.get('classification')
    allowed_classifications = rules_metadata.get('allowed_classifications', [])
    if classification and allowed_classifications:
        if classification not in allowed_classifications:
            v.add_error('missing_metadata', f"Classification '{classification}' is not in allowed list: {allowed_classifications}.")

def _validate_exceptions(v: BaseValidator):
    if not v.doc_meta:
        return
    status = str(v.doc_meta.get('status', '')).lower()
    exception_reason = v.doc_meta.get('exception_reason')
    is_exception_doc = status in ('exception', 'waiver') or exception_reason is not None

    if is_exception_doc:
        rules_fed = v.rules['rules'].get('federated_governance', {})
        exception_meta_fields = rules_fed.get('exception_meta_fields', [])
        for field in exception_meta_fields:
            if field not in v.doc_meta:
                v.add_error('missing_exception_reason', f"Exception document is missing required field: '{field}' under doc_meta.")
        
        # Expired Exception Check
        expiry_date_raw = v.doc_meta.get('expiry_date')
        if expiry_date_raw:
            expiry_date = parse_date(expiry_date_raw)
            if expiry_date:
                if expiry_date < datetime.date.today():
                    v.add_error('exception_expired', f"Exception waiver has expired on {expiry_date}.")
            else:
                v.add_error('missing_exception_reason', f"Invalid date format for expiry_date: '{expiry_date_raw}'. Use YYYY-MM-DD.")

def _validate_review_age(v: BaseValidator):
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
        else:
            v.add_error('missing_metadata', f"Invalid date format for last_reviewed: '{last_reviewed_raw}'. Use YYYY-MM-DD.")

def _validate_content_quality(v: BaseValidator):
    text_content = clean_content_for_length(v.content)
    rules_content = v.rules['rules'].get('content', {})
    
    # Prohibited Words
    prohibited_words = rules_content.get('prohibited_words', [])
    for word in prohibited_words:
        if re.search(r'\b' + re.escape(word) + r'\b', text_content, re.IGNORECASE):
            v.add_error('prohibited_word', f"Found prohibited word: '{word}'")

    # Ambiguity Check
    ambiguity = rules_content.get('ambiguity_check', {})
    if ambiguity:
        pattern = ambiguity.get('pattern')
        message = ambiguity.get('message')
        if pattern and message:
            if re.search(pattern, text_content, re.IGNORECASE):
                v.add_error('vague_claim', message)

def _validate_structure(v: BaseValidator):
    sections_map = extract_section_contents(v.content)
    
    found_sections = []
    
    # Check if mandatory sections are present (using normalized substring match)
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
    section_order_indices = []
    lines = v.content.split('\n')
    for name in found_sections:
        line_no = -1
        for l_num, line in enumerate(lines):
            if re.search(r'^##\s+(?:\d+(?:\.\d+)*\.?\s+)?' + re.escape(name), line, re.IGNORECASE):
                line_no = l_num
                break
        if line_no != -1:
            section_order_indices.append((line_no, name))

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

def _validate_cross_references(v: BaseValidator):
    """Validate referential integrity against other docs in the repo."""
    if not v.doc_meta:
        return
        
    cross_ref_fields = ['parent_pad', 'parent_sad', 'governed_by']
    for field in cross_ref_fields:
        ref_ids = v.doc_meta.get(field)
        if not ref_ids:
            continue
            
        if not isinstance(ref_ids, list):
            ref_ids = [ref_ids]
            
        for ref_id in ref_ids:
            if ref_id not in v.all_doc_ids:
                v.add_error('cross_reference_missing', f"Cross-reference '{field}: {ref_id}' not found in this repository. Verify it exists in an external project repo.")

def _validate_quantification(v: BaseValidator):
    sections_map = extract_section_contents(v.content)
    rules_quantification = v.rules['rules'].get('quantification', {})
    rules_content = v.rules['rules'].get('content', {})
    
    quant_req_sections = rules_quantification.get('required_for_sections', [])
    metric_pattern = rules_quantification.get('metric_pattern')
    req_sec_keywords = rules_content.get('required_section_keywords', {})
    prohibited_sec_keywords = rules_content.get('prohibited_section_keywords', {})

    for section_name, section_text in sections_map.items():
        clean_text = clean_content_for_length(section_text)
        
        is_quant_req = False
        for req_sec in quant_req_sections:
            if req_sec.lower() in section_name.lower():
                is_quant_req = True
                break
        if is_quant_req and metric_pattern:
            if not re.search(metric_pattern, clean_text):
                v.add_error('vague_claim', f"Section '{section_name}' requires quantified metrics but none found matching pattern '{metric_pattern}'.")

        for req_sec, keywords in req_sec_keywords.items():
            if req_sec.lower() in section_name.lower():
                for kw in keywords:
                    if not re.search(r'\b' + re.escape(kw) + r'\b', clean_text, re.IGNORECASE):
                        v.add_error('missing_section_keyword', f"Section '{section_name}' is missing mandatory keyword: '{kw}'")

        for banned_sec, keywords in prohibited_sec_keywords.items():
            if banned_sec.lower() == section_name.lower():
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', clean_text, re.IGNORECASE):
                        v.errors.append(('WARNING', f"Section '{section_name}' contains prohibited governance boilerplate word: '{kw}'"))
