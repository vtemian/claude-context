"""Generate CLAUDE.md content with configurable rules and padding."""

import random
import anthropic

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
    """Generate padding text that reinforces the emoji rule using templates."""
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


def generate_padding_via_claude(
    emoji: str,
    target_chars: int,
    style: str = "neutral",
    model: str = "claude-3-5-haiku-20241022",
) -> str:
    """Generate padding text using Claude API for more natural variation.

    Args:
        emoji: The emoji to include in instructions
        target_chars: Approximate target character count
        style: Instruction style (neutral, important, never, caps)
        model: Claude model to use (default: haiku for cost efficiency)

    Returns:
        Generated instruction text containing the emoji
    """
    style_guidance = {
        "neutral": "conversational and clear",
        "important": "emphatic with words like IMPORTANT, MUST, CRITICAL",
        "never": "using negative framing like NEVER, DO NOT, FORBIDDEN",
        "caps": "ALL CAPS for emphasis",
    }

    tone = style_guidance.get(style, style_guidance["neutral"])

    prompt = f"""Generate approximately {target_chars} characters of instructions telling someone to include the {emoji} emoji in every section they write.

Requirements:
- Each line should be a separate instruction
- Use varied phrasing - don't repeat the same sentence structure
- Tone should be {tone}
- Every line must mention {emoji}
- Output ONLY the instructions, no preamble or explanation

Example format:
Include {emoji} in every section.
Each paragraph needs {emoji} without exception.
Never forget to add {emoji} to your writing."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def generate_claude_md_content(
    emoji: str,
    padding_size: int = 0,
    style: str = "neutral",
    use_claude_padding: bool = False,
) -> str:
    """Generate complete CLAUDE.md content for one level.

    Args:
        emoji: The emoji to require in sections
        padding_size: Target size in characters for padding
        style: Instruction style (neutral, important, never, caps)
        use_claude_padding: If True, use Claude API to generate varied padding
    """
    parts = []

    # Primary rule
    rule = generate_rule_text(emoji, style)
    parts.append(rule)

    # Padding (reinforcement)
    if padding_size > 0:
        # Account for the rule we already added
        remaining = padding_size - len(rule) - 2
        if remaining > 0:
            if use_claude_padding:
                padding = generate_padding_via_claude(emoji, remaining, style)
            else:
                padding = generate_reinforcement_padding(emoji, remaining)
            parts.append(padding)

    return "\n\n".join(parts)
