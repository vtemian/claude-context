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
