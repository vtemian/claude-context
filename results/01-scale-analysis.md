# Experiment 01: CLAUDE.md Instruction Compliance vs Context Size

## Abstract

This experiment measures how Claude's compliance with CLAUDE.md instructions degrades as the size of those instructions increases. We find a critical threshold around 80,000-130,000 characters of total CLAUDE.md context, beyond which compliance drops to zero. This has significant implications for users relying on extensive CLAUDE.md configurations.

## Introduction

Claude Code loads CLAUDE.md files from multiple locations in a hierarchical structure:
- `~/.claude/CLAUDE.md` (user-level, applies to all projects)
- `./CLAUDE.md` (project root)
- `./src/CLAUDE.md` (subdirectory)
- `./src/lib/CLAUDE.md` (nested subdirectory)
- And so on...

These files contain instructions that Claude is expected to follow during interactions. A natural question arises: **How much instruction content can Claude reliably process and follow?**

This experiment systematically varies the size of CLAUDE.md content to identify the threshold at which instruction-following breaks down.

## Methodology

### Experimental Design

We use emoji inclusion as a measurable proxy for instruction compliance. Each CLAUDE.md file contains rules requiring specific emojis to appear in every section of Claude's output.

**Key design choice**: We use a fixed number of emojis (5 per level, 20 total across 4 levels) with variable reinforcement. This avoids conflating "number of distinct rules" with "total instruction size" - the latter is what this experiment measures.

### Independent Variable

**Padding size per file**: 1,000 / 5,000 / 10,000 / 20,000 / 30,000 / 50,000 characters

This translates to total context sizes of approximately 4K to 214K characters across all 4 CLAUDE.md files.

### Dependent Variable

**Compliance rate**: Percentage of required emojis that appear in each section of Claude's output.

### Procedure

1. Generate 4 CLAUDE.md files (levels 1-4) with the specified padding size
2. Each file contains 5 emoji rules from distinct pools:
   - Level 1 (root): Smileys (😀😃😄😁😆)
   - Level 2 (src): Animals (🐶🐱🐭🐹🐰)
   - Level 3 (src/lib): Food (🍎🍊🍋🍌🍉)
   - Level 4 (src/lib/core): Symbols (⭐🌟✨💫🔥)
3. Padding is filled with varied reinforcement of the same rules
4. Prompt Claude: "Write a story with 10 clearly separated sections"
5. Analyze output for emoji presence in each section
6. Repeat 3 trials per condition

### Example Rule Content

```
Every section should contain one 😀.
Include 😃 in each section you write.
Remember to include 😀 in every section.
The 😃 symbol is required in all paragraphs.
Do not forget: 😄 must appear in each section.
... (repeated with variations to reach target size)
```

## Results

### Raw Data

| Trial ID | Padding/File | Total Context | Sections Found | Compliance |
|----------|-------------|---------------|----------------|------------|
| 01-scale-p1000-t1 | 1,000 | 4,177 | 10 | 100.0% |
| 01-scale-p1000-t2 | 1,000 | 4,177 | 10 | 100.0% |
| 01-scale-p1000-t3 | 1,000 | 4,177 | 10 | 100.0% |
| 01-scale-p5000-t1 | 5,000 | 21,421 | 10 | 0.0% |
| 01-scale-p5000-t2 | 5,000 | 21,421 | 10 | 100.0% |
| 01-scale-p5000-t3 | 5,000 | 21,421 | 10 | 100.0% |
| 01-scale-p10000-t1 | 10,000 | 41,614 | 10 | 0.0% |
| 01-scale-p10000-t2 | 10,000 | 41,614 | 10 | 100.0% |
| 01-scale-p10000-t3 | 10,000 | 41,614 | 10 | 100.0% |
| 01-scale-p20000-t1 | 20,000 | 84,839 | 10 | 77.5% |
| 01-scale-p20000-t2 | 20,000 | 84,839 | 10 | 100.0% |
| 01-scale-p20000-t3 | 20,000 | 84,839 | 10 | 0.0% |
| 01-scale-p30000-t1 | 30,000 | 127,812 | 10 | 0.0% |
| 01-scale-p30000-t2 | 30,000 | 127,812 | 10 | 0.0% |
| 01-scale-p30000-t3 | 30,000 | 127,812 | 10 | 0.0% |
| 01-scale-p50000-t1 | 50,000 | 214,029 | 4 | 0.0% |
| 01-scale-p50000-t2 | 50,000 | 214,029 | 0 | 0.0% |
| 01-scale-p50000-t3 | 50,000 | 214,029 | 10 | 0.0% |

### Aggregated Results

| Padding/File | Total Context | Mean Compliance | Std Dev | Notes |
|-------------|---------------|-----------------|---------|-------|
| 1K | ~4K | 100.0% | 0.0% | Perfect compliance |
| 5K | ~21K | 66.7% | 47.1% | High variance (0%, 100%, 100%) |
| 10K | ~42K | 66.7% | 47.1% | High variance (0%, 100%, 100%) |
| 20K | ~85K | 59.2% | 43.8% | Degrading, high variance |
| 30K | ~128K | 0.0% | 0.0% | Complete failure |
| 50K | ~214K | 0.0% | 0.0% | Complete failure, task degradation |

## Analysis

### Key Findings

1. **Critical Threshold**: Compliance drops to zero between 85K and 128K characters of total CLAUDE.md content.

2. **High Variance in Transition Zone**: Between 21K-85K characters, compliance is highly variable (0% or 100% within the same condition). This suggests Claude is near a capacity limit where small variations in processing determine success or failure.

3. **All-or-Nothing Behavior**: Trials tend to show either complete compliance (100%) or complete failure (0%), with partial compliance (77.5%) being rare. This binary pattern suggests a threshold effect rather than gradual degradation.

4. **Task Degradation at Extreme Sizes**: At 214K characters, Claude sometimes fails to produce the requested 10 sections (producing 0 or 4 instead), indicating the instruction overload affects not just rule-following but basic task comprehension.

### Interpretation

The results suggest that Claude's instruction-following capacity has a soft limit around 85K-128K characters of CLAUDE.md content. Beyond this:

- **Attention dilution**: With too many instructions, none receive sufficient attention
- **Context competition**: The CLAUDE.md instructions compete with the actual task prompt
- **Threshold collapse**: Rather than graceful degradation, the system exhibits catastrophic failure

### Limitations

1. **Emoji proxy**: Using emoji inclusion as a compliance measure may not generalize to all instruction types
2. **Repetitive content**: The padding consists of repetitive rule variations, which may be processed differently than diverse instructions
3. **Single model**: Results are specific to Claude's current architecture and may change with updates
4. **Limited trials**: 3 trials per condition provides limited statistical power for the high-variance middle range

## Implications

### For CLAUDE.md Users

1. **Keep instructions concise**: Total CLAUDE.md content across all files should stay well under 80K characters
2. **Prioritize critical rules**: Place the most important instructions prominently; avoid burying them in lengthy context
3. **Avoid redundant reinforcement**: Excessive repetition of the same rule does not improve compliance and may harm it

### For Future Research

1. **Instruction diversity**: Does compliance differ for many distinct rules vs. few rules with reinforcement?
2. **Rule positioning**: Are rules at the beginning, middle, or end of CLAUDE.md files followed more reliably?
3. **Instruction type**: Do different types of instructions (formatting, content, behavior) have different compliance curves?

## Conclusion

CLAUDE.md instruction compliance degrades significantly beyond approximately 80,000 characters of total instruction content, with complete failure observed at 128,000+ characters. Users should keep their CLAUDE.md configurations well within these limits to ensure reliable instruction-following.

The high variance observed in the transition zone (21K-85K characters) suggests that near-limit configurations may produce unpredictable behavior, making conservative sizing even more important for production use cases.

---

## Appendix: Experimental Configuration

```yaml
# experiments/01-scale/config.yaml
name: scale
levels: 5
emojis: ["😀", "😃", "😄", "😁", "😆"]
padding_sizes: [1000, 5000, 10000, 20000, 30000, 50000]
trials_per_condition: 3
prompt: |
  Write a story with 10 clearly separated sections.
  Each section should be 2-3 sentences about any topic.
  Number each section (Section 1, Section 2, etc.).
```

## Appendix: File Structure

```
workspace/01-scale-p{size}/
├── CLAUDE.md                    # Level 1 (root)
├── src/
│   ├── CLAUDE.md               # Level 2
│   └── lib/
│       ├── CLAUDE.md           # Level 3
│       └── core/
│           └── CLAUDE.md       # Level 4
└── .emojis_manifest.json       # Tracks emojis per level
```

## Appendix: Compliance Calculation

For each section in Claude's output:
1. Check if ALL 20 required emojis (5 per level × 4 levels) are present
2. Section compliance = (emojis found / 20)
3. Overall compliance = mean(section compliance across all sections)

A trial with 10 sections where each section contains all 20 emojis scores 100%.
A trial where no emojis appear in any section scores 0%.
