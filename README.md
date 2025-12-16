# CLAUDE.md Compliance Research Framework

Empirically measure how well Claude follows CLAUDE.md instructions under various conditions.

## The Problem

Claude Code loads CLAUDE.md files from multiple locations and concatenates them into context. As context grows, instruction compliance may degrade. This framework measures that degradation scientifically.

## How It Works

### Measurement Approach

Instead of asking Claude what instructions it sees (self-reporting), we measure **behavioral compliance**:

1. Each CLAUDE.md level introduces a unique emoji requirement (e.g., "Include 😀 in every section")
2. Claude generates structured text output (story with numbered sections)
3. Python script counts emoji occurrences per section
4. Compliance rate = `sections_with_emoji / total_sections`

### CLAUDE.md Hierarchy

The framework creates nested CLAUDE.md files mimicking real-world usage:

| Level | Location | Emoji |
|-------|----------|-------|
| 0 | `~/.claude/CLAUDE.md` | 😀 |
| 1 | `./CLAUDE.md` | 😃 |
| 2 | `./src/CLAUDE.md` | 😄 |
| 3 | `./src/lib/CLAUDE.md` | 😁 |
| 4 | `./src/lib/core/CLAUDE.md` | 😆 |

## Installation

```bash
git clone git@github.com:vtemian/claude-context.git
cd claude-context
uv sync
```

## Quick Start

### 1. Preview Generated Files

Generate CLAUDE.md files without running Claude (safe - doesn't touch your `~/.claude/CLAUDE.md`):

```bash
uv run claude-md-research generate -e 01-scale -p 1000 -o ./workspace
```

This creates:
```
workspace/
├── CLAUDE.md           # Level 1: "Include 😃 in every section" + padding
├── src/
│   └── CLAUDE.md       # Level 2: "Include 😄 in every section" + padding
│   └── lib/
│       └── CLAUDE.md   # Level 3: ...
│       └── core/
│           └── CLAUDE.md  # Level 4: ...
```

### 2. Run an Experiment Trial

```bash
uv run claude-md-research run -e 01-scale -p 1000 -t 1 -o ./results
```

This:
1. Backs up your `~/.claude/CLAUDE.md`
2. Creates experiment files in a temp directory
3. Runs Claude Code with the standard prompt
4. Analyzes output for emoji compliance
5. Restores your original CLAUDE.md
6. Saves results to `./results/`

### 3. Analyze Results

```bash
uv run claude-md-research analyze -e 01-scale -i ./results
```

Output:
```
Experiment: 01-scale
Total trials: 5
Mean compliance: 72.3%
Range: 65.0% - 80.0%

By padding size:
   500 chars: 95.0%
  1000 chars: 85.0%
  2000 chars: 72.0%
  4000 chars: 58.0%
```

## CLI Reference

### `generate` - Create experiment files

```bash
uv run claude-md-research generate [OPTIONS]

Options:
  -e, --experiment TEXT   Experiment name (required)
  -o, --output TEXT       Output directory [default: ./workspace]
  -p, --padding INTEGER   Padding size in chars [default: 1000]
  -s, --style TEXT        Emphasis style: neutral|important|never|caps [default: neutral]
  --claude-padding        Use Claude API to generate varied padding
```

**Examples:**

```bash
# Basic generation with templates
uv run claude-md-research generate -e 01-scale -p 2000

# With IMPORTANT/MUST emphasis
uv run claude-md-research generate -e 02-emphasis -p 1000 -s important

# With Claude-generated padding (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-ant-... uv run claude-md-research generate -e 01-scale -p 1000 --claude-padding
```

### `run` - Execute a trial

```bash
uv run claude-md-research run [OPTIONS]

Options:
  -e, --experiment TEXT   Experiment name (required)
  -p, --padding INTEGER   Padding size (required)
  -t, --trial INTEGER     Trial number [default: 1]
  -o, --output TEXT       Results directory [default: ./results]
  --timeout INTEGER       Timeout in seconds [default: 60]
  -s, --style TEXT        Emphasis style [default: neutral]
  --claude-padding        Use Claude API for padding
```

**Examples:**

```bash
# Run single trial
uv run claude-md-research run -e 01-scale -p 1000 -t 1

# Run multiple trials at different padding sizes
for p in 500 1000 2000 4000; do
  for t in 1 2 3; do
    uv run claude-md-research run -e 01-scale -p $p -t $t
  done
done
```

### `analyze` - Aggregate results

```bash
uv run claude-md-research analyze [OPTIONS]

Options:
  -e, --experiment TEXT   Experiment name (required)
  -i, --input TEXT        Results directory [default: ./results]
```

## Experiments

### 01-scale: Context Size vs Compliance

**Hypothesis:** Compliance degrades as context size increases.

**Variables:**
- Padding per CLAUDE.md: 100, 500, 1000, 2000, 4000, 8000 chars

**Run:**
```bash
for p in 100 500 1000 2000 4000 8000; do
  uv run claude-md-research run -e 01-scale -p $p -t 1
done
uv run claude-md-research analyze -e 01-scale
```

### 02-emphasis: Keyword Effectiveness

**Hypothesis:** Keywords like IMPORTANT, NEVER, MUST improve compliance.

**Variables:**
- Styles: neutral, important, never, caps

**Run:**
```bash
for s in neutral important never caps; do
  uv run claude-md-research run -e 02-emphasis -p 1000 -t 1 -s $s
done
```

## Padding Generation

### Template-based (default)

Uses 15 pre-written variations that cycle:

```
Remember to include 😀 in every section.
The 😀 symbol is required in all paragraphs.
Do not forget: 😀 must appear in each section.
...
```

Pros: Deterministic, reproducible
Cons: Repetitive at large padding sizes

### Claude API-based (`--claude-padding`)

Uses Claude Haiku to generate unique phrasings:

```bash
ANTHROPIC_API_KEY=sk-ant-... uv run claude-md-research generate -e 01-scale -p 2000 --claude-padding
```

Pros: Natural variation, no repetition
Cons: Non-deterministic, API cost, potential confound (Claude writing instructions Claude follows)

## Results Structure

```
results/
├── raw/                    # Claude output captures
│   ├── 01-scale-p1000-t1.txt
│   └── 01-scale-p2000-t1.txt
├── metrics/                # JSON metrics per trial
│   ├── 01-scale-p1000-t1.json
│   └── 01-scale-p2000-t1.json
└── charts/                 # Generated visualizations (future)
```

### Metrics JSON Format

```json
{
  "trial_id": "01-scale-p1000-t1",
  "experiment": "01-scale",
  "parameters": {"padding_size": 1000, "style": "neutral"},
  "sections_found": 10,
  "compliance_rates": {
    "😀": 1.0,
    "😃": 0.9,
    "😄": 0.8,
    "😁": 0.6,
    "😆": 0.5
  },
  "overall_compliance": 0.76,
  "context_size_chars": 5240
}
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest -v

# Format code
uv run ruff format .
```

## Adding New Experiments

1. Create `experiments/<name>/config.yaml`:

```yaml
name: my-experiment
description: Test something new
levels: 5
emojis: ["😀", "😃", "😄", "😁", "😆"]
padding_sizes: [500, 1000, 2000]
trials_per_condition: 3
prompt: |
  Write a story with 10 clearly separated sections.
  Each section should be 2-3 sentences.
  Number each section (Section 1, Section 2, etc.)
```

2. Run:
```bash
uv run claude-md-research run -e my-experiment -p 1000 -t 1
```

## License

MIT
