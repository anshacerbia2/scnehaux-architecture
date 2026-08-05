import json

content = """
# Test

This is a test paragraph. <!-- lint_disable: some_rule -->
"""

from markdown_it import MarkdownIt

md = MarkdownIt()
tokens = md.parse(content)

for t in tokens:
    print(f"type={t.type}, tag={t.tag}, map={t.map}, content={repr(t.content)}")
    if t.children:
        for c in t.children:
            print(f"  CHILD: type={c.type}, content={repr(c.content)}")


