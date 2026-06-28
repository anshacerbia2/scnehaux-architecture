from .base import BaseValidator
from .utils import extract_section_contents
import re

class GDCValidator(BaseValidator):
    doc_type_name: str = "GDC"
    def validate_type_specific(self):
        if not self.doc_meta:
            return
            
        # Enforce Downstream Guideline Interface
        if self.filename.endswith('-guideline.md'):
            # Read required downstream subsections directly from the yaml ruleset (SSOT)
            downstream_subsections = self.rules.get('rules', {}).get('structure', {}).get('required_downstream_guideline_subsections', {})
            
            if downstream_subsections:
                for parent, sub_sections in downstream_subsections.items():
                    # Extract the block starting from the parent heading until the next heading of the same or higher level
                    parent_pattern = r'^#{2,4}\s+(?:[\d\.]+\s+)?' + re.escape(parent) + r'\b'
                    parent_match = re.search(parent_pattern, self.content, re.IGNORECASE | re.MULTILINE)
                    
                    if not parent_match:
                        self.add_error('missing_section', f"Downstream Guideline is missing parent section '{parent}' for required subsections.")
                        continue
                        
                    start_idx = parent_match.end()
                    # Find the level of the parent heading
                    level = len(re.match(r'^#+', parent_match.group(0).strip()).group(0))
                    
                    # Find the next heading of the same or higher level
                    next_heading_pattern = r'^#{1,' + str(level) + r'}\s+'
                    next_match = re.search(next_heading_pattern, self.content[start_idx:], re.MULTILINE)
                    
                    if next_match:
                        parent_text = self.content[start_idx:start_idx + next_match.start()]
                    else:
                        parent_text = self.content[start_idx:]
                    last_match_idx = -1
                    last_section = None
                    
                    for section_name in sub_sections:
                        # Match standard headers (## to #####) OR bold pseudo-headers (**Section Name**)
                        pattern = r'^(?:#{2,5}\s+(?:[\d\.]+\s+)?|\*\*)' + re.escape(section_name) + r'\b'
                        match = re.search(pattern, parent_text, re.IGNORECASE | re.MULTILINE)
                        if not match:
                            self.add_error('missing_section', f"Downstream Guideline is missing mandatory subsection '{section_name}' under '{parent}'.")
                        else:
                            if match.start() < last_match_idx:
                                self.add_error('structural_integrity_violation', f"Subsection '{section_name}' is out of order. It must appear after '{last_section}'.")
                            last_match_idx = match.start()
                            last_section = section_name

