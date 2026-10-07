"""Tests for 06-fitness-function/scripts/deploy-dev-skeleton-check.py (STD-GLB-009 1.5.0)."""

import importlib.util
import os

import pytest

SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "..", "scripts", "deploy-dev-skeleton-check.py"
)
spec = importlib.util.spec_from_file_location("deploy_dev_skeleton_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


@pytest.fixture(autouse=True)
def plain_output(monkeypatch):
    """Print failures as plain lines, as outside Actions, even when the tests run in CI."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)


README = "# Development server\n\n" + "".join(
    f"## {heading}\n\nDoes not apply.\n\n" for heading in check.HEADINGS
)

COMPOSE = """name: scnehaux-demo-dev
services:
  postgres:
    image: postgres
  migrate:
    build:
      context: ../..
      target: migrate
      args:
        GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}
    image: scnehaux-demo-dev-migrate
  task:
    image: scnehaux-demo-dev-migrate
    profiles: ["task"]
  demo:
    build:
      context: ../..
      target: service
      args:
        GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}
    environment:
      DEMO_PASSWORD: ${DEMO_PASSWORD:?set it}
    depends_on:
      migrate:
        condition: service_completed_successfully
    ports:
      - "127.0.0.1:${DEMO_PORT:-8084}:8080"
networks:
  api:
    name: scnehaux-demo-api
  kernel:
    external: true
    name: scnehaux-identity-api
"""


def make_repo(
    tmp_path, compose=COMPOSE, readme=README, env="DEMO_PASSWORD=\nDEMO_PORT=8084\n"
):
    """Write a conforming service repository under tmp_path, with the given files."""
    deploy = tmp_path / "deploy" / "dev"
    deploy.mkdir(parents=True)
    (tmp_path / "Dockerfile").write_text(
        "FROM golang AS build\nARG GOPROXY=https://proxy.golang.org,direct\n"
    )
    (deploy / "README.md").write_text(readme)
    (deploy / "compose.yaml").write_text(compose)
    (deploy / ".env.example").write_text(env)
    (deploy / "compose.override.example.yaml").write_text(
        'services:\n  postgres:\n    ports: !override\n      - "127.0.0.1:5434:5432"\n'
    )
    (deploy / "migrate.sh").write_text("#!/bin/sh\n")
    return tmp_path


def run(repo, kind="service", *extra):
    """Run the check on a repository as the reusable workflow does, returning its exit status."""
    return check.main(
        ["--kind", kind, "--repo-root", str(repo), "--repo-name", "demo", *extra]
    )


def test_a_conforming_service_passes(tmp_path, capsys):
    """A service whose deploy/dev follows every rule passes."""
    assert run(make_repo(tmp_path)) == 0
    assert "follows the service skeleton" in capsys.readouterr().out


def test_an_application_needs_only_the_readme(tmp_path):
    """An application needs only README.md with the ten headings."""
    deploy = tmp_path / "deploy" / "dev"
    deploy.mkdir(parents=True)
    (deploy / "README.md").write_text(README)
    assert run(tmp_path, "application") == 0


def test_missing_deploy_dir_fails(tmp_path):
    """A repository without deploy/dev fails."""
    assert run(tmp_path, "application") == 1


def test_missing_out_of_order_and_empty_headings_fail(tmp_path, capsys):
    """Missing and empty headings fail; a heading inside a code fence does not count."""
    readme = README.replace("## Backups\n\nDoes not apply.\n\n", "")
    readme = readme.replace("## Keys\n\nDoes not apply.\n\n", "## Keys\n\n")
    readme = readme.replace(
        "## Updating\n\n", "## Troubleshooting\n\nx\n\n## Updating\n\n", 1
    )
    readme += "```sh\n## Backups\n```\n"
    assert run(make_repo(tmp_path, readme=readme)) == 1
    out = capsys.readouterr().out
    assert "'## Backups' is missing" in out
    assert "'## Keys' is empty" in out


def test_a_heading_only_out_of_order_is_reported_so(tmp_path, capsys):
    """A heading present in the wrong place is reported as out of order."""
    readme = README.replace("## Keys\n\nDoes not apply.\n\n", "")
    readme = readme.replace("## Updating\n\n", "## Keys\n\nx\n\n## Updating\n\n", 1)
    assert run(make_repo(tmp_path, readme=readme)) == 1
    assert "'## Keys' is out of order" in capsys.readouterr().out


def test_compose_rules_fail(tmp_path, capsys):
    """Each compose rule fails on its own violation."""
    compose = (
        COMPOSE.replace("scnehaux-demo-dev\n", "demo\n", 1)
        .replace('"127.0.0.1:${DEMO_PORT:-8084}:8080"', '"8084:8080"')
        .replace("name: scnehaux-demo-api", "name: demo-api")
        .replace("name: scnehaux-identity-api", "name: kernel-net")
        .replace(
            "condition: service_completed_successfully", "condition: service_started"
        )
        .replace(
            '    image: scnehaux-demo-dev-migrate\n    profiles: ["task"]',
            '    build: ../..\n    profiles: ["task"]',
        )
        .replace(
            "      args:\n        GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct}\n    environment",
            "    environment",
        )
    )
    repo = make_repo(
        tmp_path, compose=compose, env="DEMO_PASSWORD=\n# UNREAD_SETTING=x\n"
    )
    (repo / "deploy" / "dev" / "migrate.sh").unlink()
    assert run(repo) == 1
    out = capsys.readouterr().out
    for expected in (
        "project name is 'demo'",
        "publishes '8084:8080' on every interface",
        "named 'demo-api'",
        "named 'kernel-net'",
        "no service waits for migrate",
        "one-off task 'task' has a build",
        "service 'demo' builds a Dockerfile that declares ARG GOPROXY",
        "UNREAD_SETTING is read by no compose file",
        "migrate.sh: missing",
    ):
        assert expected in out


def test_overrides_must_be_stated_and_public_ports_allowed(tmp_path, capsys):
    """A name override must be stated in the README; listed public ports pass."""
    compose = COMPOSE.replace(
        '"127.0.0.1:${DEMO_PORT:-8084}:8080"',
        '"443:443/udp"\n      - target: 80\n        published: "80"',
    )
    repo = make_repo(
        tmp_path,
        compose=compose.replace("scnehaux-demo-dev", "scnehaux-legacy-dev"),
        env="DEMO_PASSWORD=\n",
    )
    assert (
        run(
            repo,
            "service",
            "--project-name",
            "scnehaux-legacy-dev",
            "--public-ports",
            "80 443",
        )
        == 1
    )
    assert "'scnehaux-legacy-dev' differs" in capsys.readouterr().out
    readme = README + "The project keeps its first name, scnehaux-legacy-dev.\n"
    (repo / "deploy" / "dev" / "README.md").write_text(readme)
    assert (
        run(
            repo,
            "service",
            "--project-name",
            "scnehaux-legacy-dev",
            "--public-ports",
            "80 443",
        )
        == 0
    )


def test_missing_service_files_and_bad_yaml_fail(tmp_path, capsys):
    """A missing required file and an unparsable compose file fail."""
    repo = make_repo(tmp_path)
    (repo / "deploy" / "dev" / "compose.override.example.yaml").unlink()
    (repo / "deploy" / "dev" / "compose.ci.yaml").write_text("services: [\n")
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "compose.override.example.yaml: missing" in out
    assert "not valid YAML" in out


def test_host_binding_forms():
    """Short, bracketed IPv6, bare and long port syntaxes are read."""
    assert check.host_binding("127.0.0.1:8080:80") == ("127.0.0.1", "8080")
    assert check.host_binding("[::1]:8080:80") == ("[::1]", "8080")
    assert check.host_binding("8080") == (None, "")
    assert check.host_binding({"host_ip": "127.0.0.1", "published": 5433}) == (
        "127.0.0.1",
        "5433",
    )


def test_annotations_in_actions(tmp_path, capsys, monkeypatch):
    """In GitHub Actions a failure is printed as an error annotation."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    deploy = tmp_path / "deploy" / "dev"
    deploy.mkdir(parents=True)
    assert run(tmp_path, "application") == 1
    assert "::error file=deploy/dev/README.md::" in capsys.readouterr().out


def test_deploy_holds_only_environment_directories(tmp_path, capsys):
    """Any entry under deploy/ other than dev, staging or prod fails."""
    repo = make_repo(tmp_path)
    (repo / "deploy" / "alerts").mkdir()
    (repo / "deploy" / "notes.md").write_text("x")
    (repo / "deploy" / "staging").mkdir()
    assert run(repo) == 1
    out = capsys.readouterr().out
    assert "deploy/alerts: deploy/ holds only environment directories" in out
    assert "deploy/notes.md: deploy/ holds only environment directories" in out
    assert "deploy/staging:" not in out
