import re
import yaml
import datetime
from typing import Optional, Union, Any
from markdown_it import MarkdownIt

def parse_date(date_val: Union[datetime.datetime, datetime.date, str, None]) -> Optional[datetime.date]:
    if isinstance(date_val, datetime.datetime):
        return date_val.date()
    if isinstance(date_val, datetime.date):
        return date_val
    if isinstance(date_val, str):
        s = date_val.strip()
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None

def extract_section_contents(content: str) -> dict[str, str]:
    # Strip YAML frontmatter to prevent Setext heading misinterpretation
    content_no_fm = re.sub(r'^---\s+(.*?)\s+---', '', content, flags=re.DOTALL)
    md = MarkdownIt()
    tokens = md.parse(content_no_fm)
    
    sections = {}
    current_section = None
    lines = content_no_fm.split('\n')
    last_section_start = 0
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == 'heading_open' and token.tag == 'h2':
            # Save previous section
            if current_section is not None:
                end_line = token.map[0] if token.map else len(lines)
                sections[current_section] = '\n'.join(lines[last_section_start:end_line]).strip()
            
            # Find heading title
            i += 1
            if i < len(tokens) and tokens[i].type == 'inline':
                current_section = tokens[i].content.strip().lower()
            
            # Move past heading_close
            i += 1
            if i < len(tokens) and tokens[i].type == 'heading_close':
                heading_close_token = tokens[i]
                if heading_close_token.map:
                    last_section_start = heading_close_token.map[1]
                else:
                    # fallback to previous token map
                    if tokens[i-2].map:
                        last_section_start = tokens[i-2].map[1]
        i += 1
        
    if current_section is not None:
        sections[current_section] = '\n'.join(lines[last_section_start:]).strip()
        
    return sections

def clean_content_for_length(content: str) -> str:
    content_no_fm = re.sub(r'^---\s+(.*?)\s+---', '', content, flags=re.DOTALL)
    md = MarkdownIt()
    tokens = md.parse(content_no_fm)
    text = []
    
    def walk(tokens_list: list[Any]) -> None:
        for t in tokens_list:
            if t.type == 'text' or t.type == 'code_inline':
                text.append(t.content)
            elif t.type == 'softbreak' or t.type == 'hardbreak':
                text.append(' ')
            if getattr(t, 'children', None):
                walk(t.children)

    for t in tokens:
        # Ignore code blocks for semantic checks
        if t.type in ('fence', 'code_block', 'html_block'):
            continue
        if t.type == 'inline':
            walk(t.children)
        else:
            if getattr(t, 'children', None):
                walk(t.children)
                
    return ' '.join(text).strip()

def extract_links(content: str) -> list[str]:
    content_no_fm = re.sub(r'^---\s+(.*?)\s+---', '', content, flags=re.DOTALL)
    md = MarkdownIt()
    tokens = md.parse(content_no_fm)
    links = []
    
    def walk(tokens_list: list[Any]) -> None:
        for t in tokens_list:
            if t.type == 'link_open' and t.attrs:
                if isinstance(t.attrs, dict):
                    if 'href' in t.attrs:
                        links.append(t.attrs['href'])
                else:
                    for attr in t.attrs:
                        if attr[0] == 'href':
                            links.append(attr[1])
            if getattr(t, 'children', None):
                walk(t.children)
                
    for t in tokens:
        if t.type == 'inline':
            walk(t.children)
            
    return links

def normalize_section(name: str) -> str:
    """Normalize section name for comparison by stripping numbering."""
    return re.sub(r'^\d+(\.\d+)*\.?\s*', '', name).strip().lower()

def get_section_order(content: str) -> list[str]:
    content_no_fm = re.sub(r'^---\s+(.*?)\s+---', '', content, flags=re.DOTALL)
    md = MarkdownIt()
    tokens = md.parse(content_no_fm)
    
    order = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == 'heading_open' and token.tag == 'h2':
            i += 1
            if i < len(tokens) and tokens[i].type == 'inline':
                order.append(tokens[i].content.strip().lower())
        i += 1
    return order

def parse_frontmatter(content: str) -> tuple[Optional[dict[str, Any]], Optional[str]]:
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

def strip_code_fences(content: str) -> str:
    """
    Remove fenced code blocks (``` and ~~~) so that directives or examples
    embedded inside documentation (e.g. an illustrative `<!-- lint_disable: ... -->`)
    are NOT parsed as live directives by the engine.
    """
    no_fence = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    no_fence = re.sub(r'~~~.*?~~~', '', no_fence, flags=re.DOTALL)
    return no_fence

DOC_ID_REFERENCE_PATTERN = re.compile(r'\b(?:GDC|EAD|STD|PAD|SAD|ADR|TDD)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b')

def extract_doc_id_references(content: str) -> list[str]:
    """
    Extract architecture document IDs referenced in prose (e.g. '(**ADR-018**)').
    Code fences and frontmatter are excluded via clean_content_for_length.
    Returns a de-duplicated, order-preserving list.
    """
    prose = clean_content_for_length(content)
    return list(dict.fromkeys(DOC_ID_REFERENCE_PATTERN.findall(prose)))
