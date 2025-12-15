# CLAUDE.md Compliance Research Framework - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python framework that empirically measures how well Claude follows CLAUDE.md instructions under various conditions (context size, emphasis keywords, formatting, conflicts).

**Architecture:** CLI tool using Click that generates experiment CLAUDE.md files, invokes Claude sessions, parses emoji compliance from output, and produces metrics/charts. Each experiment is configured via YAML.

**Tech Stack:** Python 3.11+, Click (CLI), PyYAML (config), subprocess (Claude invocation), re (parsing), matplotlib (charts), pytest (testing), uv (package management)

---

## Task 1: Project Scaffolding

**Files:**
- Create: `claude-md-research/pyproject.toml`
- Create: `claude-md-research/Makefile`
- Create: `claude-md-research/src/claude_md_research/__init__.py`
- Create: `claude-md-research/tests/__init__.py`

**Step 1: Create project directory structure**

```bash
mkdir -p claude-md-research/src/claude_md_research
mkdir -p claude-md-research/tests
mkdir -p claude-md-research/experiments
mkdir -p claude-md-research/results/{raw,metrics,charts}
cd claude-md-research
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "claude-md-research"
version = "0.1.0"
description = "Empirical research framework for CLAUDE.md instruction compliance"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "pyyaml>=6.0",
    "matplotlib>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.1.0",
]

[project.scripts]
claude-md-research = "claude_md_research.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/claude_md_research"]

[tool.ruff]
line-length = 100
```

**Step 3: Create Makefile**

```makefile
.PHONY: install test lint run clean

install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/

run:
	uv run claude-md-research --help

clean:
	rm -rf results/raw/* results/metrics/* results/charts/*
	find . -type d -name __pycache__ -exec rm -rf {} +
```

**Step 4: Create __init__.py files**

```python
# src/claude_md_research/__init__.py
"""CLAUDE.md Compliance Research Framework."""

__version__ = "0.1.0"
```

```python
# tests/__init__.py
"""Tests for claude-md-research."""
```

**Step 5: Initialize uv and verify**

```bash
uv init
uv sync
uv run python -c "import claude_md_research; print(claude_md_research.__version__)"
```

Expected: `0.1.0`

**Step 6: Commit**

```bash
git add .
git commit -m "feat: scaffold claude-md-research project"
```

---

## Task 2: Configuration Data Model

**Files:**
- Create: `src/claude_md_research/config.py`
- Create: `tests/test_config.py`

**Step 1: Write failing test for config loading**

```python
# tests/test_config.py
import pytest
from claude_md_research.config import ExperimentConfig, load_config


def test_load_scale_experiment_config():
    yaml_content = """
name: scale
description: Test compliance vs context size
levels: 5
emojis: ["😀", "😃", "😄", "😁", "😆"]
padding_sizes: [100, 500, 1000]
padding_style: reinforcement
trials_per_condition: 3
prompt: |
  Write a story with 10 clearly separated sections.
  Number each section (Section 1, Section 2, etc.).
"""
    config = load_config(yaml_content)

    assert config.name == "scale"
    assert config.levels == 5
    assert config.emojis == ["😀", "😃", "😄", "😁", "😆"]
    assert config.padding_sizes == [100, 500, 1000]
    assert config.trials_per_condition == 3


def test_config_validates_emoji_count_matches_levels():
    yaml_content = """
name: test
levels: 3
emojis: ["😀", "😃"]
padding_sizes: [100]
trials_per_condition: 1
prompt: "test"
"""
    with pytest.raises(ValueError, match="emoji count.*must match.*levels"):
        load_config(yaml_content)
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'claude_md_research.config'`

**Step 3: Write config implementation**

```python
# src/claude_md_research/config.py
"""Experiment configuration data model."""

from dataclasses import dataclass, field
from typing import Any
import yaml


@dataclass
class ExperimentConfig:
    """Configuration for a compliance experiment."""

    name: str
    levels: int
    emojis: list[str]
    padding_sizes: list[int]
    trials_per_condition: int
    prompt: str
    description: str = ""
    padding_style: str = "reinforcement"
    emphasis_styles: list[dict[str, str]] = field(default_factory=list)
    formats: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self):
        if len(self.emojis) != self.levels:
            raise ValueError(
                f"emoji count ({len(self.emojis)}) must match levels ({self.levels})"
            )


def load_config(yaml_content: str) -> ExperimentConfig:
    """Load experiment config from YAML string."""
    data = yaml.safe_load(yaml_content)
    return ExperimentConfig(**data)


def load_config_file(path: str) -> ExperimentConfig:
    """Load experiment config from YAML file."""
    with open(path) as f:
        return load_config(f.read())
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_config.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/config.py tests/test_config.py
git commit -m "feat: add experiment config data model"
```

---

## Task 3: CLAUDE.md Generator

**Files:**
- Create: `src/claude_md_research/generator.py`
- Create: `tests/test_generator.py`

**Step 1: Write failing test for rule text generation**

```python
# tests/test_generator.py
import pytest
from claude_md_research.generator import (
    generate_rule_text,
    generate_reinforcement_padding,
    generate_claude_md_content,
)


def test_generate_rule_text_neutral():
    text = generate_rule_text("😀", style="neutral")
    assert "😀" in text
    assert "section" in text.lower()


def test_generate_rule_text_important():
    text = generate_rule_text("😀", style="important")
    assert "😀" in text
    assert "IMPORTANT" in text


def test_generate_reinforcement_padding():
    padding = generate_reinforcement_padding("😀", target_chars=500)
    assert "😀" in padding
    assert len(padding) >= 450  # Allow some variance
    assert len(padding) <= 550


def test_generate_claude_md_content():
    content = generate_claude_md_content(
        emoji="😀",
        padding_size=200,
        style="important",
    )
    assert "😀" in content
    assert "IMPORTANT" in content
    assert len(content) >= 150
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_generator.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write generator implementation**

```python
# src/claude_md_research/generator.py
"""Generate CLAUDE.md content with configurable rules and padding."""

import random

RULE_TEMPLATES = {
    "neutral": [
        "Every section should contain one {emoji}.",
        "Include {emoji} in each section you write.",
        "Each section needs a {emoji} somewhere in it.",
    ],
    "important": [
        "IMPORTANT: Every section MUST contain exactly one {emoji}.",
        "CRITICAL: Always include {emoji} in every section.",
        "REQUIRED: Each section must have one {emoji}.",
    ],
    "never": [
        "NEVER write a section without {emoji}. It is REQUIRED.",
        "Do NOT omit {emoji} from any section. ALWAYS include it.",
        "FORBIDDEN to skip {emoji} in any section.",
    ],
    "caps": [
        "EVERY SECTION MUST CONTAIN ONE {emoji}. NO EXCEPTIONS.",
        "YOU MUST PUT {emoji} IN EVERY SINGLE SECTION.",
        "MANDATORY: {emoji} IN ALL SECTIONS.",
    ],
}

REINFORCEMENT_TEMPLATES = [
    "Remember to include {emoji} in every section.",
    "The {emoji} symbol is required in all paragraphs.",
    "Do not forget: {emoji} must appear in each section.",
    "Every section needs exactly one {emoji}.",
    "Always place {emoji} in your output sections.",
    "Make sure {emoji} appears in every section you write.",
    "Each paragraph should contain {emoji}.",
    "The {emoji} emoji is mandatory for all sections.",
    "Include {emoji} consistently throughout all sections.",
    "Your sections must each have {emoji} in them.",
    "Don't skip {emoji} in any section.",
    "{emoji} is a required element in every section.",
    "All sections require {emoji} to be present.",
    "Ensure {emoji} is in each section without exception.",
    "Place {emoji} somewhere in every section.",
]


def generate_rule_text(emoji: str, style: str = "neutral") -> str:
    """Generate a single rule statement for an emoji."""
    templates = RULE_TEMPLATES.get(style, RULE_TEMPLATES["neutral"])
    template = random.choice(templates)
    return template.format(emoji=emoji)


def generate_reinforcement_padding(emoji: str, target_chars: int) -> str:
    """Generate padding text that reinforces the emoji rule."""
    lines = []
    current_chars = 0

    templates = REINFORCEMENT_TEMPLATES.copy()
    random.shuffle(templates)
    template_index = 0

    while current_chars < target_chars:
        template = templates[template_index % len(templates)]
        line = template.format(emoji=emoji)
        lines.append(line)
        current_chars += len(line) + 1  # +1 for newline
        template_index += 1

    return "\n".join(lines)


def generate_claude_md_content(
    emoji: str,
    padding_size: int = 0,
    style: str = "neutral",
) -> str:
    """Generate complete CLAUDE.md content for one level."""
    parts = []

    # Primary rule
    rule = generate_rule_text(emoji, style)
    parts.append(rule)

    # Padding (reinforcement)
    if padding_size > 0:
        # Account for the rule we already added
        remaining = padding_size - len(rule) - 2
        if remaining > 0:
            padding = generate_reinforcement_padding(emoji, remaining)
            parts.append(padding)

    return "\n\n".join(parts)
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_generator.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/generator.py tests/test_generator.py
git commit -m "feat: add CLAUDE.md content generator"
```

---

## Task 4: Experiment File Setup

**Files:**
- Create: `src/claude_md_research/setup.py`
- Create: `tests/test_setup.py`

**Step 1: Write failing test for experiment setup**

```python
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
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_setup.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write setup implementation**

```python
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
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_setup.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/setup.py tests/test_setup.py
git commit -m "feat: add experiment file setup/teardown"
```

---

## Task 5: Output Analyzer

**Files:**
- Create: `src/claude_md_research/analyzer.py`
- Create: `tests/test_analyzer.py`

**Step 1: Write failing test for section parsing and emoji counting**

```python
# tests/test_analyzer.py
import pytest
from claude_md_research.analyzer import (
    parse_sections,
    count_emojis_in_section,
    analyze_compliance,
    ComplianceResult,
)


def test_parse_sections_numbered():
    text = """
Section 1: The sun rose over the mountains. 😀

Section 2: Birds began to sing. 😀😃

Section 3: The day had begun.
"""
    sections = parse_sections(text)
    assert len(sections) == 3
    assert "sun rose" in sections[0]
    assert "Birds" in sections[1]
    assert "day had begun" in sections[2]


def test_count_emojis_in_section():
    section = "Hello 😀 world 😃 test 😀"
    counts = count_emojis_in_section(section, ["😀", "😃", "😄"])
    assert counts["😀"] == 2
    assert counts["😃"] == 1
    assert counts["😄"] == 0


def test_analyze_compliance_full():
    text = """
Section 1: Test 😀😃😄

Section 2: Test 😀😃😄

Section 3: Test 😀😃
"""
    emojis = ["😀", "😃", "😄"]
    result = analyze_compliance(text, emojis)

    assert result.total_sections == 3
    assert result.compliance_rates["😀"] == 1.0  # 3/3
    assert result.compliance_rates["😃"] == 1.0  # 3/3
    assert result.compliance_rates["😄"] == pytest.approx(0.666, rel=0.01)  # 2/3
    assert result.overall_compliance == pytest.approx(0.888, rel=0.01)


def test_analyze_compliance_empty_sections():
    text = "No sections here at all."
    result = analyze_compliance(text, ["😀"])
    assert result.total_sections == 0
    assert result.overall_compliance == 0.0
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write analyzer implementation**

```python
# src/claude_md_research/analyzer.py
"""Analyze Claude output for emoji compliance."""

import re
from dataclasses import dataclass


@dataclass
class ComplianceResult:
    """Results of compliance analysis for a trial."""

    total_sections: int
    compliance_rates: dict[str, float]  # emoji -> rate (0.0-1.0)
    emoji_counts: dict[str, dict[str, int]]  # section_num -> emoji -> count
    overall_compliance: float
    raw_text: str


SECTION_PATTERNS = [
    r'Section\s+(\d+)[:\s]*(.*?)(?=Section\s+\d+|$)',
    r'##\s*Section\s+(\d+)[:\s]*(.*?)(?=##\s*Section|$)',
    r'\*\*Section\s+(\d+)\*\*[:\s]*(.*?)(?=\*\*Section|$)',
    r'(\d+)\.\s+(.*?)(?=\d+\.|$)',
]


def parse_sections(text: str) -> list[str]:
    """Extract sections from Claude's output."""
    for pattern in SECTION_PATTERNS:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            return [content.strip() for _, content in matches]
    return []


def count_emojis_in_section(section: str, emojis: list[str]) -> dict[str, int]:
    """Count occurrences of each emoji in a section."""
    return {emoji: section.count(emoji) for emoji in emojis}


def analyze_compliance(text: str, emojis: list[str]) -> ComplianceResult:
    """Analyze emoji compliance across all sections."""
    sections = parse_sections(text)

    if not sections:
        return ComplianceResult(
            total_sections=0,
            compliance_rates={e: 0.0 for e in emojis},
            emoji_counts={},
            overall_compliance=0.0,
            raw_text=text,
        )

    # Count emojis per section
    emoji_counts = {}
    presence = {emoji: 0 for emoji in emojis}

    for i, section in enumerate(sections):
        section_key = f"section_{i+1}"
        counts = count_emojis_in_section(section, emojis)
        emoji_counts[section_key] = counts

        for emoji, count in counts.items():
            if count > 0:
                presence[emoji] += 1

    # Calculate compliance rates
    n_sections = len(sections)
    compliance_rates = {
        emoji: presence[emoji] / n_sections
        for emoji in emojis
    }

    # Overall compliance = average of all emoji compliance rates
    overall = sum(compliance_rates.values()) / len(emojis) if emojis else 0.0

    return ComplianceResult(
        total_sections=n_sections,
        compliance_rates=compliance_rates,
        emoji_counts=emoji_counts,
        overall_compliance=overall,
        raw_text=text,
    )
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_analyzer.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/analyzer.py tests/test_analyzer.py
git commit -m "feat: add output analyzer for emoji compliance"
```

---

## Task 6: Claude Runner

**Files:**
- Create: `src/claude_md_research/runner.py`
- Create: `tests/test_runner.py`

**Step 1: Write failing test for runner (mocked subprocess)**

```python
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
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_runner.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write runner implementation**

```python
# src/claude_md_research/runner.py
"""Execute Claude CLI sessions and capture output."""

import subprocess
import shlex
from dataclasses import dataclass


@dataclass
class RunResult:
    """Result of a Claude session."""

    success: bool
    output: str
    error: str
    working_dir: str
    prompt: str
    duration_seconds: float = 0.0


def run_claude_session(
    working_dir: str,
    prompt: str,
    timeout: int = 60,
) -> RunResult:
    """
    Run Claude CLI with a prompt and capture output.

    Uses: claude --print --prompt "..."
    """
    import time

    cmd = ["claude", "--print", "--prompt", prompt]

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        duration = time.time() - start_time

        return RunResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr,
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=duration,
        )

    except subprocess.TimeoutExpired:
        return RunResult(
            success=False,
            output="",
            error=f"Timeout after {timeout} seconds",
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=timeout,
        )
    except FileNotFoundError:
        return RunResult(
            success=False,
            output="",
            error="Claude CLI not found. Is it installed?",
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=0.0,
        )
    except Exception as e:
        return RunResult(
            success=False,
            output="",
            error=str(e),
            working_dir=working_dir,
            prompt=prompt,
            duration_seconds=time.time() - start_time,
        )
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_runner.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/runner.py tests/test_runner.py
git commit -m "feat: add Claude session runner"
```

---

## Task 7: Metrics and Results Storage

**Files:**
- Create: `src/claude_md_research/metrics.py`
- Create: `tests/test_metrics.py`

**Step 1: Write failing test for metrics storage**

```python
# tests/test_metrics.py
import pytest
import json
import tempfile
from pathlib import Path
from claude_md_research.metrics import (
    TrialMetrics,
    ExperimentMetrics,
    save_trial_metrics,
    load_experiment_metrics,
    aggregate_metrics,
)


def test_trial_metrics_to_dict():
    trial = TrialMetrics(
        trial_id="scale-p1000-t1",
        experiment="scale",
        parameters={"padding_size": 1000},
        sections_found=10,
        compliance_rates={"😀": 1.0, "😃": 0.8},
        overall_compliance=0.9,
        context_size_chars=5000,
        raw_output_file="raw/test.txt",
    )

    d = trial.to_dict()
    assert d["trial_id"] == "scale-p1000-t1"
    assert d["compliance_rates"]["😀"] == 1.0


def test_save_and_load_metrics():
    trial = TrialMetrics(
        trial_id="test-1",
        experiment="test",
        parameters={},
        sections_found=5,
        compliance_rates={"😀": 0.8},
        overall_compliance=0.8,
        context_size_chars=1000,
        raw_output_file="raw/test.txt",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        save_trial_metrics(trial, tmpdir)

        metrics_file = Path(tmpdir) / "metrics" / "test-1.json"
        assert metrics_file.exists()

        loaded = load_experiment_metrics(tmpdir, "test")
        assert len(loaded.trials) == 1
        assert loaded.trials[0].trial_id == "test-1"
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_metrics.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write metrics implementation**

```python
# src/claude_md_research/metrics.py
"""Store and aggregate experiment metrics."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class TrialMetrics:
    """Metrics from a single trial."""

    trial_id: str
    experiment: str
    parameters: dict[str, Any]
    sections_found: int
    compliance_rates: dict[str, float]
    overall_compliance: float
    context_size_chars: int
    raw_output_file: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TrialMetrics":
        return cls(**data)


@dataclass
class ExperimentMetrics:
    """Aggregated metrics for an experiment."""

    experiment: str
    trials: list[TrialMetrics]

    def mean_compliance_by_param(self, param: str) -> dict[Any, float]:
        """Calculate mean compliance grouped by a parameter."""
        groups: dict[Any, list[float]] = {}
        for trial in self.trials:
            key = trial.parameters.get(param)
            if key is not None:
                if key not in groups:
                    groups[key] = []
                groups[key].append(trial.overall_compliance)

        return {k: sum(v) / len(v) for k, v in groups.items()}


def save_trial_metrics(trial: TrialMetrics, results_dir: str) -> None:
    """Save trial metrics to JSON file."""
    metrics_dir = Path(results_dir) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    filepath = metrics_dir / f"{trial.trial_id}.json"
    with open(filepath, "w") as f:
        json.dump(trial.to_dict(), f, indent=2)


def load_experiment_metrics(results_dir: str, experiment: str) -> ExperimentMetrics:
    """Load all trial metrics for an experiment."""
    metrics_dir = Path(results_dir) / "metrics"
    trials = []

    if metrics_dir.exists():
        for filepath in metrics_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)
                if data.get("experiment") == experiment:
                    trials.append(TrialMetrics.from_dict(data))

    return ExperimentMetrics(experiment=experiment, trials=trials)


def aggregate_metrics(metrics: ExperimentMetrics) -> dict:
    """Calculate aggregate statistics."""
    if not metrics.trials:
        return {}

    all_compliance = [t.overall_compliance for t in metrics.trials]

    return {
        "experiment": metrics.experiment,
        "total_trials": len(metrics.trials),
        "mean_compliance": sum(all_compliance) / len(all_compliance),
        "min_compliance": min(all_compliance),
        "max_compliance": max(all_compliance),
    }
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_metrics.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/claude_md_research/metrics.py tests/test_metrics.py
git commit -m "feat: add metrics storage and aggregation"
```

---

## Task 8: CLI Interface

**Files:**
- Create: `src/claude_md_research/cli.py`
- Update: `src/claude_md_research/__init__.py`

**Step 1: Write failing test for CLI commands**

```python
# tests/test_cli.py
import pytest
from click.testing import CliRunner
from claude_md_research.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "CLAUDE.md Compliance Research" in result.output


def test_cli_generate_help():
    runner = CliRunner()
    result = runner.invoke(main, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--experiment" in result.output


def test_cli_analyze_help():
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--help"])
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write CLI implementation**

```python
# src/claude_md_research/cli.py
"""Command-line interface for CLAUDE.md compliance research."""

import click
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """CLAUDE.md Compliance Research Framework.

    Empirically measure how well Claude follows CLAUDE.md instructions
    under various conditions.
    """
    pass


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name (e.g., 01-scale)")
@click.option("--output", "-o", default="./workspace", help="Output directory")
@click.option("--padding", "-p", type=int, default=1000, help="Padding size in chars")
def generate(experiment: str, output: str, padding: int):
    """Generate CLAUDE.md files for an experiment."""
    click.echo(f"Generating experiment: {experiment}")
    click.echo(f"Output directory: {output}")
    click.echo(f"Padding size: {padding}")

    # TODO: Load config and generate files
    click.echo("Generated experiment files.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--trial", "-t", type=int, default=1, help="Trial number")
@click.option("--timeout", type=int, default=60, help="Timeout in seconds")
def run(experiment: str, trial: int, timeout: int):
    """Run a single experiment trial."""
    click.echo(f"Running {experiment} trial {trial}...")

    # TODO: Setup files, run Claude, analyze output
    click.echo("Trial complete.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--input", "-i", "input_dir", default="./results", help="Results directory")
def analyze(experiment: str, input_dir: str):
    """Analyze experiment results."""
    click.echo(f"Analyzing {experiment}...")
    click.echo(f"Input directory: {input_dir}")

    # TODO: Load metrics, compute aggregates
    click.echo("Analysis complete.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--format", "-f", type=click.Choice(["html", "png", "csv"]), default="png")
@click.option("--output", "-o", default="./results/charts", help="Output directory")
def report(experiment: str, format: str, output: str):
    """Generate charts and reports."""
    click.echo(f"Generating {format} report for {experiment}...")

    # TODO: Generate charts
    click.echo(f"Report saved to {output}")


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: PASS (3 tests)

**Step 5: Verify CLI works**

```bash
uv run claude-md-research --help
uv run claude-md-research generate --help
```

Expected: Help text displayed

**Step 6: Commit**

```bash
git add src/claude_md_research/cli.py tests/test_cli.py
git commit -m "feat: add CLI interface"
```

---

## Task 9: Scale Experiment Config

**Files:**
- Create: `experiments/01-scale/config.yaml`

**Step 1: Create experiment configuration**

```yaml
# experiments/01-scale/config.yaml
name: scale
description: |
  Test how compliance degrades as CLAUDE.md context size increases.
  Each level adds one emoji requirement. Padding reinforces the rule.

levels: 5
emojis:
  - "😀"  # Level 0: User (~/.claude/CLAUDE.md)
  - "😃"  # Level 1: Project root (./CLAUDE.md)
  - "😄"  # Level 2: ./src/CLAUDE.md
  - "😁"  # Level 3: ./src/lib/CLAUDE.md
  - "😆"  # Level 4: ./src/lib/core/CLAUDE.md

padding_sizes:
  - 100
  - 500
  - 1000
  - 2000
  - 4000
  - 8000

padding_style: reinforcement
trials_per_condition: 3

prompt: |
  Write a story with 10 clearly separated sections.
  Each section should be 2-3 sentences about any topic.
  Number each section (Section 1, Section 2, etc.).
```

**Step 2: Commit**

```bash
git add experiments/01-scale/config.yaml
git commit -m "feat: add scale experiment configuration"
```

---

## Task 10: Emphasis Experiment Config

**Files:**
- Create: `experiments/02-emphasis/config.yaml`

**Step 1: Create experiment configuration**

```yaml
# experiments/02-emphasis/config.yaml
name: emphasis
description: |
  Test which keywords (IMPORTANT, NEVER, MUST) improve compliance.

levels: 3
emojis:
  - "😀"
  - "😃"
  - "😄"

padding_sizes:
  - 1000

padding_style: reinforcement
trials_per_condition: 5

emphasis_styles:
  - name: neutral
    template: "Every section should contain one {emoji}."

  - name: important
    template: "IMPORTANT: Every section MUST contain exactly one {emoji}."

  - name: never
    template: "NEVER write a section without {emoji}. It is REQUIRED."

  - name: caps
    template: "EVERY SECTION MUST CONTAIN ONE {emoji}. NO EXCEPTIONS."

  - name: bold
    template: "**CRITICAL**: Every section requires {emoji}. This is mandatory."

prompt: |
  Write a story with 10 clearly separated sections.
  Each section should be 2-3 sentences.
  Number each section (Section 1, Section 2, etc.).
```

**Step 2: Commit**

```bash
git add experiments/02-emphasis/config.yaml
git commit -m "feat: add emphasis experiment configuration"
```

---

## Task 11: Integration - Wire CLI to Components

**Files:**
- Modify: `src/claude_md_research/cli.py`

**Step 1: Update CLI to use all components**

```python
# src/claude_md_research/cli.py
"""Command-line interface for CLAUDE.md compliance research."""

import click
from pathlib import Path

from claude_md_research.config import load_config_file
from claude_md_research.setup import setup_experiment_files, teardown_experiment_files
from claude_md_research.runner import run_claude_session
from claude_md_research.analyzer import analyze_compliance
from claude_md_research.metrics import (
    TrialMetrics,
    save_trial_metrics,
    load_experiment_metrics,
    aggregate_metrics,
)


@click.group()
@click.version_option()
def main():
    """CLAUDE.md Compliance Research Framework."""
    pass


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--output", "-o", default="./workspace", help="Output directory")
@click.option("--padding", "-p", type=int, default=1000, help="Padding size")
@click.option("--style", "-s", default="neutral", help="Emphasis style")
def generate(experiment: str, output: str, padding: int, style: str):
    """Generate CLAUDE.md files for an experiment."""
    config_path = f"experiments/{experiment}/config.yaml"

    if not Path(config_path).exists():
        raise click.ClickException(f"Config not found: {config_path}")

    config = load_config_file(config_path)

    setup = setup_experiment_files(
        config=config,
        base_dir=output,
        padding_size=padding,
        style=style,
    )

    click.echo(f"Created {len(setup.claude_md_paths)} CLAUDE.md files")
    click.echo(f"Working directory: {setup.working_dir}")

    for path in setup.claude_md_paths:
        click.echo(f"  - {path}")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--padding", "-p", type=int, required=True, help="Padding size")
@click.option("--trial", "-t", type=int, default=1, help="Trial number")
@click.option("--output", "-o", default="./results", help="Results directory")
@click.option("--timeout", type=int, default=60, help="Timeout seconds")
@click.option("--style", "-s", default="neutral", help="Emphasis style")
def run(experiment: str, padding: int, trial: int, output: str, timeout: int, style: str):
    """Run a single experiment trial."""
    import tempfile

    config_path = f"experiments/{experiment}/config.yaml"
    config = load_config_file(config_path)

    trial_id = f"{experiment}-p{padding}-t{trial}"
    click.echo(f"Running trial: {trial_id}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        setup = setup_experiment_files(
            config=config,
            base_dir=tmpdir,
            padding_size=padding,
            style=style,
            backup_user_config=True,
        )

        # Calculate context size
        context_size = sum(
            Path(p).stat().st_size for p in setup.claude_md_paths
            if Path(p).exists()
        )

        click.echo(f"Context size: {context_size} chars")

        try:
            # Run Claude
            result = run_claude_session(
                working_dir=setup.working_dir,
                prompt=config.prompt,
                timeout=timeout,
            )

            if not result.success:
                click.echo(f"Error: {result.error}", err=True)
                return

            # Save raw output
            raw_dir = Path(output) / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_file = raw_dir / f"{trial_id}.txt"
            raw_file.write_text(result.output)

            # Analyze
            compliance = analyze_compliance(result.output, config.emojis)

            # Save metrics
            metrics = TrialMetrics(
                trial_id=trial_id,
                experiment=experiment,
                parameters={"padding_size": padding, "style": style},
                sections_found=compliance.total_sections,
                compliance_rates=compliance.compliance_rates,
                overall_compliance=compliance.overall_compliance,
                context_size_chars=context_size,
                raw_output_file=str(raw_file),
            )

            save_trial_metrics(metrics, output)

            click.echo(f"Sections found: {compliance.total_sections}")
            click.echo(f"Overall compliance: {compliance.overall_compliance:.1%}")
            for emoji, rate in compliance.compliance_rates.items():
                click.echo(f"  {emoji}: {rate:.1%}")

        finally:
            teardown_experiment_files(setup)


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--input", "-i", "input_dir", default="./results", help="Results dir")
def analyze(experiment: str, input_dir: str):
    """Analyze experiment results."""
    metrics = load_experiment_metrics(input_dir, experiment)

    if not metrics.trials:
        click.echo("No trials found.")
        return

    agg = aggregate_metrics(metrics)

    click.echo(f"Experiment: {agg['experiment']}")
    click.echo(f"Total trials: {agg['total_trials']}")
    click.echo(f"Mean compliance: {agg['mean_compliance']:.1%}")
    click.echo(f"Range: {agg['min_compliance']:.1%} - {agg['max_compliance']:.1%}")

    # Group by padding size
    by_padding = metrics.mean_compliance_by_param("padding_size")
    if by_padding:
        click.echo("\nBy padding size:")
        for size, rate in sorted(by_padding.items()):
            click.echo(f"  {size:>5} chars: {rate:.1%}")


if __name__ == "__main__":
    main()
```

**Step 2: Run all tests**

```bash
uv run pytest tests/ -v
```

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/claude_md_research/cli.py
git commit -m "feat: wire CLI to all components"
```

---

## Task 12: README Documentation

**Files:**
- Create: `claude-md-research/README.md`

**Step 1: Write README**

```markdown
# CLAUDE.md Compliance Research Framework

Empirically measure how well Claude follows CLAUDE.md instructions under various conditions.

## Installation

```bash
uv sync
```

## Quick Start

```bash
# Generate experiment files
uv run claude-md-research generate -e 01-scale -o ./workspace -p 1000

# Run a trial
uv run claude-md-research run -e 01-scale -p 1000 -t 1 -o ./results

# Analyze results
uv run claude-md-research analyze -e 01-scale -i ./results
```

## Experiments

- **01-scale**: Context size vs compliance
- **02-emphasis**: Keyword effectiveness (IMPORTANT, NEVER, etc.)

## How It Works

1. Each CLAUDE.md level introduces a unique emoji requirement
2. Claude generates a story with numbered sections
3. Python script counts emoji occurrences per section
4. Compliance rate = sections_with_emoji / total_sections

## Results

Results are stored in `./results/`:
- `raw/` - Claude output text files
- `metrics/` - JSON metrics per trial
- `charts/` - Generated visualizations
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Summary

**Plan complete and saved to `docs/plans/2025-12-15-claude-md-compliance-framework.md`.**

**12 tasks covering:**
1. Project scaffolding
2. Configuration data model
3. CLAUDE.md generator
4. Experiment file setup
5. Output analyzer
6. Claude runner
7. Metrics storage
8. CLI interface
9. Scale experiment config
10. Emphasis experiment config
11. Integration wiring
12. README documentation

**Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
