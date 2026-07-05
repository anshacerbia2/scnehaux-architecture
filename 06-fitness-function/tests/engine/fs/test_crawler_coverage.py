import pytest
from unittest.mock import patch, mock_open
import os
from engine.fs.crawler import resolve_registry_with_duplicates

def test_crawler_handles_exception_during_read():
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [("some_dir", [], ["test.md"])]
        with patch("builtins.open", side_effect=PermissionError("Mocked Permission Error")):
            ids, metadata, duplicates = resolve_registry_with_duplicates("some_dir")
            assert len(ids) == 0
            assert len(metadata) == 0
            assert len(duplicates) == 0
