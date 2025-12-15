# tests/test_runner.py
import pytest
from unittest.mock import patch, MagicMock
from claude_md_research.runner import run_claude_session, RunResult


def test_run_claude_session_success():
    mock_output = """
Section 1: The sun rose. 😀

Section 2: Birds sang. 😀
"""

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            stderr="",
            returncode=0,
        )

        result = run_claude_session(
            working_dir="/tmp/test",
            prompt="Write 2 sections.",
            timeout=30,
        )

        assert result.success is True
        assert result.output == mock_output
        assert "Section 1" in result.output


def test_run_claude_session_timeout():
    with patch("subprocess.run") as mock_run:
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=30)

        result = run_claude_session(
            working_dir="/tmp/test",
            prompt="Write sections.",
            timeout=30,
        )

        assert result.success is False
        assert "timeout" in result.error.lower()
