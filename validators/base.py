import re
import yaml
import os
import datetime

def parse_date(date_val):
    if isinstance(date_val, datetime.date):
        return date_val
    if isinstance(date_val, datetime.datetime):
        return date_val.date()
    if isinstance(date_val, str):
        s = date_val.strip()
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None

def clean_content_for_length(content):
    # Remove code blocks
    content_clean = re.sub(r'```[\s\S]*?```', '', content)
    # Remove inline code
    content_clean = re.sub(r'`[^`]*`', '', content_clean)
    # Remove HTML comments
    content_clean = re.sub(r'<!--[\s\S]*?-->', '', content_clean)
    # Remove markdown links, keep link text
    content_clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content_clean)
    # Strip spaces
    return content_clean.strip()

def extract_section_contents(content):
    lines = content.split('\n')
    sections = {}
    current_section = None
    current_content = []

    for line in lines:
        header_match = re.match(r'^##\s+(?:\d+(?:\.\d+)*\.?\s+)?(.+)', line)
        if header_match:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = header_match.group(1).strip().lower()
            current_content = []
        else:
            if current_section is not None:
                current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections

def normalize_section(name):
    """Normalize section name for comparison by stripping numbering."""
    return re.sub(r'^\d+(\.\d+)*\.?\s*', '', name).strip().lower()

def resolve_all_doc_ids(target_dir):
    """Scan all .md files and build a set of doc_meta.id values."""
    ids = set()
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', '.vscode', 'validators')]
        for file in files:
            if not file.endswith('.md'): continue
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
                if fm:
                    data = yaml.safe_load(fm.group(1))
                    if data and 'doc_meta' in data:
                        doc_id = data['doc_meta'].get('id')
                        if doc_id: ids.add(doc_id)
            except: pass
    return ids

def parse_frontmatter(content):
    frontmatter_match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
    if not frontmatter_match:
        return None, "Missing YAML frontmatter."
    try:
        frontmatter_data = yaml.safe_load(frontmatter_match.group(1))
        if frontmatter_data and 'doc_meta' in frontmatter_data:
            return frontmatter_data['doc_meta'], None
        else:
            return None, "YAML frontmatter is missing 'doc_meta' block."
    except Exception as e:
        return None, f"Failed to parse YAML frontmatter: {e}"

class BaseValidator:
    """Base class for all document type validators."""
    
    doc_type_name: str = "Unknown"
    
    @property
    def mandatory_sections(self):
        return []
    
    @property
    def optional_sections(self):
        return []
    
    @property
    def required_metadata_fields(self):
        return []
        
    def __init__(self, file_path: str, content: str, doc_meta: dict, rules: dict, all_doc_ids: set):
        self.file_path = file_path
        self.content = content
        self.doc_meta = doc_meta
        self.rules = rules
        self.all_doc_ids = all_doc_ids
        self.errors: list[tuple[str, str]] = []
        self.rel_path = os.path.relpath(file_path, '.').replace('\\', '/')
        self.filename = os.path.basename(file_path)
        
        # Parse lint_disable comments: <!-- lint_disable: rule_name, rule_name -->
        self.disabled_rules = set()
        for match in re.finditer(r'<!--\s*lint_disable:\s*([a-zA-Z0-9_,\s]+)\s*-->', self.content):
            rules_str = match.group(1)
            for r in rules_str.split(','):
                self.disabled_rules.add(r.strip())
    
    def add_error(self, category: str, message: str):
        if category in self.disabled_rules:
            return
        severity = self.rules.get('severity_levels', {}).get(category, 'ERROR')
        self.errors.append((severity, message))
    
    def validate(self) -> list[tuple[str, str]]:
        """Run all validations."""
        from .common import run_common_validations
        run_common_validations(self)
        self.validate_type_specific()
        return self.errors
    
    def validate_type_specific(self):
        """Override in subclass for doc-type-specific checks."""
        pass
