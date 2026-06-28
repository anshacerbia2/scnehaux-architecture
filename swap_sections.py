import re

with open('00-governance/GDC-000-governance-policy.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start indices of the main sections
sec2_start = content.find('## 2. The Policy & Enforcement Ecosystem')
sec3_start = content.find('## 3. The Policy Framework (Existential Maxims)')
sec4_start = content.find('## 4. Exceptions & Waivers')
if sec4_start == -1:
    # try another possible header for section 4
    sec4_start = content.find('## 4.')

if sec2_start != -1 and sec3_start != -1 and sec4_start != -1:
    part1 = content[:sec2_start]
    part2 = content[sec2_start:sec3_start]
    part3 = content[sec3_start:sec4_start]
    part4_and_rest = content[sec4_start:]
    
    # Rename Section 2 -> Section 3 "Enforcement Mechanism (The Ecosystem)"
    part2 = part2.replace('## 2. The Policy & Enforcement Ecosystem', '## 3. Enforcement Mechanism (The Ecosystem)')
    part2 = part2.replace('### 2.1', '### 3.1')
    part2 = part2.replace('### 2.2', '### 3.2')
    part2 = part2.replace('### 2.3', '### 3.3')
    part2 = part2.replace('### 2.4', '### 3.4')
    part2 = part2.replace('### 2.5', '### 3.5')
    
    # Rename Section 3 -> Section 2 "Policy Framework (Existential Maxims)"
    part3 = part3.replace('## 3. The Policy Framework (Existential Maxims)', '## 2. Policy Framework (Existential Maxims)')
    part3 = part3.replace('### 3.1', '### 2.1')
    part3 = part3.replace('### 3.2', '### 2.2')
    
    # Reassemble in the new order: Part 1 -> Part 3 (now 2) -> Part 2 (now 3) -> Part 4
    final_content = part1 + part3 + part2 + part4_and_rest
    
    with open('00-governance/GDC-000-governance-policy.md', 'w', encoding='utf-8', newline='') as f:
        f.write(final_content)
    print("Swapped Section 2 and 3 successfully.")
else:
    print(f"Could not find headers. sec2: {sec2_start}, sec3: {sec3_start}, sec4: {sec4_start}")

