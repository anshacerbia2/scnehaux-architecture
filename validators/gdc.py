from .base import BaseValidator
import re

class GDCValidator(BaseValidator):
    def validate_type_specific(self):
        if not self.doc_meta:
            return
            
        rules_metadata = self.rules['rules'].get('metadata', {})
        allowed_statuses = rules_metadata.get('allowed_statuses', [])
        allowed_classifications = rules_metadata.get('allowed_classifications', [])
        
        status = self.doc_meta.get('status')
        if status and allowed_statuses and status not in allowed_statuses:
            self.add_error('missing_metadata', f"Status '{status}' is not in allowed list: {allowed_statuses}.")
            
        classification = self.doc_meta.get('classification')
        if classification and allowed_classifications and classification not in allowed_classifications:
            self.add_error('missing_metadata', f"Classification '{classification}' is not in allowed list: {allowed_classifications}.")

        # Enforce Downstream Guideline Interface
        if self.filename.endswith('-guideline.md'):
            # The 4 pillars might be h3 or h4 headers.
            # We check for exact case-insensitive matches using regex.
            pillars = {
                'Taxonomy or Directory Structure': r'#{2,4}\s+.*\b(taxonomy|directory structure)\b',
                'Naming Convention': r'#{2,4}\s+.*\bnaming convention(s)?\b',
                'Section Semantics': r'#{2,4}\s+.*\bsection semantics\b',
                'Metadata Schema': r'#{2,4}\s+.*\bmetadata schema\b'
            }
            
            for pillar_name, pattern in pillars.items():
                if not re.search(pattern, self.content, re.IGNORECASE):
                    self.add_error('missing_section', f"Downstream Guideline is missing mandatory '{pillar_name}' heading (h2-h4).")

