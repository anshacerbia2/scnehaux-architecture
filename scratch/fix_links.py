import os
import re

replacements = {
    "ADR-001": "ADR-IAM-001",
    "ADR-SCNX-IAM-GO-SECURITY-003": "ADR-IAM-001",
    "SAD-AUTH-01": "SAD-001",
    "TDD-001": "STD-GLB-FE-008",
    "GDC-005-tech-lifecycle.md": "GDC-004-tech-lifecycle.md",
    "STD-GLB": "STD-GLB-001",
    "ADR-E004": "ADR-IAM-001",
    "EAD-004-technology-architecture.md": "EAD-004-enterprise-integration-architecture.md",
    "ADR-E004-epoch-based-session-management.md": "ADR-IAM-001-epoch-session.md",
    "STD-E003": "STD-GLB-FE-010",
    "TDD-SCNX-UI-JS-002": "STD-UIP-ENG-001",
    "STD-SCNX-UI-JS-002": "STD-UIP-ENG-001",
    "documentation-governance-standard.md": "GDC-000-governance-policy.md",
    "STD-E015": "STD-GLB-005",
    "STD-E004": "STD-GLB-004",
    "STD-E016": "STD-GLB-004",
    "STD-E017": "STD-GLB-006",
    "STD-E018": "STD-GLB-008",
    "STD-E002": "STD-GLB-002"
}

files = []
for root, dirs, f in os.walk("."):
    if ".git" in root or "node_modules" in root:
        continue
    for x in f:
        if x.endswith(".md"):
            files.append(os.path.join(root, x))

for path in files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content
    for old, new in replacements.items():
        if not old.endswith(".md"):
            new_content = re.sub(r'\b' + re.escape(old) + r'\b', new, new_content)
        else:
            new_content = new_content.replace(old, new)
    
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {path}")
