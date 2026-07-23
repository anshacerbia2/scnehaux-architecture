import os, re

root_dir = r'd:\Ansha\architecture-description\scnehaux-architecture'

for r, d, f in os.walk(root_dir):
    if '.git' in d: d.remove('.git')
    for file in f:
        if file.endswith('.md'):
            path = os.path.join(r, file)
            with open(path, 'r', encoding='utf-8') as f_in:
                content = f_in.read()
            
            # The python string literal
            new_content = content.replace(r"....\\", r"..\..\ ")
            new_content = new_content.replace(r"..../", r"../../")
            
            # fix the typo I introduced in my previous script where `_global` merged with `standards`
            new_content = new_content.replace(r"02-standards_global", r"02-standards\_global")
            new_content = new_content.replace(r"..\..\ ", r"..\..\ ") # remove the space I added
            
            # The linter wants a subsection #### Blast Radius.
            if file.endswith('.sad.md') and '#### Blast Radius' not in new_content and '### Resilience & Failure Modes' in new_content:
                new_content = new_content.replace('### Resilience & Failure Modes', '### Resilience & Failure Modes\n\n#### Blast Radius\n\nSee below for component-specific blast radius analysis.\n')
            
            # Convert all backslashes in markdown links to forward slashes! 
            # Because backslashes in markdown links are technically illegal anyway.
            def fix_link_slashes(match):
                link_text = match.group(1)
                link_url = match.group(2)
                # replace backslash with forward slash in the URL part
                fixed_url = link_url.replace('\\', '/')
                # replace `..../` with `../../` in case it's there
                fixed_url = fixed_url.replace('..../', '../../')
                fixed_url = fixed_url.replace('02-standards_global', '02-standards/_global')
                return f"[{link_text}]({fixed_url})"
                
            new_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', fix_link_slashes, new_content)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as f_out:
                    f_out.write(new_content)
                print(f'Fixed {path}')
