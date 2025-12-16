# CLAUDE.md Compliance Research

Empirical research measuring how well Claude follows CLAUDE.md instructions under various conditions.

## The Problem

I use CLAUDE.md files extensively and had questions:
- **How long can my instructions be** before Claude starts ignoring them?
- **Should I use one big CLAUDE.md** or split across nested directories?
- **Should I write detailed explanations** or keep instructions terse?

So I built a test framework and ran 150+ trials to find out.

## Key Findings

### 1. Context Size Limit (~80K chars)

Compliance drops sharply after ~80K total characters across all CLAUDE.md files:

| Total Context | Compliance |
|--------------|------------|
| ~4K chars | 100% ✅ |
| ~21K chars | 67% ⚠️ |
| ~42K chars | 67% ⚠️ |
| ~85K chars | 59% ⚠️ |
| ~128K chars | 0% ❌ |
| ~214K chars | 0% ❌ |

**Recommendation:** Keep total CLAUDE.md content under 80K characters.

### 2. Rule Count Is Not the Bottleneck

Claude can follow 200+ distinct rules with ~98% compliance when using terse instructions:

| Rules | Compliance |
|-------|------------|
| 10-80 | ~100% ✅ |
| 100-160 | ~100% ✅ |
| 200 | 98% ✅ |

**Recommendation:** Don't worry about having too many rules—worry about total size.

### 3. Terse Instructions Beat Verbose Explanations

Verbose explanations perform worse than single-sentence rules:

| Style | Example | Compliance |
|-------|---------|------------|
| Terse | `"Include 😀 in each section."` | **94.8%** |
| Verbose | `"When writing any section, you must include 😀. This is a firm requirement..."` | **86.6%** |

Verbose rules use 5x more context but achieve 8% *worse* compliance.

**Recommendation:** Use short, direct instructions. Don't over-explain.

### 4. Nesting Works Fine

4 levels of nested CLAUDE.md files (root → src → src/lib → src/lib/core) work well. The total size matters, not the nesting depth.

## Methodology

### Measurement Approach

Instead of asking Claude what instructions it sees (self-reporting), we measure **behavioral compliance**:

1. Each CLAUDE.md file contains emoji rules: `"Include 😀 in every section"`
2. Claude generates a 10-section story
3. Script counts emoji occurrences per section
4. Compliance = `sections_with_emoji / total_sections`

### Why Emojis?

- **Unambiguous:** Either present or not
- **Measurable:** Easy to count programmatically
- **Non-interfering:** Don't affect story quality
- **Distinct per level:** Easy to track which CLAUDE.md files are followed

### CLAUDE.md Hierarchy

Tests use 4 nested levels (level 0 skipped to avoid modifying user config):

| Level | Location | Emoji Pool |
|-------|----------|------------|
| 1 | `./CLAUDE.md` | Smileys 😀😃😄😁😆 |
| 2 | `./src/CLAUDE.md` | Animals 🐶🐱🐭🐹🐰 |
| 3 | `./src/lib/CLAUDE.md` | Food 🍎🍊🍋🍌🍉 |
| 4 | `./src/lib/core/CLAUDE.md` | Symbols ⭐🌟✨💫🔥 |

### Test Prompt

```
Write a story with 10 clearly separated sections.
Each section should be 2-3 sentences about any topic.
Number each section (Section 1, Section 2, etc.).
```

## Experiments

### Experiment 01: Context Size (`01-scale`)

**Question:** At what context size does compliance break down?

**Method:**
- Padding sizes: 1K, 5K, 10K, 20K, 30K, 50K chars per file
- 4 files = 4K to 200K total context
- 3 trials per condition
- Fixed 5 emojis per level (20 total)

**Key Finding:** Hard cliff between 85K-128K chars. Beyond that, Claude completely ignores instructions.

**Full analysis:** [results/01-scale-analysis.md](results/01-scale-analysis.md)

### Experiment 03: Rule Count (`03-rule-count`)

**Question:** How many distinct rules can Claude follow?

**Method:**
- Rule counts: 10, 20, 30... up to 200
- Terse single-sentence rules
- 3 trials per condition

**Key Finding:** 94.8% mean compliance. Rule count is not the limiting factor.

### Experiment 04: Verbosity (`04-verbose-rules`)

**Question:** Do detailed rule explanations improve compliance?

**Method:**
- Same rule counts as experiment 03
- Verbose 2-3 sentence explanations instead of terse rules
- 3 trials per condition

**Key Finding:** 86.6% mean compliance (-8.2% vs terse). Verbose hurts.

**Full comparison:** [results/03-04-rule-count-analysis.md](results/03-04-rule-count-analysis.md)

## Installation

```bash
git clone git@github.com:vtemian/claude-context.git
cd claude-context
uv sync
```

## Usage

### Run All Experiments

```bash
make experiments
```

### Run Individual Experiments

```bash
make run-01    # Context size (18 trials)
make run-03    # Rule count - terse (45 trials)
make run-04    # Rule count - verbose (45 trials)
```

### Analyze Results

```bash
make analyze      # All experiments
make analyze-01   # Just 01-scale
make analyze-03   # Just 03-rule-count
make analyze-04   # Just 04-verbose-rules
```

### Generate Charts

```bash
python scripts/generate_chart.py        # 01-scale chart
python scripts/generate_rule_charts.py  # 03 vs 04 comparison
```

### Custom Configuration

```bash
# Generate CLAUDE.md files with 10K padding per file
uv run claude-md-research generate -e 01-scale -p 10000 -o ./workspace

# Generate with 50 rules (terse)
uv run claude-md-research generate -e 03-rule-count -r 50 -o ./workspace

# Generate with 50 rules (verbose)
uv run claude-md-research generate -e 04-verbose-rules -r 50 -s verbose -o ./workspace


# Run a single trial
uv run claude-md-research run -e 01-scale -p 5000 -t 1 -w ./workspace
```

## Project Structure

```
claude-context/
├── experiments/           # Experiment configurations
│   ├── 01-scale/         # Context size experiment
│   ├── 03-rule-count/    # Terse rule count experiment
│   └── 04-verbose-rules/ # Verbose rule count experiment
├── results/
│   ├── metrics/          # JSON metrics per trial
│   ├── raw/              # Raw Claude output
│   ├── charts/           # Generated visualizations
│   ├── 01-scale-analysis.md
│   └── 03-04-rule-count-analysis.md
├── scripts/
│   ├── generate_chart.py
│   └── generate_rule_charts.py
├── src/claude_md_research/
│   ├── analyzer.py       # Output parsing & compliance calculation
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Experiment configuration
│   ├── generator.py      # CLAUDE.md content generation
│   ├── metrics.py        # Results storage
│   ├── runner.py         # Claude CLI execution
│   └── setup.py          # File structure setup
└── tests/
```

## Practical Recommendations

Based on 150+ trials:

1. **Keep total CLAUDE.md under 80K chars** - Compliance drops to 0% beyond ~128K
2. **Use terse instructions** - One sentence per rule, no explanations needed
3. **Don't repeat yourself** - Reinforcement wastes context without improving compliance
4. **Nesting is fine** - 4 levels work well, total size is what matters
5. **Many short rules > few long rules** - Same context budget, better results

### Example: Good CLAUDE.md

```markdown
# Code Style
- Use TypeScript strict mode
- Prefer const over let
- No any types

# Testing
- Write tests for new functions
- Use vitest for unit tests

# Git
- Commit messages: imperative mood
- No commits to main directly
```

### Example: Bad CLAUDE.md

```markdown
# Code Style Guidelines

When writing code in this project, it is extremely important that you always
use TypeScript's strict mode. This means you should enable all strict type
checking options in the tsconfig.json file. The reason for this is that strict
mode catches many common errors at compile time rather than runtime...

[300 more words of explanation]
```

## Results Data

All raw data is included in the repository:

- `results/metrics/*.json` - Structured metrics per trial
- `results/raw/*.txt` - Raw Claude output
- `results/charts/*.png` - Generated visualizations

## Contributing

PRs welcome! Ideas for future experiments:

- [ ] Rule positioning (start vs end of file)
- [ ] Rule conflicts (contradictory instructions)
- [ ] Different instruction types (formatting vs behavior)
- [ ] Model comparison (Sonnet vs Opus vs Haiku)
- [ ] Emphasis keywords (IMPORTANT, MUST, NEVER)

## Development

```bash
# Run tests
make test

# Lint
make lint

# Format
make format
```

## License

MIT
