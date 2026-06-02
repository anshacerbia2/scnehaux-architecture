import os
import re

def fix_status():
    adr_dir = os.path.join(os.path.dirname(__file__), '..', '05-decisions')
    fixed_count = 0

    for root, _, files in os.walk(adr_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find the frontmatter block
                match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
                if match:
                    frontmatter = match.group(1)
                    # Use regex to find `status: approved` and replace with `status: accepted`
                    new_frontmatter, num_subs = re.subn(r'status:\s*approved', 'status: accepted', frontmatter)
                    
                    if num_subs > 0:
                        new_content = content[:match.start(1)] + new_frontmatter + content[match.end(1):]
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Fixed status in {file_path}")
                        fixed_count += 1
                        
                # Also replace the markdown table status if it says 'approved'
                # | 2026-05-01 | approved | foundational |
                with open(file_path, 'r', encoding='utf-8') as f:
                    content2 = f.read()
                new_content2, num_subs2 = re.subn(r'\|\s*approved\s*\|', '| accepted |', content2)
                if num_subs2 > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content2)
                    print(f"Fixed table status in {file_path}")

    print(f"Fixed {fixed_count} ADR files.")

if __name__ == "__main__":
    fix_status()
