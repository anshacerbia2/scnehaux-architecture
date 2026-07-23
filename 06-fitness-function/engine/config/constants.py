"""
Global configuration constants for the Scnehaux Architecture Linter.
"""

# Global denylist of directories to ignore during filesystem traversal.
# This prevents the linter from crawling through caches and dependencies,
# dramatically improving performance and eliminating false positives.
EXCLUDED_DIRS = (
    ".git",
    "__pycache__",
    "node_modules",
    ".vscode",
    "validators",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    "scnehaux_linter.egg-info",
    "scratch",
)
