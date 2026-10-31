import re

from markdown_it import MarkdownIt

from engine.parsing.markdown_ast import extract_sections_normalized, strip_code_fences
from engine.validators.base import BaseValidator

# Markdown link target: `[text](target)`, `[text](<target>)`, or `[text](target "title")`.
_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
# Autolink `<https://...>` or a bare `https://...` URL.
_HTTPS_URL = re.compile(r"(?<![\w(])<?https://[^\s>|)]+")
_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _normalise_cell(text: str) -> str:
    """Lower-case a table cell and strip inline emphasis and code markers."""
    stripped = re.sub(r"[`*_]", "", text)
    return re.sub(r"\s+", " ", stripped).strip().lower()


def _is_repository_evidence(target: str) -> bool:
    """
    A link counts as repository evidence when it is an `https://` URL or a relative path
    inside this repository. Fragment-only links, `mailto:`, plain `http://`, and every other
    scheme are rejected: they cannot point at a file, commit, pull request, or workflow run.
    """
    if not target or target.startswith("#"):
        return False
    if target.lower().startswith("https://"):
        return True
    return not _URI_SCHEME.match(target)


def _cell_has_evidence(cell: str) -> bool:
    for target in _MARKDOWN_LINK.findall(cell):
        if _is_repository_evidence(target):
            return True
    return bool(_HTTPS_URL.search(cell))


def _clause_cited(reference: str, text: str) -> bool:
    """True when a clause (6.1.2) or control (A.5.9) number is cited and not as a prefix of a longer one."""
    pattern = r"(?<![\w.])" + re.escape(reference) + r"(?!\.?\d)"
    return re.search(pattern, text) is not None


class ISMSValidator(BaseValidator):
    doc_type_name: str = "ISMS"

    def validate_type_specific(self) -> None:
        """
        Execute rules specific to ISMS records (GDC-012).

        Enforces the management-system record contract:
        - At least one ISO/IEC 27001:2022 clause or Annex A control is declared, and every declared
          number is cited in the 'ISO/IEC 27001 Mapping' section.
        - `review_cycle_days` does not exceed the maximum for the record kind (`isms_record`).
        - Each single-instance record kind has exactly one active home in the registry.
        - The body makes no certification claim, carries no personal identifier, and does not
          reproduce normative requirement text ('shall').
        - Every 'Control status' table uses the control status vocabulary, links repository
          evidence for each 'implemented' row, and justifies each 'not applicable' row.

        <pre>Args:
            None

        Returns:
            None
        </pre>
        """
        # @flow-domain: StartISMS((Start ISMS Validation)) --> LoadRules["Load x-isms-rules from isms.schema.json"]
        if not self.doc_meta:
            return

        rules = self.domain_schema.get("x-isms-rules", {})

        # @flow-domain: LoadRules --> CheckMapping{"Clauses or controls declared and cited?"}
        self._validate_mapping(rules)
        # @flow-domain: CheckMapping --> CheckCadence{"review_cycle_days within record maximum?"}
        self._validate_review_cadence(rules)
        # @flow-domain: CheckCadence --> CheckHome{"Single active home for record kind?"}
        self._validate_single_home(rules)
        # @flow-domain: CheckHome --> CheckPublication["Scan body: certification claims, personal identifiers, 'shall'"]
        self._validate_publication_rules(rules)
        # @flow-domain: CheckPublication --> CheckControls["Validate 'Control status' tables and evidence links"]
        self._validate_control_status_tables(rules)
        # @flow-domain: CheckControls --> EndISMS((Return findings))

    def _validate_mapping(self, rules: dict) -> None:
        clauses = self.doc_meta.get("iso_clauses") or []
        controls = self.doc_meta.get("annex_a_controls") or []
        if not isinstance(clauses, list) or not isinstance(controls, list):
            return  # The JSON schema reports the type error.

        if not clauses and not controls:
            self.add_error(
                "missing_metadata",
                "ISMS record declares neither 'iso_clauses' nor 'annex_a_controls'. "
                "Every record answers at least one ISO/IEC 27001:2022 clause or Annex A control.",
            )
            return

        section_name = rules.get("mapping_section", "ISO/IEC 27001 Mapping")
        mapping_text = extract_sections_normalized(self.content).get(section_name)
        if mapping_text is None:
            return  # The JSON schema reports the missing section.

        for reference in [str(c) for c in clauses] + [str(c) for c in controls]:
            if not _clause_cited(reference, mapping_text):
                self.add_error(
                    "missing_section_keyword",
                    f"'{reference}' is declared in doc_meta but not cited in the "
                    f"'{section_name}' section. Cite its number and title.",
                )

    def _validate_review_cadence(self, rules: dict) -> None:
        record_kind = self.doc_meta.get("isms_record")
        cycle = self.doc_meta.get("review_cycle_days")
        limit = rules.get("record_review_cycle_max_days", {}).get(record_kind)
        if limit is None or not isinstance(cycle, int) or isinstance(cycle, bool):
            return
        if cycle > limit:
            self.add_error(
                "isms_review_cadence_violation",
                f"ISMS record kind '{record_kind}' must be reviewed at least every {limit} days, "
                f"but declares review_cycle_days: {cycle}.",
            )

    def _validate_single_home(self, rules: dict) -> None:
        record_kind = self.doc_meta.get("isms_record")
        if record_kind not in rules.get("single_instance_records", []):
            return
        if str(self.doc_meta.get("status", "")).lower() == "deprecated":
            return

        own_id = self.doc_meta.get("id")
        for other_id, meta in sorted(self.all_doc_metadata.items()):
            if other_id == own_id or not str(other_id).startswith("ISMS-"):
                continue
            if not isinstance(meta, dict):
                continue
            if meta.get("isms_record") != record_kind:
                continue
            if str(meta.get("status", "")).lower() == "deprecated":
                continue
            self.add_error(
                "structural_integrity_violation",
                f"ISMS record kind '{record_kind}' already has an active home in '{other_id}'. "
                "A record kind other than 'other' lives in exactly one document.",
            )

    def _body_text(self) -> str:
        """Body text with code fences and frontmatter blanked, preserving line numbers."""
        text = strip_code_fences(self.content)
        return re.sub(
            r"^---\s+.*?\s+---",
            lambda m: "\n" * m.group(0).count("\n"),
            text,
            flags=re.DOTALL,
        )

    def _scan(self, text: str, patterns: list, rule_id: str, message: str) -> None:
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                line_num = text.count("\n", 0, match.start()) + 1
                self.add_error(
                    rule_id,
                    f"{message} Found '{match.group(0)}' on line {line_num}.",
                    line_num=line_num,
                )

    def _validate_publication_rules(self, rules: dict) -> None:
        text = self._body_text()
        self._scan(
            text,
            rules.get("certification_claim_patterns", []),
            "isms_certification_claim",
            "ISMS records make no certification claim; write 'aligned with' or "
            "'prepared for' ISO/IEC 27001:2022.",
        )
        self._scan(
            text,
            rules.get("personal_identifier_patterns", []),
            "isms_personal_identifier",
            "ISMS records name roles, never people: no email address or personal account handle.",
        )
        self._scan(
            text,
            rules.get("reproduced_requirement_patterns", []),
            "isms_reproduced_requirement_text",
            "ISMS records never reproduce ISO/IEC 27001 text; cite the clause or control number "
            "and title, and state requirements with MUST / MUST NOT.",
        )

    def _iter_tables(self):
        """Yield each Markdown table as a list of (cells, line_number) rows, header row first."""
        text = self._body_text()
        tokens = MarkdownIt("commonmark").enable("table").parse(text)

        rows: list = []
        row: list | None = None
        row_line = 0
        for token in tokens:
            if token.type == "table_open":
                rows = []
            elif token.type == "tr_open":
                row = []
                row_line = (token.map[0] + 1) if token.map else 0
            elif token.type == "inline" and row is not None:
                row.append(token.content)
            elif token.type == "tr_close" and row is not None:
                rows.append((row, row_line))
                row = None
            elif token.type == "table_close":
                yield rows

    def _validate_control_status_tables(self, rules: dict) -> None:
        config = rules.get("control_status", {})
        status_column = config.get("status_column", "control status")
        evidence_column = config.get("evidence_column", "evidence")
        justification_column = config.get("justification_column", "justification")
        allowed = config.get("allowed_values", [])
        needs_evidence = set(config.get("evidence_required_for", []))
        needs_justification = set(config.get("justification_required_for", []))
        empty_values = set(config.get("empty_justification_values", [""]))

        for rows in self._iter_tables():
            # A Markdown table always has a header row.
            header, header_line = rows[0]
            columns = [_normalise_cell(cell) for cell in header]
            if status_column not in columns:
                continue

            status_idx = columns.index(status_column)
            evidence_idx = (
                columns.index(evidence_column) if evidence_column in columns else None
            )
            justification_idx = (
                columns.index(justification_column)
                if justification_column in columns
                else None
            )

            if evidence_idx is None:
                self.add_error(
                    "isms_control_status_violation",
                    f"Table on line {header_line} has a 'Control status' column but no "
                    "'Evidence' column.",
                    line_num=header_line,
                )

            for cells, line_num in rows[1:]:
                status = (
                    _normalise_cell(cells[status_idx])
                    if status_idx < len(cells)
                    else ""
                )
                if status not in allowed:
                    self.add_error(
                        "isms_control_status_violation",
                        f"Control status '{status}' on line {line_num} is not one of: "
                        f"{', '.join(allowed)}.",
                        line_num=line_num,
                    )
                    continue

                if status in needs_evidence and evidence_idx is not None:
                    cell = cells[evidence_idx] if evidence_idx < len(cells) else ""
                    if not _cell_has_evidence(cell):
                        self.add_error(
                            "isms_control_status_violation",
                            f"Control on line {line_num} is '{status}' but its 'Evidence' cell "
                            "links no repository evidence (an https:// URL or a relative path).",
                            line_num=line_num,
                        )

                if status in needs_justification:
                    cell = (
                        cells[justification_idx]
                        if justification_idx is not None
                        and justification_idx < len(cells)
                        else ""
                    )
                    if _normalise_cell(cell) in empty_values:
                        self.add_error(
                            "isms_control_status_violation",
                            f"Control on line {line_num} is '{status}' but has no "
                            "'Justification'.",
                            line_num=line_num,
                        )
