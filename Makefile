.PHONY: install test lint format clean help
.PHONY: experiments run-01 run-02 run-03 analyze analyze-01 analyze-02 analyze-03

# Development targets
install:
	uv sync

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/

help:
	@echo "CLAUDE.md Compliance Research Framework"
	@echo ""
	@echo "Development:"
	@echo "  make install        Install dependencies"
	@echo "  make test           Run tests"
	@echo "  make lint           Check code style"
	@echo "  make format         Format code"
	@echo ""
	@echo "Experiments:"
	@echo "  make experiments    Run all experiments"
	@echo "  make run-01         Run 01-scale (6 padding sizes × 3 trials)"
	@echo "  make run-02         Run 02-emphasis (5 styles × 5 trials)"
	@echo "  make run-03         Run 03-rule-count (15 rule counts × 3 trials)"
	@echo ""
	@echo "Analysis:"
	@echo "  make analyze        Analyze all experiments"
	@echo "  make analyze-01     Analyze 01-scale"
	@echo "  make analyze-02     Analyze 02-emphasis"
	@echo "  make analyze-03     Analyze 03-rule-count"
	@echo ""
	@echo "  make clean          Remove workspace and results"

# Experiment configuration
# Max ~50K per file × 4 files = 200K total context (within Claude's limit)
PADDING_SIZES := 1000 5000 10000 20000 30000 50000
TRIALS_01 := 1 2 3
STYLES := neutral important never caps bold
TRIALS_02 := 1 2 3 4 5
RULE_COUNTS := 10 20 30 40 50 60 70 80 90 100 120 140 160 180 200
TRIALS_03 := 1 2 3

# Run all experiments
experiments: run-01 run-02 run-03 analyze

# 01-scale: Test compliance vs context size (6 padding sizes × 3 trials = 18 runs)
run-01:
	@echo "=== Running 01-scale experiment (6 padding sizes × 3 trials) ==="
	@for padding in $(PADDING_SIZES); do \
		echo ""; \
		echo "=== Padding: $$padding chars ==="; \
		uv run claude-md-research generate -e 01-scale -p $$padding --claude-padding -o workspace/01-scale-p$$padding; \
		for trial in $(TRIALS_01); do \
			echo "--- Trial $$trial (padding=$$padding) ---"; \
			uv run claude-md-research run -e 01-scale -p $$padding -t $$trial -w workspace/01-scale-p$$padding; \
		done; \
	done

# 02-emphasis: Test which keywords improve compliance (5 styles × 5 trials = 25 runs)
run-02:
	@echo "=== Running 02-emphasis experiment (5 styles × 5 trials) ==="
	@for style in $(STYLES); do \
		echo ""; \
		echo "=== Style: $$style ==="; \
		uv run claude-md-research generate -e 02-emphasis -s $$style --claude-padding -o workspace/02-emphasis-$$style; \
		for trial in $(TRIALS_02); do \
			echo "--- Trial $$trial ($$style) ---"; \
			uv run claude-md-research run -e 02-emphasis -s $$style -t $$trial -w workspace/02-emphasis-$$style; \
		done; \
	done

# 03-rule-count: Test how many rules Claude can follow (15 counts × 3 trials = 45 runs)
run-03:
	@echo "=== Running 03-rule-count experiment (15 rule counts × 3 trials) ==="
	@for rules in $(RULE_COUNTS); do \
		echo ""; \
		echo "=== Rules: $$rules ==="; \
		uv run claude-md-research generate -e 03-rule-count -r $$rules -o workspace/03-rule-count-r$$rules; \
		for trial in $(TRIALS_03); do \
			echo "--- Trial $$trial (rules=$$rules) ---"; \
			uv run claude-md-research run -e 03-rule-count -r $$rules -t $$trial -w workspace/03-rule-count-r$$rules; \
		done; \
	done

# Analysis
analyze: analyze-01 analyze-02 analyze-03

analyze-01:
	@echo "=== Analyzing 01-scale ==="
	-uv run claude-md-research analyze -e 01-scale

analyze-02:
	@echo "=== Analyzing 02-emphasis ==="
	-uv run claude-md-research analyze -e 02-emphasis

analyze-03:
	@echo "=== Analyzing 03-rule-count ==="
	-uv run claude-md-research analyze -e 03-rule-count

# Cleanup
clean:
	rm -rf workspace results
	find . -type d -name __pycache__ -exec rm -rf {} +
	@echo "Cleaned workspace and results"
