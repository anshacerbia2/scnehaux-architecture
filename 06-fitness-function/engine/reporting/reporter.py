import logging

logger = logging.getLogger(__name__)


def print_errors(
    file_path: str,
    errors: list[tuple[str, str]],
    output_format: str = "text",
) -> tuple[list[tuple[str, str]], bool, bool]:
    """
    Format and aggregate errors for a specific file.
    Returns (errors, is_clean, has_blocking).
      - is_clean: True only when there are zero issues (no errors, no warnings).
      - has_blocking: True when CRITICAL or ERROR level findings exist.
    """
    has_blocking = any(sev in ("CRITICAL", "ERROR") for sev, _ in errors)

    # If JSON output is requested, do not print to stdout yet, just return the state.
    if output_format == "json":
        return errors, not has_blocking, has_blocking

    # If there are no errors, mark as PASS
    if not errors:
        logger.info("[PASS] %s", file_path)
        return errors, True, False

    # Print the formatted failure/warning message to stdout
    status_str = "[FAIL]" if has_blocking else "[WARNING]"
    print(f"\n{status_str} {file_path}")
    for sev, msg in errors:
        print(f"  - [{sev}] {msg}")

    return errors, not errors, has_blocking


def build_sarif(results: list[dict]) -> dict:
    """
    Convert aggregated results into a SARIF 2.1.0 document so violations surface as
    inline annotations on GitHub PRs (via code-scanning upload).
    `results` is a list of {"file": path, "errors": [(severity, message), ...]}.
    """
    level_map = {"CRITICAL": "error", "ERROR": "error", "WARNING": "warning"}
    sarif_results = []
    for item in results:
        uri = item["file"].replace("\\", "/")
        if uri.startswith("./"):
            uri = uri[2:]
        for sev, msg in item["errors"]:
            sarif_results.append(
                {
                    "ruleId": f"scnehaux/{sev.lower()}",
                    "level": level_map.get(sev, "warning"),
                    "message": {"text": msg},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": uri},
                                "region": {"startLine": 1},
                            }
                        }
                    ],
                }
            )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Scnehaux Architecture Linter",
                        "informationUri": "https://github.com/scnehaux/scnehaux-architecture",
                        "rules": [],
                    }
                },
                "results": sarif_results,
            }
        ],
    }
