import os
import pytest
from unittest.mock import Mock, patch
from claude_md_research.generator import (
    generate_rule_text,
    generate_reinforcement_padding,
    generate_claude_md_content,
    generate_padding_via_claude,
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


def test_generate_padding_via_claude_mocked():
    """Test Claude API padding generation with mocked response."""
    mock_response = Mock()
    mock_response.content = [Mock(text="""Include 😀 in every section you write.
Each paragraph must contain the 😀 emoji.
Never forget to add 😀 to your sections.
The 😀 symbol is required throughout.""")]

    with patch("claude_md_research.generator.anthropic.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        result = generate_padding_via_claude("😀", target_chars=200)

        assert "😀" in result
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "😀" in call_kwargs["messages"][0]["content"]
        assert call_kwargs["model"] == "claude-3-5-haiku-20241022"


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
def test_generate_padding_via_claude_integration():
    """Integration test with real API - only runs if API key is set."""
    result = generate_padding_via_claude("🎯", target_chars=300)

    assert "🎯" in result
    assert len(result) >= 200  # Allow some variance
    # Should have multiple lines
    assert result.count("\n") >= 2
