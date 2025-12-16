"""Command-line interface for CLAUDE.md compliance research."""

import json
import click
from pathlib import Path

from claude_md_research.config import load_config_file
from claude_md_research.setup import setup_experiment_files, teardown_experiment_files
from claude_md_research.runner import run_claude_session
from claude_md_research.analyzer import analyze_compliance
from claude_md_research.metrics import (
    TrialMetrics,
    save_trial_metrics,
    load_experiment_metrics,
    aggregate_metrics,
)


@click.group()
@click.version_option()
def main():
    """CLAUDE.md Compliance Research Framework."""
    pass


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--output", "-o", default="./workspace", help="Output directory")
@click.option("--padding", "-p", type=int, default=None, help="Padding size (chars)")
@click.option("--rules", "-r", type=int, default=None, help="Total number of rules (overrides padding)")
@click.option("--max-emojis", "-m", type=int, default=5, help="Max emojis per level for padding mode")
@click.option("--style", "-s", default="neutral", help="Emphasis style")
@click.option("--claude-padding", is_flag=True, help="Use Claude API to generate padding")
def generate(experiment: str, output: str, padding: int | None, rules: int | None, max_emojis: int, style: str, claude_padding: bool):
    """Generate CLAUDE.md files for an experiment."""
    config_path = f"experiments/{experiment}/config.yaml"

    if not Path(config_path).exists():
        raise click.ClickException(f"Config not found: {config_path}")

    config = load_config_file(config_path)

    # Default padding if neither specified
    if padding is None and rules is None:
        padding = 1000

    setup = setup_experiment_files(
        config=config,
        base_dir=output,
        padding_size=padding,
        num_rules=rules,
        max_emojis=max_emojis,
        style=style,
        skip_user_config=True,  # Don't modify user's ~/.claude/CLAUDE.md
        use_claude_padding=claude_padding,
    )

    total_emojis = len(setup.all_emojis)
    click.echo(f"Created {len(setup.claude_md_paths)} CLAUDE.md files (level 0 skipped)")
    click.echo(f"Total rules/emojis: {total_emojis}")
    if rules:
        click.echo(f"Mode: fixed rule count")
    else:
        padding_type = "Claude API" if claude_padding else "templates"
        click.echo(f"Mode: padding-based ({padding} chars, {padding_type})")
    click.echo(f"Working directory: {setup.working_dir}")

    for level, emojis in setup.emojis_by_level.items():
        level_names = {1: "root", 2: "src", 3: "src/lib", 4: "src/lib/core"}
        click.echo(f"  Level {level} ({level_names.get(level, '?')}): {len(emojis)} rules")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--trial", "-t", type=int, default=1, help="Trial number")
@click.option("--padding", "-p", type=int, default=None, help="Padding size (for metrics)")
@click.option("--rules", "-r", type=int, default=None, help="Rule count (for metrics)")
@click.option("--style", "-s", default=None, help="Style used (for metrics)")
@click.option("--output", "-o", default="./results", help="Results directory")
@click.option("--workspace", "-w", default="./workspace", help="Workspace with CLAUDE.md files (from generate)")
@click.option("--timeout", type=int, default=120, help="Timeout seconds")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed logs")
def run(experiment: str, trial: int, padding: int | None, rules: int | None, style: str | None, output: str, workspace: str, timeout: int, verbose: bool):
    """Run Claude in workspace and analyze compliance.

    First use 'generate' to create CLAUDE.md files, then 'run' to execute.
    """
    config_path = f"experiments/{experiment}/config.yaml"
    config = load_config_file(config_path)

    # Find the deepest directory in workspace
    workspace_path = Path(workspace).resolve()
    if not workspace_path.exists():
        raise click.ClickException(f"Workspace not found: {workspace}. Run 'generate' first.")

    # Find all CLAUDE.md files and show them
    claude_md_files = list(workspace_path.rglob("CLAUDE.md"))
    if not claude_md_files:
        raise click.ClickException(f"No CLAUDE.md files found in {workspace}. Run 'generate' first.")

    click.echo(f"Found {len(claude_md_files)} CLAUDE.md files:")
    context_size = 0
    for claude_md in claude_md_files:
        size = claude_md.stat().st_size
        context_size += size
        click.echo(f"  {claude_md} ({size} chars)")
        if verbose:
            content = claude_md.read_text()
            first_line = content.split('\n')[0][:60]
            click.echo(f"    First line: {first_line}...")

    # Find working directory (deepest level with CLAUDE.md)
    working_dir = workspace_path
    for subdir in ["src/lib/core", "src/lib", "src", ""]:
        candidate = workspace_path / subdir if subdir else workspace_path
        if (candidate / "CLAUDE.md").exists():
            working_dir = candidate
            break

    # Build trial ID with parameters
    trial_id_parts = [experiment]
    if padding:
        trial_id_parts.append(f"p{padding}")
    if rules:
        trial_id_parts.append(f"r{rules}")
    if style:
        trial_id_parts.append(f"s-{style}")
    trial_id_parts.append(f"t{trial}")
    trial_id = "-".join(trial_id_parts)
    click.echo(f"\nRunning trial: {trial_id}")
    click.echo(f"Total context: {context_size} chars")
    click.echo(f"Working dir: {working_dir}")
    click.echo(f"Prompt: {config.prompt[:50]}...")

    # Run Claude
    click.echo("\nExecuting Claude...")
    result = run_claude_session(
        working_dir=str(working_dir),
        prompt=config.prompt,
        timeout=timeout,
    )

    if not result.success:
        if result.error:
            click.echo(f"stderr: {result.error}", err=True)
        if result.output:
            click.echo(f"stdout (may contain error): {result.output[:500]}", err=True)
        raise click.ClickException(f"Claude failed: {result.error or 'unknown error (check stdout)'}")

    click.echo(f"Claude completed in {result.duration_seconds:.1f}s")

    if verbose:
        click.echo(f"\n--- Raw output preview (first 500 chars) ---")
        click.echo(result.output[:500])
        click.echo("--- End preview ---\n")

    # Save raw output
    raw_dir = Path(output) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_file = raw_dir / f"{trial_id}.txt"
    raw_file.write_text(result.output)
    click.echo(f"Raw output saved to: {raw_file}")

    # Load emoji manifest to know which emojis to check
    manifest_path = workspace_path / ".emojis_manifest.json"
    if manifest_path.exists():
        emojis_by_level = json.loads(manifest_path.read_text())
        # Flatten all emojis from all levels
        emojis_to_check = []
        for level_emojis in emojis_by_level.values():
            emojis_to_check.extend(level_emojis)
    else:
        # Fallback to config emojis (skip level 0)
        emojis_to_check = config.emojis[1:]

    compliance = analyze_compliance(result.output, emojis_to_check)

    # Save metrics
    parameters = {}
    if padding:
        parameters["padding_size"] = padding
    if rules:
        parameters["num_rules"] = rules
    if style:
        parameters["style"] = style

    metrics = TrialMetrics(
        trial_id=trial_id,
        experiment=experiment,
        parameters=parameters,
        sections_found=compliance.total_sections,
        compliance_rates=compliance.compliance_rates,
        overall_compliance=compliance.overall_compliance,
        context_size_chars=context_size,
        raw_output_file=str(raw_file),
    )

    save_trial_metrics(metrics, output)

    click.echo(f"Sections found: {compliance.total_sections}")
    click.echo(f"Overall compliance: {compliance.overall_compliance:.1%}")
    for emoji, rate in compliance.compliance_rates.items():
        click.echo(f"  {emoji}: {rate:.1%}")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--input", "-i", "input_dir", default="./results", help="Results dir")
def analyze(experiment: str, input_dir: str):
    """Analyze experiment results."""
    metrics = load_experiment_metrics(input_dir, experiment)

    if not metrics.trials:
        click.echo("No trials found.")
        return

    agg = aggregate_metrics(metrics)

    click.echo(f"Experiment: {agg['experiment']}")
    click.echo(f"Total trials: {agg['total_trials']}")
    click.echo(f"Mean compliance: {agg['mean_compliance']:.1%}")
    click.echo(f"Range: {agg['min_compliance']:.1%} - {agg['max_compliance']:.1%}")

    # Group by padding size
    by_padding = metrics.mean_compliance_by_param("padding_size")
    if by_padding:
        click.echo("\nBy padding size:")
        for size, rate in sorted(by_padding.items()):
            click.echo(f"  {size:>6} chars: {rate:.1%}")

    # Group by rule count
    by_rules = metrics.mean_compliance_by_param("num_rules")
    if by_rules:
        click.echo("\nBy rule count:")
        for count, rate in sorted(by_rules.items()):
            click.echo(f"  {count:>3} rules: {rate:.1%}")


if __name__ == "__main__":
    main()
