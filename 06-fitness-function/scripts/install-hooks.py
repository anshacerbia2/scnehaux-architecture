import os
import stat
import sys


def install_hook():
    """
    Install a Git pre-commit hook that enforces Scnehaux Architecture Governance rules.
    Detects the host OS and injects the appropriate shell script (PowerShell for Windows, Bash for Unix).
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    hooks_dir = os.path.join(repo_root, ".git", "hooks")

    if not os.path.exists(hooks_dir):
        print(
            f"Error: .git/hooks directory not found at {hooks_dir}. Are you in the root of the repository?"
        )
        sys.exit(1)

    hook_path = os.path.join(hooks_dir, "pre-commit")

    is_windows = sys.platform.startswith("win")

    if is_windows:
        hook_content = """#!/usr/bin/env powershell
# Pre-commit hook to enforce Scnehaux Architecture Governance
Write-Host "Running Scnehaux Governance Linter..."

$CHANGED_FILES = git diff --cached --name-only --diff-filter=ACM | Select-String -Pattern '\\.md$' | ForEach-Object { $_.Line }

if (-not $CHANGED_FILES) {
    Write-Host "No markdown files changed. Skipping linter."
    exit 0
}

$TARGETS = $CHANGED_FILES -join ' '

Write-Host "Verifying code and documentation formatting..."
Invoke-Expression "make lint-code"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ [CRITICAL] Code formatting failed (Ruff)!"
    exit 1
}

Invoke-Expression "make lint-docs-format"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ [CRITICAL] Markdown/JSON formatting failed (Prettier)!"
    exit 1
}

Write-Host "Running Unit Tests..."
Invoke-Expression "make test"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ [CRITICAL] Unit tests failed! Please fix the tests before committing."
    exit 1
}

$env:PYTHONPATH="06-fitness-function"
Invoke-Expression "python 06-fitness-function/engine/cli.py --format text --target $TARGETS"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ [CRITICAL] Architecture Linter failed!"
    Write-Host "Commit rejected. Please fix the governance violations before committing."
    exit 1
}

Write-Host "✅ Governance check passed. Proceeding with commit."
exit 0
"""
    else:
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

echo "Verifying code and documentation formatting..."
make lint-code
if [ $? -ne 0 ]; then
  echo "❌ [CRITICAL] Code formatting failed (Ruff)!"
  exit 1
fi

make lint-docs-format
if [ $? -ne 0 ]; then
  echo "❌ [CRITICAL] Markdown/JSON formatting failed (Prettier)!"
  exit 1
fi

echo "Running Unit Tests..."
make test
if [ $? -ne 0 ]; then
  echo "❌ [CRITICAL] Unit tests failed! Please fix the tests before committing."
  exit 1
fi

export PYTHONPATH="06-fitness-function"
python 06-fitness-function/engine/cli.py --format text --target $TARGETS

if [ $? -ne 0 ]; then
  echo ""
  echo "❌ [CRITICAL] Architecture Linter failed!"
  echo "Commit rejected. Please fix the governance violations before committing."
  exit 1
fi

echo "✅ Governance check passed. Proceeding with commit."
exit 0
"""

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)

    # Make the script executable on Unix-like systems
    if not is_windows:
        st = os.stat(hook_path)
        os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    print(
        f"Successfully installed pre-commit hook at {hook_path} (OS: {'Windows' if is_windows else 'Unix'})"
    )


if __name__ == "__main__":
    install_hook()
