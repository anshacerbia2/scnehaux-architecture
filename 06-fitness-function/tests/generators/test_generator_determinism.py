import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_traceability_render_is_independent_of_discovery_order():
    module = load_module(
        "traceability_generator",
        "06-fitness-function/generators/generate_traceability_graph.py",
    )

    docs = {
        "SAD-002": {
            "id": "SAD-002",
            "type": "SAD",
            "parent_pad": "PAD-PLT-002",
            "realizes_capability": None,
        },
        "EAD-002": {
            "id": "EAD-002",
            "type": "EAD",
            "parent_pad": None,
            "realizes_capability": None,
        },
        "PAD-PLT-002": {
            "id": "PAD-PLT-002",
            "type": "PAD",
            "parent_pad": None,
            "realizes_capability": ["EAD-002", "EAD-001"],
        },
        "EAD-001": {
            "id": "EAD-001",
            "type": "EAD",
            "parent_pad": None,
            "realizes_capability": None,
        },
    }

    reversed_docs = dict(reversed(list(docs.items())))
    assert module.render_graph(docs) == module.render_graph(reversed_docs)


def test_topography_render_is_independent_of_path_order():
    module = load_module(
        "topography_generator",
        "06-fitness-function/generators/generate_engine_topography.py",
    )

    paths = [
        ("engine", "reporting", "reporter.py"),
        ("engine", "cli.py"),
        ("scripts", "codeowners-validator.py"),
        ("generators", "generate_traceability_graph.py"),
    ]

    assert module.generate_markdown_from_paths(paths) == module.generate_markdown_from_paths(
        list(reversed(paths))
    )


def test_topography_uses_git_tracked_inputs_not_ambient_workspace():
    module = load_module(
        "topography_generator_tracked",
        "06-fitness-function/generators/generate_engine_topography.py",
    )

    tracked = module.tracked_paths()
    flattened = {"/".join(parts) for parts in tracked}

    assert not any("scratch/" in path for path in flattened)
    assert not any(".egg-info/" in path for path in flattened)
    assert "engine/reporting/reporter.py" in flattened
