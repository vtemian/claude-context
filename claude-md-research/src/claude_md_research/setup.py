# src/claude_md_research/setup.py
"""Set up and tear down experiment file structures."""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from claude_md_research.config import ExperimentConfig
from claude_md_research.generator import generate_claude_md_content


@dataclass
class ExperimentSetup:
    """Tracks created files for an experiment."""

    config: ExperimentConfig
    base_dir: str
    working_dir: str
    claude_md_paths: list[str]
    backed_up_user_claude_md: str | None = None


# Directory structure for levels (relative to base_dir)
LEVEL_PATHS = [
    None,  # Level 0: User config (~/.claude/CLAUDE.md) - handled separately
    "CLAUDE.md",  # Level 1: Project root
    "src/CLAUDE.md",  # Level 2
    "src/lib/CLAUDE.md",  # Level 3
    "src/lib/core/CLAUDE.md",  # Level 4
]


def setup_experiment_files(
    config: ExperimentConfig,
    base_dir: str,
    padding_size: int,
    style: str = "neutral",
    backup_user_config: bool = False,
) -> ExperimentSetup:
    """Create CLAUDE.md files for an experiment trial."""
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    claude_md_paths = []
    backed_up_path = None

    for level in range(config.levels):
        emoji = config.emojis[level]
        content = generate_claude_md_content(
            emoji=emoji,
            padding_size=padding_size,
            style=style,
        )

        if level == 0:
            # Level 0: User config
            user_claude_md = Path.home() / ".claude" / "CLAUDE.md"

            if backup_user_config and user_claude_md.exists():
                backed_up_path = str(user_claude_md) + ".backup"
                shutil.copy(user_claude_md, backed_up_path)

            user_claude_md.parent.mkdir(parents=True, exist_ok=True)
            user_claude_md.write_text(content)
            claude_md_paths.append(str(user_claude_md))
        else:
            # Project-level configs
            if level < len(LEVEL_PATHS) and LEVEL_PATHS[level]:
                rel_path = LEVEL_PATHS[level]
                full_path = base_path / rel_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                claude_md_paths.append(str(full_path))

    # Determine working directory (deepest level)
    working_dir = str(base_path)
    if config.levels > 1 and len(claude_md_paths) > 1:
        deepest = Path(claude_md_paths[-1])
        working_dir = str(deepest.parent)

    return ExperimentSetup(
        config=config,
        base_dir=base_dir,
        working_dir=working_dir,
        claude_md_paths=claude_md_paths,
        backed_up_user_claude_md=backed_up_path,
    )


def teardown_experiment_files(setup: ExperimentSetup) -> None:
    """Remove experiment files and restore backups."""
    # Remove project files (skip level 0 which is user config)
    for path in setup.claude_md_paths[1:]:
        if os.path.exists(path):
            os.remove(path)

    # Restore user config if backed up
    if setup.backed_up_user_claude_md:
        user_path = Path.home() / ".claude" / "CLAUDE.md"
        shutil.move(setup.backed_up_user_claude_md, user_path)
