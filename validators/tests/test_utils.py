from datetime import date
import datetime

from validators.utils import (
    parse_date, extract_links, extract_section_contents,
    clean_content_for_length, normalize_section, get_section_order,
    parse_frontmatter,
)

def test_parse_date():
    assert parse_date("2026-06-21") == date(2026, 6, 21)
    assert parse_date(date(2026, 6, 21)) == date(2026, 6, 21)
    assert parse_date("invalid-date") is None

def test_extract_links():
    content = "Check out [Google](https://google.com) and [this document](./ADR-001.md)."
    links = extract_links(content)
    assert len(links) == 2
    assert "https://google.com" in links
    assert "./ADR-001.md" in links

def test_extract_section_contents():
    content = "---\nmeta\n---\n## Introduction\nHello\n## Background\nWorld"
    sections = extract_section_contents(content)
    assert 'introduction' in sections
    assert sections['introduction'] == 'Hello'
    assert 'background' in sections
    assert sections['background'] == 'World'

def test_clean_content_for_length():
    content = "Hello `code` world\n```\nignore this\n```"
    cleaned = clean_content_for_length(content)
    assert "ignore this" not in cleaned
    assert "Hello  code  world" in cleaned

def test_normalize_section():
    assert normalize_section("1.2.3 Introduction ") == "introduction"
    assert normalize_section("Background") == "background"

def test_get_section_order():
    content = "## Introduction\n## Background"
    order = get_section_order(content)
    assert order == ["introduction", "background"]

def test_parse_frontmatter():
    content = "---\ndoc_meta:\n  id: ADR-001\n---\nBody"
    meta, err = parse_frontmatter(content)
    assert err is None
    assert meta["id"] == "ADR-001"

def test_parse_frontmatter_missing():
    meta, err = parse_frontmatter("No frontmatter here")
    assert err == "Missing YAML frontmatter."

def test_parse_frontmatter_invalid_yaml():
    meta, err = parse_frontmatter("---\ninvalid: yaml: : ---\n")
    assert "Failed to parse YAML frontmatter" in err

def test_parse_frontmatter_no_doc_meta():
    meta, err = parse_frontmatter("---\nother: true\n---\n")
    assert "YAML frontmatter is missing 'doc_meta' block" in err

def test_parse_date_datetime():
    dt = datetime.datetime(2026, 6, 21, 12, 0)
    assert parse_date(dt) == datetime.date(2026, 6, 21)

def test_extract_links_nested():
    content = "Check [*Google*](https://google.com)"
    links = extract_links(content)
    assert "https://google.com" in links

def test_clean_content_for_length_html_block():
    content = "Hello\n\n<div>ignore</div>\n\nworld"
    cleaned = clean_content_for_length(content)
    assert "ignore" not in cleaned
    assert "Hello world" in cleaned
