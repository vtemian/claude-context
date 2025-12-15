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
