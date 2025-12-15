# CLAUDE.md Compliance Research Framework

Empirically measure how well Claude follows CLAUDE.md instructions under various conditions.

## Installation

```bash
uv sync
```

## Quick Start

```bash
# Generate experiment files
uv run claude-md-research generate -e 01-scale -o ./workspace -p 1000

# Run a trial
uv run claude-md-research run -e 01-scale -p 1000 -t 1 -o ./results

# Analyze results
uv run claude-md-research analyze -e 01-scale -i ./results
```

## Experiments

- **01-scale**: Context size vs compliance
- **02-emphasis**: Keyword effectiveness (IMPORTANT, NEVER, etc.)

## How It Works

1. Each CLAUDE.md level introduces a unique emoji requirement
2. Claude generates a story with numbered sections
3. Python script counts emoji occurrences per section
4. Compliance rate = sections_with_emoji / total_sections

## Results

Results are stored in `./results/`:
- `raw/` - Claude output text files
- `metrics/` - JSON metrics per trial
- `charts/` - Generated visualizations
