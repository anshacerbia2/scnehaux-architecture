"""
Checks a repository's deploy/dev directory against the skeleton of STD-GLB-009
§Development Server Deployment (1.5.0). The reusable workflow
.github/workflows/deploy-dev-skeleton.yml runs it in every service and application repository.

What it checks, and nothing more:

  Both kinds
    0. Every entry directly under deploy/ is an environment directory: dev, staging or prod. An
       artifact every environment uses, such as alert rules, lives outside deploy/.
    1. deploy/dev/README.md exists.
    2. Its level-2 headings (outside code fences) contain the ten skeleton headings, with exactly
       their text, in their order. Other level-2 headings may sit between them.
    3. Each of the ten has a body: a section that does not apply says so rather than being empty.

  Service kind only
    4. compose.yaml, .env.example and compose.override.example.yaml exist, and migrate.sh exists
       when compose.yaml has a `migrate` service.
    5. compose.yaml's top-level `name:` is the expected project name.
    6. Every host port in every committed compose*.yaml binds to 127.0.0.1 (or ::1), except the
       ports the caller lists as public.
    7. Every network declared with a `name:` is the expected api network, unless it is `external`;
       an external network's name has the form scnehaux-<something>-api.
    8. When a `migrate` service exists, some service without a profile depends on it with
       `condition: service_completed_successfully`.
    9. A service behind `profiles` has no `build:` of its own: it runs an image another service
       builds, so `docker compose up --build` rebuilds it.
   10. A `build:` whose Dockerfile declares `ARG GOPROXY` passes GOPROXY as a build arg
       interpolated from the environment (`${GOPROXY...}`).
   11. Every variable .env.example names, set or commented out, is read somewhere: interpolated
       in a compose file, or named in a deploy/dev script or the repository's scripts/ directory.
   12. When run in a git checkout, deploy/dev/.env and deploy/dev/keys/ are ignored by git.
   13. A project or api network name that differs from the default is stated in README.md.

Exit status 0 when every check passes, 1 when any fails, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

import yaml

HEADINGS = (
    "What runs",
    "Before you start",
    "First start",
    "Updating",
    "One-off tasks",
    "Wiring to other services",
    "Keys",
    "Backups",
    "Never do",
    "Troubleshooting",
)

ENVIRONMENTS = ("dev", "staging", "prod")
LOOPBACK = ("127.0.0.1", "::1", "[::1]")
EXTERNAL_API_NETWORK = re.compile(r"^scnehaux-[a-z0-9-]+-api$")
ENV_NAME = re.compile(r"^\s*#?\s*([A-Z][A-Z0-9_]*)=")
INTERPOLATION = re.compile(r"\$\{([^}:?+-]*)(?::?[-?+]([^}]*))?\}")


class _ComposeLoader(yaml.SafeLoader):
    """A safe YAML loader that accepts compose's `!reset` and `!override` merge tags."""


def _construct_tagged(loader, node):
    """Build a tagged node as its plain value: the tag only changes how compose merges it."""
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node, deep=True)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node, deep=True)
    return loader.construct_scalar(node)


_ComposeLoader.add_constructor("!reset", _construct_tagged)
_ComposeLoader.add_constructor("!override", _construct_tagged)


class Report:
    """Collects failures, printing each as a GitHub annotation when run in Actions."""

    def __init__(self, root: str):
        self.root = root
        self.failures: list[str] = []

    def fail(self, path: str, message: str) -> None:
        """Record one failed check against a file, relative to the repository root."""
        rel = os.path.relpath(path, self.root)
        self.failures.append(f"{rel}: {message}")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::error file={rel}::{message}")
        else:
            print(f"FAIL {rel}: {message}")


def readme_headings(text: str) -> list[tuple[str, bool]]:
    """
    Return the README's level-2 headings outside fenced code blocks, in order, each with whether
    its section has any non-blank line before the next heading of level 1 or 2.
    """
    headings: list[tuple[str, bool]] = []
    fence = None
    for line in text.splitlines():
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if marker:
            if fence is None:
                fence = marker.group(1)[0]
            elif stripped.startswith(fence * 3):
                fence = None
            if headings:
                headings[-1] = (headings[-1][0], True)
            continue
        if fence is None and re.match(r"^#{1,2}\s", line):
            if line.startswith("## "):
                headings.append((line[3:].strip(), False))
            else:
                headings.append(("#", False))
            continue
        if stripped and headings:
            headings[-1] = (headings[-1][0], True)
    return [h for h in headings if h[0] != "#"]


def check_deploy_tree(report: Report, deploy_root: str) -> None:
    """Check 0: deploy/ holds one directory per environment and nothing else."""
    if not os.path.isdir(deploy_root):
        return
    for entry in sorted(os.listdir(deploy_root)):
        path = os.path.join(deploy_root, entry)
        if entry not in ENVIRONMENTS or not os.path.isdir(path):
            report.fail(
                path,
                "deploy/ holds only environment directories (dev, staging, prod); "
                "an artifact every environment uses lives outside deploy/",
            )


def check_readme(report: Report, readme: str) -> None:
    """Checks 1 to 3: the README exists and carries the ten headings, in order, each with a body."""
    if not os.path.isfile(readme):
        report.fail(readme, "missing; every deploy/dev carries a README.md")
        return
    with open(readme, encoding="utf-8") as f:
        found = readme_headings(f.read())
    position = 0
    for wanted in HEADINGS:
        index = next(
            (i for i in range(position, len(found)) if found[i][0] == wanted), None
        )
        if index is None:
            if any(h == wanted for h, _ in found):
                report.fail(readme, f"heading '## {wanted}' is out of order")
            else:
                report.fail(readme, f"heading '## {wanted}' is missing")
            continue
        if not found[index][1]:
            report.fail(
                readme,
                f"section '## {wanted}' is empty; a section that does not apply says so",
            )
        position = index + 1


def load_compose(report: Report, path: str):
    """Parse one compose file, recording a failure when it is not valid YAML."""
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, Loader=_ComposeLoader) or {}
    except yaml.YAMLError as exc:
        report.fail(path, f"not valid YAML: {exc}")
        return {}


def resolve(value: str) -> str:
    """Replace each ${NAME:-default} by its default and every other ${...} by nothing."""
    return INTERPOLATION.sub(lambda m: m.group(2) or "", value)


def host_binding(entry) -> tuple[str | None, str]:
    """Return (host_ip or None, published port) for one entry of a service's `ports`."""
    if isinstance(entry, dict):
        ip = entry.get("host_ip")
        return (
            resolve(str(ip)) if ip else None,
            resolve(str(entry.get("published", ""))),
        )
    spec = resolve(str(entry)).split("/")[0]
    if spec.startswith("["):
        ip, _, rest = spec[1:].partition("]")
        return ("[" + ip + "]", rest.lstrip(":").split(":")[0])
    parts = spec.split(":")
    if len(parts) >= 3:
        return (parts[0], parts[1])
    if len(parts) == 2:
        return (None, parts[0])
    return (None, "")


def check_ports(
    report: Report, path: str, compose: dict, public_ports: set[str]
) -> None:
    """Check 6: every published port binds to loopback unless the caller lists it as public."""
    for name, service in (compose.get("services") or {}).items():
        for entry in (service or {}).get("ports") or []:
            ip, published = host_binding(entry)
            if ip in LOOPBACK:
                continue
            if published and published in public_ports:
                continue
            report.fail(
                path,
                f"service '{name}' publishes '{entry}' on every interface; bind it to 127.0.0.1",
            )


def check_networks(report: Report, path: str, compose: dict, api_network: str) -> None:
    """Check 7: a named network is the stack's api network, or an external scnehaux-*-api."""
    for key, network in (compose.get("networks") or {}).items():
        network = network or {}
        name = network.get("name")
        if not name:
            continue
        if network.get("external"):
            if not EXTERNAL_API_NETWORK.match(str(name)):
                report.fail(
                    path,
                    f"external network '{key}' is named '{name}'; another stack's network is scnehaux-<repository>-api",
                )
        elif name != api_network:
            report.fail(
                path,
                f"network '{key}' is named '{name}'; the network other stacks join is '{api_network}'",
            )


def check_services(
    report: Report, path: str, compose: dict, repo_root: str, deploy: str
) -> None:
    """Checks 8 to 10: the migrate gate, profiled tasks without builds, and GOPROXY build args."""
    services = compose.get("services") or {}
    if "migrate" in services and os.path.basename(path) == "compose.yaml":
        gated = False
        for name, service in services.items():
            service = service or {}
            if name == "migrate" or service.get("profiles"):
                continue
            depends = service.get("depends_on") or {}
            if isinstance(depends, dict):
                condition = (depends.get("migrate") or {}).get("condition")
                gated = gated or condition == "service_completed_successfully"
        if not gated:
            report.fail(
                path,
                "no service waits for migrate with condition: service_completed_successfully",
            )
    for name, service in services.items():
        service = service or {}
        build = service.get("build")
        if service.get("profiles") and build:
            report.fail(
                path,
                f"one-off task '{name}' has a build of its own; run the migrate service's image by name",
            )
        if not build:
            continue
        if isinstance(build, str):
            build = {"context": build}
        context = os.path.normpath(os.path.join(deploy, str(build.get("context", "."))))
        dockerfile = os.path.join(context, str(build.get("dockerfile", "Dockerfile")))
        if not dockerfile.startswith(os.path.normpath(repo_root)) or not os.path.isfile(
            dockerfile
        ):
            continue
        with open(dockerfile, encoding="utf-8") as f:
            declares = re.search(r"^\s*ARG\s+GOPROXY\b", f.read(), re.MULTILINE)
        if not declares:
            continue
        args = build.get("args") or {}
        if isinstance(args, list):
            args = dict(a.split("=", 1) if "=" in a else (a, "") for a in args)
        if "${GOPROXY" not in str(args.get("GOPROXY", "")):
            report.fail(
                path,
                f"service '{name}' builds a Dockerfile that declares ARG GOPROXY; pass "
                "GOPROXY: ${GOPROXY:-https://proxy.golang.org,direct} in build.args",
            )


def check_env_example(
    report: Report, deploy: str, repo_root: str, compose_texts: list[str]
) -> None:
    """Check 11: every variable .env.example names is read by compose or by a script."""
    path = os.path.join(deploy, ".env.example")
    if not os.path.isfile(path):
        return
    readers = list(compose_texts)
    for directory in (deploy, os.path.join(repo_root, "scripts")):
        if not os.path.isdir(directory):
            continue
        for entry in sorted(os.listdir(directory)):
            if entry.endswith((".sh", ".ps1", ".py", ".mjs")):
                with open(
                    os.path.join(directory, entry), encoding="utf-8", errors="replace"
                ) as f:
                    readers.append(f.read())
    compose_names = {
        "COMPOSE_FILE",
        "COMPOSE_PROJECT_NAME",
        "COMPOSE_PROFILES",
        "COMPOSE_PATH_SEPARATOR",
    }
    with open(path, encoding="utf-8") as f:
        for line in f:
            match = ENV_NAME.match(line)
            if not match:
                continue
            name = match.group(1)
            if name in compose_names:
                continue
            if not any(re.search(rf"\b{name}\b", text) for text in readers):
                report.fail(
                    path,
                    f"{name} is read by no compose file and no script; compose passes a container only the variables it lists",
                )


def check_ignored(report: Report, repo_root: str, deploy_dir: str) -> None:
    """Check 12: in a git checkout, .env and keys/ under deploy/dev are ignored."""
    try:
        inside = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return
    if inside.returncode != 0:
        return
    for rel in (f"{deploy_dir}/.env", f"{deploy_dir}/keys/client.pem"):
        result = subprocess.run(
            ["git", "-C", repo_root, "check-ignore", "-q", "--no-index", rel],
            check=False,
        )
        if result.returncode != 0:
            report.fail(
                os.path.join(repo_root, rel),
                "is not ignored by git; .env and keys/ never reach a commit",
            )


def main(argv=None) -> int:
    """Parse the arguments, run every check for the kind, and print a summary."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--kind", required=True, choices=("service", "application"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--deploy-dir", default="deploy/dev")
    parser.add_argument("--project-name", default="")
    parser.add_argument("--api-network", default="")
    parser.add_argument("--public-ports", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    deploy = os.path.join(repo_root, args.deploy_dir)
    report = Report(repo_root)
    readme = os.path.join(deploy, "README.md")

    check_deploy_tree(report, os.path.dirname(os.path.normpath(deploy)))
    if not os.path.isdir(deploy):
        report.fail(
            deploy, "missing; every service and application repository has deploy/dev"
        )
        print(f"{len(report.failures)} check(s) failed.")
        return 1

    check_readme(report, readme)

    if args.kind == "service":
        project = args.project_name or f"scnehaux-{args.repo_name}-dev"
        api_network = args.api_network or f"scnehaux-{args.repo_name}-api"
        public_ports = set(args.public_ports.split())

        for required in (
            "compose.yaml",
            ".env.example",
            "compose.override.example.yaml",
        ):
            if not os.path.isfile(os.path.join(deploy, required)):
                report.fail(
                    os.path.join(deploy, required),
                    "missing; a server-deployed service carries it",
                )

        compose_texts: list[str] = []
        for entry in sorted(os.listdir(deploy)):
            if not re.match(r"^compose(\.[A-Za-z0-9_-]+)*\.ya?ml$", entry):
                continue
            path = os.path.join(deploy, entry)
            with open(path, encoding="utf-8") as f:
                compose_texts.append(f.read())
            compose = load_compose(report, path)
            if entry == "compose.yaml":
                if compose.get("name") != project:
                    report.fail(
                        path,
                        f"project name is '{compose.get('name')}'; expected '{project}'",
                    )
                if "migrate" in (compose.get("services") or {}) and not os.path.isfile(
                    os.path.join(deploy, "migrate.sh")
                ):
                    report.fail(
                        os.path.join(deploy, "migrate.sh"),
                        "missing; compose.yaml has a migrate service",
                    )
            check_ports(report, path, compose, public_ports)
            check_networks(report, path, compose, api_network)
            check_services(report, path, compose, repo_root, deploy)

        check_env_example(report, deploy, repo_root, compose_texts)
        check_ignored(report, repo_root, args.deploy_dir)

        if os.path.isfile(readme):
            with open(readme, encoding="utf-8") as f:
                text = f.read()
            for override in (args.project_name, args.api_network):
                if override and override not in text:
                    report.fail(
                        readme,
                        f"'{override}' differs from the standard's name and README.md does not state it",
                    )

    if report.failures:
        print(
            f"{len(report.failures)} check(s) failed (STD-GLB-009 §Development Server Deployment)."
        )
        return 1
    print(f"deploy/dev follows the {args.kind} skeleton.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
