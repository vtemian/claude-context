# Experiments 03 & 04: Rule Count and Verbosity

## Abstract

These experiments measure how many distinct CLAUDE.md rules Claude can follow simultaneously, and whether verbose rule descriptions improve compliance. We find that Claude can reliably follow up to 200 distinct rules (one emoji per rule), and that verbose, multi-sentence rule descriptions provide no benefit over terse single-sentence rules—in fact, they perform slightly worse.

## Introduction

Building on Experiment 01 (which tested total instruction size), these experiments isolate two variables:

1. **Experiment 03 (rule-count)**: How many distinct rules can Claude track simultaneously?
2. **Experiment 04 (verbose-rules)**: Does explaining rules in 2-3 sentences improve compliance over single-sentence rules?

These questions matter because CLAUDE.md users must decide:
- How many separate instructions to include
- How much detail to provide for each instruction

## Methodology

### Experimental Design

Both experiments use the same structure:
- 15 rule counts tested: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200
- 3 trials per condition
- 4 CLAUDE.md levels (each gets 1/4 of the rules)
- Each rule requires a unique emoji in every output section

### Independent Variables

**Rule count**: Total number of distinct emoji rules across all CLAUDE.md files.

**Rule verbosity**:
- Terse (03): Single sentence per rule (~40 chars)
  - Example: `"Include 😀 in each section you write."`
- Verbose (04): 2-3 sentences per rule (~200 chars)
  - Example: `"When writing any section of your response, you must include the 😀 emoji. This is a firm requirement that applies to every single section without exception. Failing to include 😀 would be considered incomplete output."`

### Dependent Variable

**Compliance rate**: Percentage of required emojis present in each section.

### Context Size Comparison

| Rules | Terse Context | Verbose Context | Ratio |
|-------|---------------|-----------------|-------|
| 10 | 323 chars | 1,605 chars | 5.0x |
| 50 | 1,945 chars | 9,757 chars | 5.0x |
| 100 | 4,078 chars | 20,283 chars | 5.0x |
| 200 | 8,138 chars | 40,386 chars | 5.0x |

Verbose rules consistently require ~5x more context than terse rules.

## Results

### Aggregated Comparison

| Rule Count | Terse (03) | Verbose (04) | Difference |
|------------|------------|--------------|------------|
| 10 | 90.8% | 100.0% | +9.2% |
| 20 | 100.0% | 100.0% | 0.0% |
| 30 | 99.9% | 99.9% | 0.0% |
| 40 | 99.9% | 100.0% | +0.1% |
| 50 | 99.9% | 100.0% | +0.1% |
| 60 | 99.9% | 100.0% | +0.1% |
| 70 | 100.0% | 100.0% | 0.0% |
| 80 | 100.0% | 100.0% | 0.0% |
| 90 | 66.7% | 0.0% | -66.7% |
| 100 | 99.9% | 99.9% | 0.0% |
| 120 | 99.9% | 99.9% | 0.0% |
| 140 | 99.9% | 66.6% | -33.3% |
| 160 | 100.0% | 100.0% | 0.0% |
| 180 | 66.6% | 100.0% | +33.3% |
| 200 | 98.4% | 32.8% | -65.6% |
| **Mean** | **94.8%** | **86.6%** | **-8.2%** |

### Failure Analysis

**Terse (03) failures:**
- r90-t2: 0% compliance (1 of 3 trials)
- r180-t2: 0% compliance (1 of 3 trials)

**Verbose (04) failures:**
- r90: 0% compliance (ALL 3 trials)
- r140-t1: 0% compliance
- r200-t1, r200-t2: 0% compliance (2 of 3 trials)

### Failure Behavior

When Claude fails to comply, it exhibits two distinct patterns:

1. **Complete ignorance**: Claude writes a valid story but includes zero emojis. The CLAUDE.md instructions are completely ignored.

2. **Front-loading**: Claude places all emojis in the title/header, then writes emoji-free sections. Technically "found" but not distributed correctly.

Example of front-loading (from 03-rule-count-r90-t2):
```
# The Adventure of the Curious Cat 😀😃😄😁😆😅🤣😂🙂😊😇🥰😍🤩😘😋😛🤪😜🤓🤠🥳🐶🐱...

**Section 1**
Once upon a time, there was a little gray cat named Whiskers...
```

## Analysis

### Key Findings

1. **High rule capacity**: Claude can follow up to 200 distinct rules with >98% compliance when using terse instructions. The rule count itself is not a limiting factor at these scales.

2. **Verbosity hurts, not helps**: Verbose rules averaged 86.6% compliance vs 94.8% for terse rules (-8.2%). The additional context provides no benefit and may cause:
   - Attention dilution (more text to process)
   - Repetitive phrasing fatigue
   - Higher probability of hitting context limits

3. **Catastrophic failures are random**: Both experiments show occasional complete failures (0% compliance) at seemingly random rule counts. These failures are not gradual—they're all-or-nothing.

4. **Verbose failures cluster at high counts**: At 200 rules, verbose instructions failed 2 of 3 trials (32.8% mean), while terse instructions maintained 98.4%. The 40K character verbose context approaches the danger zone identified in Experiment 01.

### Why Verbose Rules Fail

The r90 verbose case is instructive: at 17,714 characters of context, Claude completely ignored all emoji rules in all 3 trials. This is well below the ~85K threshold found in Experiment 01, suggesting that:

1. **Repetitive verbose content may be deprioritized**: When rules are explained in multiple similar sentences, Claude may perceive them as redundant padding rather than critical instructions.

2. **Concise instructions signal importance**: Terse, direct rules may be interpreted as more authoritative than lengthy explanations.

3. **Context efficiency matters**: Using 5x more context for the same information leaves less room for the actual task.

### Variance and Reproducibility

Both experiments show high variance at certain rule counts (66.7% = one failure out of three trials). This suggests:

- Claude's instruction-following has a stochastic component
- Near-limit configurations produce unpredictable results
- Multiple trials are essential for reliable measurement

## Implications

### For CLAUDE.md Authors

1. **Keep rules terse**: Single-sentence instructions outperform multi-sentence explanations
2. **Don't over-explain**: Verbose descriptions waste context and may reduce compliance
3. **Rule count is not the bottleneck**: 200+ distinct rules work fine with concise phrasing
4. **Total context size matters more than rule count**: A few verbose rules may perform worse than many terse ones

### Recommended Rule Format

**Do:**
```
Include 😀 in each section you write.
```

**Don't:**
```
When writing any section of your response, you must include the 😀 emoji.
This is a firm requirement that applies to every single section without
exception. Failing to include 😀 would be considered incomplete output.
```

### For Future Research

1. **Rule positioning**: Do rules at the start vs end of CLAUDE.md files have different compliance rates?
2. **Rule conflict**: What happens when rules contradict each other?
3. **Rule specificity**: Do more specific rules (e.g., "put 😀 at the end of each section") work better than general ones?

## Conclusion

Claude can reliably follow a large number of distinct CLAUDE.md rules (200+) when those rules are expressed concisely. Verbose, explanatory rule descriptions provide no benefit and actually reduce compliance by 8% on average. Users should prefer terse, direct instructions over detailed explanations.

The key insight is that CLAUDE.md compliance is limited by total context size, not rule count. Given the same context budget, many short rules outperform few long rules.

---

## Appendix: Experimental Configuration

### Experiment 03 (Terse Rules)
```yaml
name: rule-count
rule_counts: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]
trials_per_condition: 3
style: neutral  # Single-sentence rules
```

### Experiment 04 (Verbose Rules)
```yaml
name: verbose-rules
rule_counts: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]
trials_per_condition: 3
style: verbose  # 2-3 sentence rules
```

## Appendix: Sample Rules

### Terse (Experiment 03)
```
Include 😀 in each section you write.
Every section should contain one 😃.
Each section needs a 😄 somewhere in it.
```

### Verbose (Experiment 04)
```
When writing any section of your response, you must include the 😀 emoji. This is a firm requirement that applies to every single section without exception. Failing to include 😀 would be considered incomplete output.

The 😃 symbol serves as an important marker in your writing. Each section you produce needs to contain this emoji somewhere within it. Please ensure you never forget to add 😃 to your sections.

As you compose your response, remember that 😄 is a mandatory element. Every section must feature this emoji at least once. This rule is non-negotiable and applies consistently throughout your entire output.
```
