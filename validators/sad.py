from .base import BaseValidator

class SADValidator(BaseValidator):
    def validate_type_specific(self):
        if not self.doc_meta:
            return

        # SAD must have parent_pad traceability
        parent_pad = self.doc_meta.get('parent_pad')
        if parent_pad is None or (isinstance(parent_pad, list) and len(parent_pad) == 0):
            self.add_error('traceability_violation',
                "SAD document is missing required traceability field: 'parent_pad'.")
        else:
            pad_ids = parent_pad if isinstance(parent_pad, list) else [parent_pad]
            for pad_id in pad_ids:
                if pad_id not in self.all_doc_ids:
                    self.add_error('traceability_violation',
                        f"SAD 'parent_pad' in metadata references PAD '{pad_id}' which does not exist in the repository.")
                else:
                    # Bidirectional check: ensure PAD recognizes this SAD
                    pad_meta = self.all_doc_metadata.get(pad_id)
                    if pad_meta:
                        fulfilled_by = pad_meta.get('fulfilled_by')
                        fulfilled_list = fulfilled_by if isinstance(fulfilled_by, list) else ([fulfilled_by] if fulfilled_by else [])
                        self_id = self.doc_meta.get('id')
                        if self_id not in fulfilled_list:
                            self.add_error('traceability_violation',
                                f"SAD '{self_id}' references parent PAD '{pad_id}', but PAD '{pad_id}' does not list this SAD in its 'fulfilled_by'. Bidirectional traceability is broken.")

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
