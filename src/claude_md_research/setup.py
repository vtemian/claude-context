# src/claude_md_research/setup.py
"""Set up and tear down experiment file structures."""

import json
import os
import shutil
from dataclasses import dataclass, field
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
    emojis_by_level: dict[int, list[str]] = field(default_factory=dict)
    backed_up_user_claude_md: str | None = None

    @property
    def all_emojis(self) -> list[str]:
        """Get flat list of all emojis used across all levels."""
        all_emojis = []
        for emojis in self.emojis_by_level.values():
            all_emojis.extend(emojis)
        return all_emojis


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
    padding_size: int | None = None,
    num_rules: int | None = None,
    max_emojis: int = 5,
    style: str = "neutral",
    backup_user_config: bool = False,
    skip_user_config: bool = False,
    use_claude_padding: bool = False,
) -> ExperimentSetup:
    """Create CLAUDE.md files for an experiment trial.

    Args:
        config: Experiment configuration
        base_dir: Base directory for project-level files
        padding_size: Size of reinforcement padding (chars)
        num_rules: Total number of rules to distribute across levels (overrides padding_size)
        max_emojis: Max emojis per level for padding mode (default 5)
        style: Emphasis style for rules
        backup_user_config: If True, backup ~/.claude/CLAUDE.md before modifying
        skip_user_config: If True, do not create/modify ~/.claude/CLAUDE.md (level 0)
        use_claude_padding: If True, use Claude API to generate varied padding
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    claude_md_paths = []
    emojis_by_level = {}
    backed_up_path = None

    # Calculate rules per level if num_rules specified
    active_levels = config.levels - 1 if skip_user_config else config.levels
    rules_per_level = None
    if num_rules is not None:
        rules_per_level = num_rules // active_levels

    for level in range(config.levels):
        if level == 0:
            # Level 0: User config (~/.claude/CLAUDE.md)
            if skip_user_config:
                continue

            content, emojis = generate_claude_md_content(
                level=level,
                padding_size=padding_size,
                num_rules=rules_per_level,
                max_emojis=max_emojis,
                style=style,
                use_claude_padding=use_claude_padding,
            )
            emojis_by_level[level] = emojis

            user_claude_md = Path.home() / ".claude" / "CLAUDE.md"

            if backup_user_config and user_claude_md.exists():
                backed_up_path = str(user_claude_md) + ".backup"
                shutil.copy(user_claude_md, backed_up_path)

            user_claude_md.parent.mkdir(parents=True, exist_ok=True)
            user_claude_md.write_text(content)
            claude_md_paths.append(str(user_claude_md))
        else:
            # Project-level configs (levels 1-4)
            if level < len(LEVEL_PATHS) and LEVEL_PATHS[level]:
                content, emojis = generate_claude_md_content(
                    level=level,
                    padding_size=padding_size,
                    num_rules=rules_per_level,
                    max_emojis=max_emojis,
                    style=style,
                    use_claude_padding=use_claude_padding,
                )
                emojis_by_level[level] = emojis

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

    # Save emojis manifest for the analyzer
    manifest_path = base_path / ".emojis_manifest.json"
    manifest_path.write_text(json.dumps(emojis_by_level, ensure_ascii=False, indent=2))

    return ExperimentSetup(
        config=config,
        base_dir=base_dir,
        working_dir=working_dir,
        claude_md_paths=claude_md_paths,
        emojis_by_level=emojis_by_level,
        backed_up_user_claude_md=backed_up_path,
    )


def teardown_experiment_files(setup: ExperimentSetup) -> None:
    """Remove experiment files and restore backups."""
    user_claude_md = str(Path.home() / ".claude" / "CLAUDE.md")

    # Remove project files (skip user config if present)
    for path in setup.claude_md_paths:
        if path == user_claude_md:
            # Don't delete user config - it will be restored from backup
            continue
        if os.path.exists(path):
            os.remove(path)

    # Restore user config if backed up
    if setup.backed_up_user_claude_md:
        user_path = Path.home() / ".claude" / "CLAUDE.md"
        shutil.move(setup.backed_up_user_claude_md, user_path)
