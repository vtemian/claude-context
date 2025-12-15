# tests/test_setup.py
import pytest
import tempfile
import os
from pathlib import Path
from claude_md_research.setup import (
    setup_experiment_files,
    teardown_experiment_files,
    ExperimentSetup,
)
from claude_md_research.config import ExperimentConfig


@pytest.fixture
def sample_config():
    return ExperimentConfig(
        name="test",
        levels=3,
        emojis=["😀", "😃", "😄"],
        padding_sizes=[100],
        trials_per_condition=1,
        prompt="Write 5 sections.",
    )


def test_setup_creates_directory_structure(sample_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup = setup_experiment_files(
            config=sample_config,
            base_dir=tmpdir,
            padding_size=100,
        )

        # Check files were created
        assert os.path.exists(setup.claude_md_paths[0])  # Level 0
        assert os.path.exists(setup.claude_md_paths[1])  # Level 1 (./CLAUDE.md)
        assert os.path.exists(setup.claude_md_paths[2])  # Level 2 (./src/CLAUDE.md)
        assert setup.working_dir.endswith("src")

        # Check content contains emoji
        with open(setup.claude_md_paths[1]) as f:
            content = f.read()
            assert "😃" in content


def test_teardown_removes_files(sample_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup = setup_experiment_files(
            config=sample_config,
            base_dir=tmpdir,
            padding_size=100,
        )

        teardown_experiment_files(setup)

        # Project files should be gone
        assert not os.path.exists(setup.claude_md_paths[1])
        assert not os.path.exists(setup.claude_md_paths[2])
