import os
import pytest
from unittest.mock import Mock, patch
from claude_md_research.generator import (
    generate_rule_text,
    generate_reinforcement_padding,
    generate_claude_md_content,
    generate_padding_via_claude,
    generate_diverse_emoji_rules,
    EMOJI_POOLS,
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


def test_generate_diverse_emoji_rules():
    """Test diverse emoji rules generation."""
    content, emojis = generate_diverse_emoji_rules(level=1, target_chars=500)

    # Should have multiple emojis
    assert len(emojis) > 1
    # All emojis should be from level 1 pool
    for emoji in emojis:
        assert emoji in EMOJI_POOLS[1]
    # Content should contain all emojis
    for emoji in emojis:
        assert emoji in content


def test_generate_claude_md_content():
    """Test content generation returns tuple of (content, emojis)."""
    content, emojis = generate_claude_md_content(
        level=1,
        padding_size=500,
        style="important",
    )

    # Should return emojis from level 1 pool
    assert len(emojis) > 0
    for emoji in emojis:
        assert emoji in EMOJI_POOLS[1]

    # Content should mention at least some emojis
    assert any(emoji in content for emoji in emojis)
    assert len(content) >= 400


def test_generate_claude_md_content_minimal():
    """Test minimal content with no padding."""
    content, emojis = generate_claude_md_content(level=2, padding_size=0)

    # Should return single emoji with minimal rule
    assert len(emojis) == 1
    assert emojis[0] in EMOJI_POOLS[2]
    assert emojis[0] in content


def test_generate_padding_via_claude_mocked():
    """Test Claude API padding generation with mocked streaming response."""
    mock_text = """Include 😀 in every section you write.
Each paragraph must contain the 🐶 emoji.
Never forget to add 🍎 to your sections.
The ⭐ symbol is required throughout."""

    with patch("claude_md_research.generator.anthropic.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_stream = Mock()
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=False)
        mock_stream.text_stream = iter([mock_text])
        mock_client.messages.stream.return_value = mock_stream
        mock_anthropic.return_value = mock_client

        emojis = ["😀", "🐶", "🍎", "⭐"]
        result = generate_padding_via_claude(emojis, target_chars=200)

        assert any(e in result for e in emojis)
        mock_client.messages.stream.assert_called_once()
        call_kwargs = mock_client.messages.stream.call_args[1]
        # Should mention all emojis in prompt
        prompt = call_kwargs["messages"][0]["content"]
        for emoji in emojis:
            assert emoji in prompt
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
def test_generate_padding_via_claude_integration():
    """Integration test with real API - only runs if API key is set."""
    emojis = ["🎯", "🔥", "⭐"]
    result = generate_padding_via_claude(emojis, target_chars=300)

    # Should contain at least some of the emojis
    assert any(e in result for e in emojis)
    assert len(result) >= 200  # Allow some variance
    # Should have multiple lines
    assert result.count("\n") >= 2
