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
