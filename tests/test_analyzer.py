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
