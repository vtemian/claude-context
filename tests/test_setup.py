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
            skip_user_config=True,  # Don't touch real user config during tests
        )

        # Check files were created (only project levels since skip_user_config=True)
        assert len(setup.claude_md_paths) == 2  # Levels 1 and 2 only
        assert os.path.exists(setup.claude_md_paths[0])  # Level 1 (./CLAUDE.md)
        assert os.path.exists(setup.claude_md_paths[1])  # Level 2 (./src/CLAUDE.md)
        assert setup.working_dir.endswith("src")

        # Check content contains emojis from level 1's pool
        with open(setup.claude_md_paths[0]) as f:
            content = f.read()
            # Verify at least one emoji from level 1 is present
            level_1_emojis = setup.emojis_by_level.get(1, [])
            assert len(level_1_emojis) > 0, "Level 1 should have emojis"
            assert any(emoji in content for emoji in level_1_emojis)


def test_teardown_removes_files(sample_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        setup = setup_experiment_files(
            config=sample_config,
            base_dir=tmpdir,
            padding_size=100,
            skip_user_config=True,  # Don't touch real user config during tests
        )

        teardown_experiment_files(setup)

        # Project files should be gone
        assert not os.path.exists(setup.claude_md_paths[0])
        assert not os.path.exists(setup.claude_md_paths[1])


def test_skip_user_config_does_not_touch_user_claude_md(sample_config):
    """Verify skip_user_config=True leaves ~/.claude/CLAUDE.md untouched."""
    user_claude_md = Path.home() / ".claude" / "CLAUDE.md"

    # Save original content if exists
    original_content = None
    if user_claude_md.exists():
        original_content = user_claude_md.read_text()

    with tempfile.TemporaryDirectory() as tmpdir:
        setup = setup_experiment_files(
            config=sample_config,
            base_dir=tmpdir,
            padding_size=100,
            skip_user_config=True,
        )

        # Level 0 should NOT be in the paths list
        user_path_str = str(user_claude_md)
        assert user_path_str not in setup.claude_md_paths

        # Only project-level files should exist (levels 1 and 2)
        assert len(setup.claude_md_paths) == 2
        assert all(tmpdir in p for p in setup.claude_md_paths)

        # User config should be unchanged
        if original_content is not None:
            assert user_claude_md.read_text() == original_content
