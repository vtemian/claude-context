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
