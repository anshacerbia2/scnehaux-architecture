import os
import stat
import sys

def install_hook():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    hooks_dir = os.path.join(repo_root, '.git', 'hooks')
    
    if not os.path.exists(hooks_dir):
        print(f"Error: .git/hooks directory not found at {hooks_dir}. Are you in the root of the repository?")
        sys.exit(1)
        
    hook_path = os.path.join(hooks_dir, 'pre-commit')
    
    hook_content = """#!/bin/bash
# Pre-commit hook to enforce Scnehaux Architecture Governance
echo "Running Scnehaux Governance Linter..."

# Extract only changed markdown files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.md$')

if [ -z "$CHANGED_FILES" ]; then
    echo "No markdown files changed. Skipping linter."
    exit 0
fi

# Convert newlines to spaces for the target argument
TARGETS=$(echo "$CHANGED_FILES" | tr '\\n' ' ')

python linter.py --format text --target $TARGETS

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ [CRITICAL] Architecture Linter failed!"
  echo "Commit rejected. Please fix the governance violations before committing."
  exit 1
fi

echo "✅ Governance check passed. Proceeding with commit."
exit 0
"""
    
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)
        
    # Make the script executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)
    
    print(f"Successfully installed pre-commit hook at {hook_path}")

if __name__ == "__main__":
    install_hook()
