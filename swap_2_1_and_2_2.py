import re

def swap():
    filepath = '00-governance/GDC-000-governance-policy.md'
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    idx_2_1_start = 0
    idx_2_2_start = 0
    idx_2_3_start = 0
    
    for i, line in enumerate(lines):
        if line.startswith('### 2.1 Logical Abstraction & The Traceability DAG'):
            idx_2_1_start = i
        if line.startswith('### 2.2 The Fractal Boundary'):
            idx_2_2_start = i
        if line.startswith('### 2.3 The Mutability Matrix'):
            idx_2_3_start = i
            break
            
    logical_block = lines[idx_2_1_start:idx_2_2_start]
    fractal_block = lines[idx_2_2_start:idx_2_3_start]
    
    lines = lines[:idx_2_1_start] + fractal_block + logical_block + lines[idx_2_3_start:]
    
    content = ''.join(lines)
    
    # Rename Fractal block headers from 2.2 to 2.1
    content = content.replace('### 2.2 The Fractal Boundary', '### 2.1 The Fractal Boundary')
    content = content.replace('#### 2.2.1 Physical Decentralization', '#### 2.1.1 Physical Decentralization')
    content = content.replace('#### 2.2.2 Logical Decentralization', '#### 2.1.2 Logical Decentralization')
    
    # Rename Logical block headers from 2.1 to 2.2
    content = content.replace('### 2.1 Logical Abstraction & The Traceability DAG', '### 2.2 Logical Abstraction & The Traceability DAG')
    content = content.replace('#### 2.1.1 The 1-to-N Mapping Rule', '#### 2.2.1 The 1-to-N Mapping Rule')
    content = content.replace('#### 2.1.2 The C4 Traceability Chain', '#### 2.2.2 The C4 Traceability Chain')
    content = content.replace('#### 2.1.3 The Orphan Policy & Ecosystem Escape Hatch', '#### 2.2.3 The Orphan Policy & Ecosystem Escape Hatch')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print('Swap successful')

swap()
