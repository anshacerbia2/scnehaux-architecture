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
    Validates the Fail-Closed security behavior when a schema file is missing.
    Ensures that a FileNotFoundError triggers a hard system crash (SystemExit)
    and logs a critical error message.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit) as exc_info:
            load_json_schema_file("missing_schema.json")

        # Verify the exit code is 1 (hard crash)
        assert exc_info.value.code == 1
        # Verify the critical logger was called
        mock_logger_critical.assert_called_once_with(
            "Schema file '%s' not found.", "missing_schema.json"
        )
