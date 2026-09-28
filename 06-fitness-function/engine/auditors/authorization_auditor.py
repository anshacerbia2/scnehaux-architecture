"""
Audits the authorization edge between Standards and Decision Records.

GDC-007 section 2.4.2 requires every major revision of a Standard to be authorized
by a Decision Record. GDC-000 section 2.4.1 keeps that edge out of the attachment
hierarchy: `governed_by` attaches a Standard to an EAD, a PAD, or GDC-000, while
`authorized_by` names the ADR that authorized its current major version. The ADR
declares the same edge from its side in `authorizes`.

The audit evaluates the final state of the registry, not the order in which files
changed. A Standard and its authorizing ADR may therefore be promoted in the same
ratification commit.
"""

from datetime import date, datetime

from engine.config.severity import SeverityRule

# A Standard in these statuses has no normative authority yet.
PRE_AUTHORITY_STD_STATUSES = frozenset({"draft", "proposed"})

# A retired Standard no longer needs a live authorization.
RETIRED_STD_STATUSES = frozenset({"deprecated"})

# An ADR in these statuses may authorize a Standard that is still under review.
REVIEWABLE_ADR_STATUSES = frozenset({"proposed", "accepted"})

# Severity of a legacy entry that is still inside its allowance window.
LEGACY_ALLOWANCE_SEVERITY = "WARNING"


def _as_list(value):
    """
    Coerce a scalar value or None into a list format.
    Used for normalizing metadata fields that can be either strings or lists.
    """
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _major_version(raw_version):
    """
    Return the major component of a Semantic Version, or None when it cannot be read.
    """
    try:
        return int(str(raw_version).split(".", 1)[0])
    except (TypeError, ValueError):
        return None


def _parse_date(raw_date):
    """
    Parse an ISO date (YYYY-MM-DD), returning None when it is absent or malformed.
    """
    if isinstance(raw_date, date):
        return raw_date
    try:
        return datetime.strptime(str(raw_date), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _audit_authorizing_adrs(doc_id, meta, registry, sev):
    """
    Check that every `authorized_by` entry of one Standard resolves to an ADR that
    declares the Standard back and whose status matches the Standard's status.
    """
    findings = []
    filepath = meta.get("_filepath", doc_id)
    status = str(meta.get("status", "")).lower()

    for ref in _as_list(meta.get("authorized_by")):
        adr = registry.get(ref) if isinstance(ref, str) else None
        if (
            not isinstance(ref, str)
            or not ref.startswith("ADR-")
            or not isinstance(adr, dict)
        ):
            findings.append(
                (
                    sev,
                    f"STD '{doc_id}' names '{ref}' in 'authorized_by', but it is not an ADR in this repository.",
                    filepath,
                )
            )
            continue

        if doc_id not in _as_list(adr.get("authorizes")):
            findings.append(
                (
                    sev,
                    f"ADR '{ref}' does not list STD '{doc_id}' in 'authorizes'. "
                    "An authorization must be declared by both the Standard and the ADR.",
                    filepath,
                )
            )

        if status in RETIRED_STD_STATUSES:
            continue

        adr_status = str(adr.get("status", "")).lower() or "unknown"
        if status in PRE_AUTHORITY_STD_STATUSES:
            if adr_status not in REVIEWABLE_ADR_STATUSES:
                findings.append(
                    (
                        sev,
                        f"STD '{doc_id}' is '{status}' but its authorizing ADR '{ref}' is '{adr_status}'. "
                        "A Standard under review must be authorized by a 'proposed' or 'accepted' ADR.",
                        filepath,
                    )
                )
        elif adr_status != "accepted":
            findings.append(
                (
                    sev,
                    f"STD '{doc_id}' is '{status}' but its authorizing ADR '{ref}' is '{adr_status}'. "
                    "A Standard holds authority only when every authorizing ADR is 'accepted' in the same commit.",
                    filepath,
                )
            )

    return findings


def _audit_missing_authorization(doc_id, meta, legacy, today, sev):
    """
    Require `authorized_by` on a Standard whose major version is 2 or higher,
    honoring a dated legacy allowance recorded in the base schema.
    """
    status = str(meta.get("status", "")).lower()
    major = _major_version(meta.get("version"))
    if (
        major is None
        or major < 2
        or _as_list(meta.get("authorized_by"))
        or status in RETIRED_STD_STATUSES
    ):
        return []

    filepath = meta.get("_filepath", doc_id)
    entry = legacy.get(doc_id)
    if entry is None:
        return [
            (
                sev,
                f"STD '{doc_id}' is at major version {major} but declares no 'authorized_by'. "
                "GDC-007 section 2.4.2 requires an authorizing ADR for every major revision.",
                filepath,
            )
        ]

    expires = _parse_date(entry.get("expires"))
    if expires is None:
        return [
            (
                sev,
                f"Legacy authorization allowance for STD '{doc_id}' has no valid 'expires' date (YYYY-MM-DD).",
                filepath,
            )
        ]
    if today > expires:
        return [
            (
                sev,
                f"STD '{doc_id}' is at major version {major} without 'authorized_by', and its legacy "
                f"allowance expired on {expires.isoformat()}. Record the authorizing ADR.",
                filepath,
            )
        ]
    reason = entry.get("reason", "no reason recorded")
    return [
        (
            LEGACY_ALLOWANCE_SEVERITY,
            f"STD '{doc_id}' is at major version {major} without 'authorized_by'. Recorded legacy debt "
            f"until {expires.isoformat()}: {reason}",
            filepath,
        )
    ]


def _audit_authorizes_backlinks(doc_id, meta, registry, sev):
    """
    Check that every Standard named in an ADR's `authorizes` exists and names the ADR back.
    """
    findings = []
    filepath = meta.get("_filepath", doc_id)
    for ref in _as_list(meta.get("authorizes")):
        std = registry.get(ref) if isinstance(ref, str) else None
        if (
            not isinstance(ref, str)
            or not ref.startswith("STD-")
            or not isinstance(std, dict)
        ):
            findings.append(
                (
                    sev,
                    f"ADR '{doc_id}' names '{ref}' in 'authorizes', but it is not an STD in this repository.",
                    filepath,
                )
            )
        elif doc_id not in _as_list(std.get("authorized_by")):
            findings.append(
                (
                    sev,
                    f"ADR '{doc_id}' authorizes STD '{ref}', but the Standard does not name it in 'authorized_by'.",
                    filepath,
                )
            )
    return findings


def audit_standard_authorization(
    local_doc_metadata: dict,
    severity_levels: dict,
    legacy_entries: list | None = None,
    registry: dict | None = None,
    today: date | None = None,
) -> list[tuple[str, str, str]]:
    """
    Enforce the ADR authorization invariant of GDC-007 section 2.4.2.

    <pre>Args:
        - local_doc_metadata (dict): Documents in the lint target, keyed by document ID.
        - severity_levels (dict): Mapping of SeverityRule to severity string.
        - legacy_entries (list, optional): Dated allowances for Standards that reached a
          major version before the authorization field existed. Each entry carries `id`,
          `expires`, and `reason`.
        - registry (dict, optional): Full document registry used to resolve references.
          Defaults to `local_doc_metadata`.
        - today (date, optional): Evaluation date. Defaults to the current date.

    Returns:
        list[tuple[str, str, str]]: A list of (severity, message, filepath) tuples.
    </pre>
    """
    findings = []
    sev = severity_levels[SeverityRule.UNAUTHORIZED_MAJOR_REVISION]
    registry = registry if registry is not None else local_doc_metadata
    today = today or date.today()
    legacy = {
        entry.get("id"): entry
        for entry in (legacy_entries or [])
        if isinstance(entry, dict) and entry.get("id")
    }

    for doc_id, meta in local_doc_metadata.items():
        if not isinstance(meta, dict):
            continue
        if str(doc_id).startswith("STD-"):
            findings.extend(_audit_authorizing_adrs(doc_id, meta, registry, sev))
            findings.extend(
                _audit_missing_authorization(doc_id, meta, legacy, today, sev)
            )
        elif str(doc_id).startswith("ADR-"):
            findings.extend(_audit_authorizes_backlinks(doc_id, meta, registry, sev))

    for legacy_id, entry in legacy.items():
        meta = registry.get(legacy_id)
        if not isinstance(meta, dict):
            findings.append(
                (
                    LEGACY_ALLOWANCE_SEVERITY,
                    f"Legacy authorization allowance '{legacy_id}' does not match any STD. Remove the entry.",
                    "00-governance/schemas/base.schema.json",
                )
            )
        elif _as_list(meta.get("authorized_by")):
            findings.append(
                (
                    LEGACY_ALLOWANCE_SEVERITY,
                    f"Legacy authorization allowance '{legacy_id}' is obsolete because the Standard now "
                    "declares 'authorized_by'. Remove the entry.",
                    meta.get("_filepath", legacy_id),
                )
            )

    return findings


def audit_replacement_lineage(
    local_doc_metadata: dict,
    severity_levels: dict,
    registry: dict | None = None,
) -> list[tuple[str, str, str]]:
    """
    Enforce the replacement procedure of GDC-010 section 2.4.2 on the final state of a commit.

    A `replacement` ADR names the decisions it replaces in `supersedes`. While the
    replacement is `proposed`, every replaced ADR stays `accepted`, so a binding
    decision exists throughout the review. When the replacement is `accepted`, every
    replaced ADR is `superseded` and names the replacement in `superseded_by`. A
    `superseded` ADR must point at an accepted replacement that points back.

    <pre>Args:
        - local_doc_metadata (dict): Documents in the lint target, keyed by document ID.
        - severity_levels (dict): Mapping of SeverityRule to severity string.
        - registry (dict, optional): Full document registry used to resolve references.
          Defaults to `local_doc_metadata`.

    Returns:
        list[tuple[str, str, str]]: A list of (severity, message, filepath) tuples.
    </pre>
    """
    findings = []
    sev = severity_levels[SeverityRule.DECISION_LINEAGE_VIOLATION]
    registry = registry if registry is not None else local_doc_metadata

    for doc_id, meta in local_doc_metadata.items():
        if not isinstance(meta, dict) or not str(doc_id).startswith("ADR-"):
            continue
        status = str(meta.get("status", "")).lower()

        if str(meta.get("adr_type", "")).lower() == "replacement":
            findings.extend(
                _audit_replaced_decisions(doc_id, meta, status, registry, sev)
            )

        if status == "superseded":
            findings.extend(_audit_superseded_decision(doc_id, meta, registry, sev))

    return findings


def _audit_replaced_decisions(doc_id, meta, status, registry, sev):
    """
    Check the ADRs named in a replacement's `supersedes` against the replacement's status.
    """
    findings = []
    filepath = meta.get("_filepath", doc_id)
    for ref in _as_list(meta.get("supersedes")):
        old = registry.get(ref) if isinstance(ref, str) else None
        if (
            not isinstance(ref, str)
            or not ref.startswith("ADR-")
            or not isinstance(old, dict)
        ):
            findings.append(
                (
                    sev,
                    f"Replacement ADR '{doc_id}' supersedes '{ref}', which is not an ADR in this repository.",
                    filepath,
                )
            )
            continue
        old_status = str(old.get("status", "")).lower() or "unknown"
        if status == "proposed" and old_status != "accepted":
            findings.append(
                (
                    sev,
                    f"Replacement ADR '{doc_id}' is under review, so the ADR it replaces ('{ref}') "
                    f"must stay 'accepted' until ratification, but it is '{old_status}'.",
                    filepath,
                )
            )
        elif status == "accepted" and (
            old_status != "superseded"
            or doc_id not in _as_list(old.get("superseded_by"))
        ):
            findings.append(
                (
                    sev,
                    f"Replacement ADR '{doc_id}' is accepted, so '{ref}' must be 'superseded' and name "
                    f"'{doc_id}' in 'superseded_by' in the same commit.",
                    filepath,
                )
            )
    return findings


def _audit_superseded_decision(doc_id, meta, registry, sev):
    """
    Check that a superseded ADR points at accepted replacements that point back.
    """
    filepath = meta.get("_filepath", doc_id)
    replacements = _as_list(meta.get("superseded_by"))
    if not replacements:
        return [
            (
                sev,
                f"ADR '{doc_id}' is superseded but names no replacement in 'superseded_by'.",
                filepath,
            )
        ]
    findings = []
    for ref in replacements:
        new = registry.get(ref) if isinstance(ref, str) else None
        if (
            not isinstance(new, dict)
            or str(new.get("adr_type", "")).lower() != "replacement"
            or doc_id not in _as_list(new.get("supersedes"))
            or str(new.get("status", "")).lower() != "accepted"
        ):
            findings.append(
                (
                    sev,
                    f"ADR '{doc_id}' is superseded by '{ref}', which must be an accepted replacement ADR "
                    f"that names '{doc_id}' in 'supersedes'.",
                    filepath,
                )
            )
    return findings
