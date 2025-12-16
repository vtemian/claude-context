"""Generate CLAUDE.md content with configurable rules and padding."""

import random
import anthropic

# Emoji pools by level - each CLAUDE.md level gets its own distinct pool
# This makes it easy to track which level's rules are being followed
EMOJI_POOLS = {
    # Level 1 (project root): Smileys & faces
    1: [
        "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "😊",
        "😇", "🥰", "😍", "🤩", "😘", "😋", "😛", "🤪", "😜", "🤓",
        "🤠", "🥳", "🥸", "😎", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨",
        "😏", "😒", "🙄", "😬", "😮", "🤤", "😴", "🤒", "🤕", "🤢",
        "🤮", "🤧", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳", "🥸",
    ],
    # Level 2 (src/): Animals
    2: [
        "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
        "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🐤", "🦆",
        "🦅", "🦉", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋",
        "🐌", "🐞", "🐜", "🦟", "🦗", "🕷️", "🦂", "🐢", "🐍", "🦎",
        "🦖", "🦕", "🐙", "🦑", "🦐", "🦞", "🦀", "🐡", "🐠", "🐟",
        "🐬", "🐳", "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧",
        "🐘", "🦛", "🦏", "🐪", "🐫", "🦒", "🦘", "🦬", "🐃", "🐂",
    ],
    # Level 3 (src/lib/): Food & plants
    3: [
        "🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🍒", "🍑", "🥭",
        "🍍", "🥥", "🥝", "🍅", "🥑", "🥦", "🥬", "🥒", "🌶️", "🌽",
        "🥕", "🧄", "🧅", "🥔", "🍠", "🥐", "🥯", "🍞", "🥖", "🥨",
        "🧀", "🥚", "🍳", "🧈", "🥞", "🧇", "🥓", "🥩", "🍗", "🍖",
        "🌭", "🍔", "🍟", "🍕", "🫓", "🥪", "🥙", "🧆", "🌮", "🌯",
        "🫔", "🥗", "🥘", "🫕", "🍝", "🍜", "🍲", "🍛", "🍣", "🍱",
        "🥟", "🦪", "🍤", "🍙", "🍚", "🍘", "🍥", "🥠", "🥮", "🍢",
        "🍡", "🍧", "🍨", "🍦", "🥧", "🧁", "🍰", "🎂", "🍮", "🍭",
        "🍬", "🍫", "🍿", "🍩", "🍪", "🌰", "🥜", "🍯", "🥛", "🍼",
        "🫖", "☕", "🍵", "🧃", "🥤", "🧋", "🍶", "🍺", "🍻", "🥂",
    ],
    # Level 4 (src/lib/core/): Symbols & objects
    4: [
        "⭐", "🌟", "✨", "💫", "🔥", "💡", "📌", "📍", "🎯", "🎪",
        "🎨", "🎭", "🎬", "🎤", "🎧", "🎵", "🎶", "🎹", "🎸", "🎺",
        "✅", "❌", "⚡", "💥", "💢", "💦", "💨", "🕐", "🔔", "🔕",
        "📢", "📣", "💬", "💭", "♠️", "♣️", "♥️", "♦️", "🃏", "🎴",
        "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🔶",
        "🔷", "🔸", "🔹", "▪️", "▫️", "◾", "◽", "🔲", "🔳", "⬛",
        "⬜", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "💠", "🔘",
        "🎁", "🎀", "🎊", "🎉", "🎈", "🧸", "🎮", "🕹️", "🎲", "🧩",
        "♟️", "🎰", "🎳", "🔮", "🧿", "🪬", "🖼️", "🧵", "🧶", "👑",
        "💎", "💍", "🏆", "🥇", "🥈", "🥉", "🏅", "🎖️", "📿", "🔑",
    ],
}

# Flat pool for backward compatibility
EMOJI_POOL = EMOJI_POOLS[1] + EMOJI_POOLS[2] + EMOJI_POOLS[3] + EMOJI_POOLS[4]

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
    "verbose": [
        "When writing any section of your response, you must include the {emoji} emoji. This is a firm requirement that applies to every single section without exception. Failing to include {emoji} would be considered incomplete output.",
        "The {emoji} symbol serves as an important marker in your writing. Each section you produce needs to contain this emoji somewhere within it. Please ensure you never forget to add {emoji} to your sections.",
        "As you compose your response, remember that {emoji} is a mandatory element. Every section must feature this emoji at least once. This rule is non-negotiable and applies consistently throughout your entire output.",
        "Your output quality depends on consistent use of {emoji} in all sections. Make it a habit to include this emoji in every paragraph you write. Double-check each section to verify {emoji} is present before moving on.",
        "The presence of {emoji} in each section is crucial for this task. Without {emoji}, a section is considered incomplete and invalid. Always verify that you have included {emoji} before finishing any section.",
        "Think of {emoji} as a signature that must appear in every section. Just as you would sign each page of an important document, you must place {emoji} in each section. This ensures consistency and completeness.",
        "Including {emoji} is not optional - it is a core requirement. Every section of your response must contain this emoji to be considered valid. Treat the absence of {emoji} as a critical error to avoid.",
        "Before submitting any section, ask yourself: does this contain {emoji}? If the answer is no, you must add it. This simple check will ensure you meet the requirement of having {emoji} in all sections.",
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


def generate_diverse_emoji_rules(
    level: int,
    target_chars: int,
    style: str = "neutral",
) -> tuple[str, list[str]]:
    """Generate rules for many different emojis from a level's pool.

    Args:
        level: CLAUDE.md level (1-4) to get emoji pool from
        target_chars: Target character count for all rules combined
        style: Instruction style

    Returns:
        Tuple of (rules_text, list_of_emojis_used)
    """
    pool = EMOJI_POOLS.get(level, EMOJI_POOL)
    templates = RULE_TEMPLATES.get(style, RULE_TEMPLATES["neutral"]) + REINFORCEMENT_TEMPLATES

    lines = []
    emojis_used = []
    current_chars = 0
    emoji_index = 0

    # Shuffle pool for variety
    shuffled_pool = pool.copy()
    random.shuffle(shuffled_pool)

    while current_chars < target_chars and emoji_index < len(shuffled_pool):
        emoji = shuffled_pool[emoji_index]
        emojis_used.append(emoji)

        # Generate multiple rules for this emoji
        emoji_templates = templates.copy()
        random.shuffle(emoji_templates)

        for template in emoji_templates[:3]:  # 3 rules per emoji
            if current_chars >= target_chars:
                break
            line = template.format(emoji=emoji)
            lines.append(line)
            current_chars += len(line) + 1

        emoji_index += 1

    return "\n".join(lines), emojis_used


def generate_padding_via_claude(
    emojis: list[str],
    target_chars: int,
    style: str = "neutral",
    model: str = "claude-haiku-4-5-20251001",
) -> str:
    """Generate diverse emoji rules using Claude API.

    Args:
        emojis: List of emojis to create rules for
        target_chars: Approximate target character count
        style: Instruction style (neutral, important, never, caps)
        model: Claude model to use (default: Haiku 4.5 for cost efficiency)

    Returns:
        Generated instruction text with rules for all emojis
    """
    style_guidance = {
        "neutral": "conversational and clear",
        "important": "emphatic with words like IMPORTANT, MUST, CRITICAL",
        "never": "using negative framing like NEVER, DO NOT, FORBIDDEN",
        "caps": "ALL CAPS for emphasis",
    }

    tone = style_guidance.get(style, style_guidance["neutral"])
    emoji_list = " ".join(emojis)

    # Haiku 4.5 supports 64K output tokens (~256K chars)
    max_tokens = min(target_chars // 4 + 500, 64000)

    prompt = f"""Generate approximately {target_chars} characters of instructions telling someone to include specific emojis in every section they write.

The emojis to include are: {emoji_list}

Requirements:
- Create rules for EACH of these emojis: {emoji_list}
- Each line should be a separate instruction about ONE emoji
- Use varied phrasing - don't repeat the same sentence structure
- Tone should be {tone}
- Distribute rules across all emojis (don't focus on just a few)
- Output ONLY the instructions, no preamble or explanation

Example format:
Include 😀 in every section.
Each paragraph needs 🐶 without exception.
Never forget to add 🍎 to your writing.
The ⭐ emoji must appear in all sections."""

    client = anthropic.Anthropic()

    # Use streaming for large requests to avoid timeout errors
    result_text = ""
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            result_text += text

    return result_text


def generate_claude_md_content(
    level: int,
    padding_size: int | None = None,
    num_rules: int | None = None,
    max_emojis: int = 5,
    style: str = "neutral",
    use_claude_padding: bool = False,
) -> tuple[str, list[str]]:
    """Generate complete CLAUDE.md content for one level.

    Args:
        level: CLAUDE.md level (1-4) to get emoji pool from
        padding_size: Target size in characters for rules
        num_rules: Exact number of rules/emojis to generate (overrides padding_size)
        max_emojis: Maximum emojis per level for padding mode (default 5)
        style: Instruction style (neutral, important, never, caps)
        use_claude_padding: If True, use Claude API to generate varied rules

    Returns:
        Tuple of (content, list_of_emojis_used)
    """
    pool = EMOJI_POOLS.get(level, EMOJI_POOL)

    # Mode 1: Fixed number of rules (one rule per emoji)
    if num_rules is not None:
        num_emojis = min(num_rules, len(pool))
        emojis = pool[:num_emojis]
        # Generate exactly one rule per emoji
        lines = []
        templates = RULE_TEMPLATES.get(style, RULE_TEMPLATES["neutral"])
        for emoji in emojis:
            template = random.choice(templates)
            lines.append(template.format(emoji=emoji))
        return "\n".join(lines), emojis

    # Mode 2: Padding-based (fixed emoji count, variable reinforcement)
    if padding_size is None or padding_size <= 0:
        # Minimal content: just one rule with first emoji
        emoji = pool[0]
        content = generate_rule_text(emoji, style)
        return content, [emoji]

    # Use fixed number of emojis, fill padding with reinforcement
    num_emojis = min(max_emojis, len(pool))
    emojis = pool[:num_emojis]

    if use_claude_padding:
        content = generate_padding_via_claude(emojis, padding_size, style)
        content = _adjust_content_size(content, emojis, padding_size, style)
    else:
        content = _generate_reinforced_rules(emojis, padding_size, style)

    return content, emojis


def _generate_reinforced_rules(
    emojis: list[str],
    target_chars: int,
    style: str = "neutral",
) -> str:
    """Generate rules for fixed emojis, filling target size with reinforcement."""
    templates = RULE_TEMPLATES.get(style, RULE_TEMPLATES["neutral"]) + REINFORCEMENT_TEMPLATES

    lines = []
    current_chars = 0
    template_idx = 0
    emoji_idx = 0

    # Shuffle templates for variety
    shuffled_templates = templates.copy()
    random.shuffle(shuffled_templates)

    while current_chars < target_chars:
        emoji = emojis[emoji_idx % len(emojis)]
        template = shuffled_templates[template_idx % len(shuffled_templates)]
        line = template.format(emoji=emoji)
        lines.append(line)
        current_chars += len(line) + 1
        template_idx += 1
        emoji_idx += 1

    return "\n".join(lines)


def _adjust_content_size(
    content: str,
    emojis: list[str],
    target_size: int,
    style: str,
) -> str:
    """Adjust content to be close to target size by truncating or padding."""
    tolerance = 0.1  # 10% tolerance

    if len(content) > target_size * (1 + tolerance):
        # Truncate to target size at a line boundary
        lines = content.split("\n")
        truncated = []
        current_size = 0
        for line in lines:
            if current_size + len(line) + 1 > target_size:
                break
            truncated.append(line)
            current_size += len(line) + 1
        content = "\n".join(truncated)

    elif len(content) < target_size * (1 - tolerance):
        # Pad with template-based rules
        remaining = target_size - len(content) - 2
        if remaining > 0 and emojis:
            templates = REINFORCEMENT_TEMPLATES.copy()
            random.shuffle(templates)
            padding_lines = []
            chars = 0
            template_idx = 0
            emoji_idx = 0
            while chars < remaining:
                emoji = emojis[emoji_idx % len(emojis)]
                template = templates[template_idx % len(templates)]
                line = template.format(emoji=emoji)
                padding_lines.append(line)
                chars += len(line) + 1
                template_idx += 1
                emoji_idx += 1
            content = content + "\n\n" + "\n".join(padding_lines)

    return content
