from .base import BaseValidator

class TDDValidator(BaseValidator):
    def validate_type_specific(self):
        if not self.doc_meta:
            return

        # TDD must have parent_sad traceability
        parent_sad = self.doc_meta.get('parent_sad')
        if parent_sad is None or (isinstance(parent_sad, list) and len(parent_sad) == 0):
            self.add_error('traceability_violation',
                "TDD document is missing required traceability field: 'parent_sad'.")
        else:
            sad_ids = parent_sad if isinstance(parent_sad, list) else [parent_sad]
            for sad_id in sad_ids:
                if sad_id not in self.all_doc_ids:
                    self.add_error('traceability_violation',
                        f"TDD 'parent_sad' in metadata references SAD '{sad_id}' which does not exist in the repository.")

        # Check for hold technologies
        import os
        import yaml
        
        tech_radar_path = os.path.join(os.path.dirname(__file__), '..', '01-enterprise', 'tech-radar.yaml')
        hold_techs = []
        if os.path.exists(tech_radar_path):
            try:
                with open(tech_radar_path, 'r', encoding='utf-8') as f:
                    radar = yaml.safe_load(f)
                    hold_techs = radar.get('technology_radar', {}).get('hold', [])
            except Exception:
                pass

        if hold_techs:
            import re
            from .utils import clean_content_for_length
            content_str = getattr(self, 'content', '')
            clean_text = clean_content_for_length(content_str)
            for tech in hold_techs:
                if re.search(r'\b' + re.escape(tech) + r'\b', clean_text, re.IGNORECASE):
                    self.add_error('technology_hold_violation', f"Document implements technology on HOLD status: '{tech}'.")
