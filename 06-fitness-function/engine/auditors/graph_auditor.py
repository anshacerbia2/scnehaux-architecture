"""
Repository-level traceability graph audit.

Per-file validators (sad.py / pad.py / tdd.py) check individual edges. This module
runs once over the FULL registry to catch defects that are only visible globally:
circular upward dependencies (the chain EAD -> PAD -> SAD -> TDD must remain a DAG).

Self-references (e.g. GDC-000 declaring `governed_by: [GDC-000]`, the constitution
governing itself) are intentional and are NOT treated as cycles.
"""

from engine.config.severity import SeverityRule

# Hardcoded list of metadata fields that represent an upward dependency in the DAG
UPWARD_EDGE_FIELDS = ("realizes_capability", "parent_pad", "parent_sad", "governed_by")


def _as_list(value):
    """
    Coerce a scalar value or None into a list format.
    Used for normalizing metadata fields that can be either strings or lists.
    """
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def build_upward_graph(all_doc_metadata):
    """
    Build an adjacency map of upward references restricted to known, non-self ids.

    This function parses specific metadata fields (`UPWARD_EDGE_FIELDS`) across all
    registered documents to map their upward topological dependencies. Self-references
    are explicitly filtered out to avoid false-positive cycles.

    Returns:
        dict: A mapping from document ID to a set of its upstream parent IDs.
    """
    known = set(all_doc_metadata.keys())
    graph = {}
    for doc_id, meta in all_doc_metadata.items():
        if not isinstance(meta, dict):
            graph[doc_id] = set()
            continue
        targets = set()
        for field in UPWARD_EDGE_FIELDS:
            for ref in _as_list(meta.get(field)):
                if ref in known and ref != doc_id:
                    targets.add(ref)
        graph[doc_id] = targets
    return graph


def audit_traceability_graph(all_doc_metadata):
    """
    Return a list of (category, message) tuples for global traceability defects.

    Currently detects circular dependencies (length >= 2) in the upward-reference
    graph and emits them as 'traceability_violation' (a blocking ERROR).
    """
    errors = []
    graph = build_upward_graph(all_doc_metadata)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    reported = set()

    def dfs(node, stack):
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, ()):
            state = color.get(nxt, BLACK)
            if state == GRAY and nxt in stack:
                cycle = stack[stack.index(nxt) :] + [nxt]
                key = tuple(sorted(set(cycle)))
                if key not in reported:
                    reported.add(key)
                    errors.append(
                        (
                            "traceability_violation",
                            f"Circular traceability dependency detected: {' -> '.join(cycle)}. "
                            "Upward references (parent_pad/parent_sad/governed_by) must form a DAG.",
                        )
                    )
            elif state == WHITE:
                dfs(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for node in list(graph.keys()):
        if color[node] == WHITE:
            dfs(node, [])
    return errors


def audit_duplicate_ids(
    duplicate_ids: dict, severity_levels: dict
) -> list[tuple[str, str, str]]:
    """
    Evaluate duplicate document IDs across the repository to enforce the SSOT (Single Source of Truth) invariant.

    This auditor iterates over the duplicate map generated during the pre-scan phase. For every duplicated
    ID, it generates an error tuple pointing to the conflicting file paths.

    Returns:
        list[tuple[str, str, str]]: A list of (severity, message, filepath) tuples.
    """
    findings = []
    for dup_id, paths in sorted(duplicate_ids.items()):
        sev = severity_levels[SeverityRule.DUPLICATE_ID]
        findings.append(
            (
                sev,
                f"Duplicate document ID '{dup_id}' declared in multiple files: {', '.join(paths)}. "
                "Document IDs must be globally unique (SSOT).",
                paths[-1],
            )
        )
    return findings


def audit_hierarchy_tiers(
    all_doc_metadata: dict, severity_levels: dict
) -> list[tuple[str, str, str]]:
    """
    Enforce C4 Tier Mapping (GDC-000 Section 2.3.1).
    TDD -> SAD -> PAD -> EAD.
    ADR & STD -> EAD or PAD.
    """
    findings = []
    sev = severity_levels[SeverityRule.STRUCTURAL_INTEGRITY_VIOLATION]

    for doc_id, meta in all_doc_metadata.items():
        if not isinstance(meta, dict):
            continue

        filepath = meta.get("_filepath", "Unknown")

        # Check TDD
        if doc_id.startswith("TDD-"):
            for parent in _as_list(meta.get("parent_sad")):
                if not isinstance(parent, str) or not parent.startswith("SAD-"):
                    findings.append(
                        (
                            sev,
                            f"Hierarchy violation: TDD '{doc_id}' must attach to a SAD, but parent_sad contains '{parent}'.",
                            filepath,
                        )
                    )

        # Check SAD
        elif doc_id.startswith("SAD-"):
            parent = meta.get("parent_pad")
            if parent and not parent.startswith("PAD-"):
                findings.append(
                    (
                        sev,
                        f"Hierarchy violation: SAD '{doc_id}' must attach to a PAD, but parent_pad is '{parent}'.",
                        filepath,
                    )
                )

        # Check PAD
        elif doc_id.startswith("PAD-"):
            # Some PADs might attach to EAD via governed_by or parent_ead, let's check governed_by
            parents = _as_list(meta.get("governed_by"))
            has_ead = any(p.startswith("EAD-") for p in parents)
            if (
                parents
                and not has_ead
                and not any(p.startswith("GDC-") for p in parents)
            ):
                findings.append(
                    (
                        sev,
                        f"Hierarchy violation: PAD '{doc_id}' must attach to an EAD via governed_by.",
                        filepath,
                    )
                )

        # Check ADR / STD
        elif doc_id.startswith("ADR-") or doc_id.startswith("STD-"):
            parents = _as_list(meta.get("governed_by")) + _as_list(
                meta.get("parent_pad")
            )
            for p in parents:
                if not (
                    p.startswith("EAD-") or p.startswith("PAD-") or p.startswith("GDC-")
                ):
                    findings.append(
                        (
                            sev,
                            f"Hierarchy violation: {doc_id[:3]} '{doc_id}' cannot attach to '{p}'. Must be EAD or PAD.",
                            filepath,
                        )
                    )

    return findings


def audit_orphans(
    all_doc_metadata: dict, severity_levels: dict
) -> list[tuple[str, str, str]]:
    """
    Enforce architectural connectivity by ensuring no orphaned artifacts exist below the EAD tier.

    This check validates that nodes with an in-degree of 0 (no incoming upward edges) are exclusively
    top-level constructs (EADs or GDCs). Any lower-tier document (TDD, SAD, PAD) missing its requisite
    parent reference (e.g. `parent_pad`, `governed_by`) is flagged as a traceability violation.

    Returns:
        list[tuple[str, str, str]]: A list of (severity, message, filepath) tuples for orphaned nodes.
    """
    findings = []
    sev = severity_levels[SeverityRule.TRACEABILITY_VIOLATION]

    for doc_id, meta in all_doc_metadata.items():
        if not isinstance(meta, dict):
            continue

        filepath = meta.get("_filepath", "Unknown")

        if doc_id.startswith("TDD-") and not meta.get("parent_sad"):
            findings.append(
                (
                    sev,
                    f"Orphan artifact: TDD '{doc_id}' must declare a 'parent_sad'.",
                    filepath,
                )
            )

        elif doc_id.startswith("SAD-") and not meta.get("parent_pad"):
            findings.append(
                (
                    sev,
                    f"Orphan artifact: SAD '{doc_id}' must declare a 'parent_pad'.",
                    filepath,
                )
            )

        elif doc_id.startswith("PAD-") and not meta.get("governed_by"):
            findings.append(
                (
                    sev,
                    f"Orphan artifact: PAD '{doc_id}' must declare 'governed_by' (pointing to an EAD).",
                    filepath,
                )
            )

    return findings
