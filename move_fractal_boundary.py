import re

def move_and_renumber():
    filepath = '00-governance/GDC-000-governance-policy.md'
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find Section 2.1 End / 2.2 Start
    idx_2_2 = 0
    for i, line in enumerate(lines):
        if line.startswith('### 2.2 The Mutability Matrix'):
            idx_2_2 = i
            break
            
    # Find Section 3.1 Start and End
    idx_3_1_start = 0
    idx_3_2_start = 0
    for i, line in enumerate(lines):
        if line.startswith('### 3.1 The Fractal Boundary'):
            idx_3_1_start = i
        if line.startswith('### 3.2 The Dual-Gate Enforcement Model'):
            idx_3_2_start = i
            break
            
    # Extract 3.1 block
    fractal_block = lines[idx_3_1_start:idx_3_2_start]
    
    # Remove 3.1 block from original location
    del lines[idx_3_1_start:idx_3_2_start]
    
    # Insert 3.1 block before 2.2
    lines = lines[:idx_2_2] + fractal_block + lines[idx_2_2:]
    
    content = ''.join(lines)
    
    # Now we do the renaming
    # 1. Rename the moved Fractal Boundary block
    content = content.replace('### 3.1 The Fractal Boundary', '### 2.2 The Fractal Boundary')
    content = content.replace('#### 3.1.1 Physical Decentralization', '#### 2.2.1 Physical Decentralization')
    content = content.replace('#### 3.1.2 Logical Decentralization', '#### 2.2.2 Logical Decentralization')
    
    # 2. Renumber subsequent 2.x headers
    content = content.replace('### 2.2 The Mutability Matrix', '### 2.3 The Mutability Matrix')
    content = content.replace('### 2.3 Design-Time vs. Consumption-Time Separation', '### 2.4 Design-Time vs. Consumption-Time Separation')
    content = content.replace('### 2.4 Versioning & Change Management', '### 2.5 Versioning & Change Management')
    content = content.replace('### 2.5 Document Lifecycle & State Management', '### 2.6 Document Lifecycle & State Management')
    
    # 3. Renumber subsequent 3.x headers
    content = content.replace('### 3.2 The Dual-Gate Enforcement Model', '### 3.1 The Dual-Gate Enforcement Model')
    content = content.replace('### 3.3 The Glossary of Truth & Execution Gateways', '### 3.2 The Glossary of Truth & Execution Gateways')
    content = content.replace('### 3.4 The Policy Layer (The Artifact-Specific Guidelines)', '### 3.3 The Policy Layer (The Artifact-Specific Guidelines)')
    content = content.replace('### 3.5 The Enforcement Layer (The GDC Pillars)', '### 3.4 The Enforcement Layer (The GDC Pillars)')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print('Move and rename successful')

move_and_renumber()
