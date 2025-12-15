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
    # Should contain at least one emphasis keyword from important templates
    assert any(keyword in text for keyword in ["IMPORTANT", "CRITICAL", "REQUIRED", "MUST"])


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
    # Should contain at least one emphasis keyword from important templates
    assert any(keyword in content for keyword in ["IMPORTANT", "CRITICAL", "REQUIRED", "MUST"])
    assert len(content) >= 150
