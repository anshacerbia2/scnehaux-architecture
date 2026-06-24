"""
Repository-level traceability graph audit.

Per-file validators (sad.py / pad.py / tdd.py) check individual edges. This module
runs once over the FULL registry to catch defects that are only visible globally:
circular upward dependencies (the chain EAD -> PAD -> SAD -> TDD must remain a DAG).

Self-references (e.g. GDC-000 declaring `governed_by: [GDC-000]`, the constitution
governing itself) are intentional and are NOT treated as cycles.
"""

# Edges that point "upward" toward higher-authority documents.
UPWARD_EDGE_FIELDS = ('parent_pad', 'parent_sad', 'governed_by')


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def build_upward_graph(all_doc_metadata):
    """Build an adjacency map of upward references restricted to known, non-self ids."""
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
                cycle = stack[stack.index(nxt):] + [nxt]
                key = tuple(sorted(set(cycle)))
                if key not in reported:
                    reported.add(key)
                    errors.append((
                        'traceability_violation',
                        f"Circular traceability dependency detected: {' -> '.join(cycle)}. "
                        "Upward references (parent_pad/parent_sad/governed_by) must form a DAG."
                    ))
            elif state == WHITE:
                dfs(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for node in list(graph.keys()):
        if color[node] == WHITE:
            dfs(node, [])
    return errors
