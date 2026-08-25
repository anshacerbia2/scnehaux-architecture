import pytest
from unittest.mock import patch, mock_open
from engine.config.loader import load_json_schema_file


def test_load_json_schema_file_success():
    """
    Validates that a valid JSON schema file is successfully parsed.
    Mocks the file system read operation to return a predefined JSON structure.
    """
    mock_json = '{"type": "object", "properties": {"id": {"type": "string"}}}'
    with patch("builtins.open", mock_open(read_data=mock_json)):
        result = load_json_schema_file("fake_schema.json")

    assert result == {"type": "object", "properties": {"id": {"type": "string"}}}


@patch("engine.config.loader.logger.critical")
def test_load_json_schema_file_not_found(mock_logger_critical):
    """
    Validates the behavior when a schema file is missing.
    Ensures that a FileNotFoundError is properly raised.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_json_schema_file("missing_schema.json")


def test_validate_severity_schema_unknown_rule():
    from engine.config.loader import validate_severity_schema
    from engine.config.severity import SeverityRule

    full_levels = {r.value: "ERROR" for r in SeverityRule}
    full_levels["unknown_rule_xyz"] = "HIGH"
    with pytest.raises(RuntimeError) as exc:
        validate_severity_schema(full_levels)
    assert "Unknown severity rules found" in str(exc.value)


def test_validate_blocking_severities_missing_and_unknown():
    from engine.config.loader import validate_blocking_severities

    # Missing required blocking severity
    with pytest.raises(RuntimeError) as exc1:
        validate_blocking_severities(["CRITICAL"])
    assert "Missing blocking severities" in str(exc1.value)

    # Unknown blocking severity
    with pytest.raises(RuntimeError) as exc2:
        validate_blocking_severities(["CRITICAL", "ERROR", "UNKNOWN_SEV"])
    assert "Unknown blocking severities" in str(exc2.value)
