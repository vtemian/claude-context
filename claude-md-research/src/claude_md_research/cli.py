"""Command-line interface for CLAUDE.md compliance research."""

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
@click.option("--padding", "-p", type=int, default=1000, help="Padding size")
@click.option("--style", "-s", default="neutral", help="Emphasis style")
def generate(experiment: str, output: str, padding: int, style: str):
    """Generate CLAUDE.md files for an experiment."""
    config_path = f"experiments/{experiment}/config.yaml"

    if not Path(config_path).exists():
        raise click.ClickException(f"Config not found: {config_path}")

    config = load_config_file(config_path)

    setup = setup_experiment_files(
        config=config,
        base_dir=output,
        padding_size=padding,
        style=style,
        skip_user_config=True,  # Don't modify user's ~/.claude/CLAUDE.md
    )

    click.echo(f"Created {len(setup.claude_md_paths)} CLAUDE.md files (level 0 skipped)")
    click.echo(f"Working directory: {setup.working_dir}")

    for path in setup.claude_md_paths:
        click.echo(f"  - {path}")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--padding", "-p", type=int, required=True, help="Padding size")
@click.option("--trial", "-t", type=int, default=1, help="Trial number")
@click.option("--output", "-o", default="./results", help="Results directory")
@click.option("--timeout", type=int, default=60, help="Timeout seconds")
@click.option("--style", "-s", default="neutral", help="Emphasis style")
def run(experiment: str, padding: int, trial: int, output: str, timeout: int, style: str):
    """Run a single experiment trial."""
    import tempfile

    config_path = f"experiments/{experiment}/config.yaml"
    config = load_config_file(config_path)

    trial_id = f"{experiment}-p{padding}-t{trial}"
    click.echo(f"Running trial: {trial_id}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        setup = setup_experiment_files(
            config=config,
            base_dir=tmpdir,
            padding_size=padding,
            style=style,
            backup_user_config=True,
        )

        # Calculate context size
        context_size = sum(
            Path(p).stat().st_size for p in setup.claude_md_paths
            if Path(p).exists()
        )

        click.echo(f"Context size: {context_size} chars")

        try:
            # Run Claude
            result = run_claude_session(
                working_dir=setup.working_dir,
                prompt=config.prompt,
                timeout=timeout,
            )

            if not result.success:
                click.echo(f"Error: {result.error}", err=True)
                return

            # Save raw output
            raw_dir = Path(output) / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_file = raw_dir / f"{trial_id}.txt"
            raw_file.write_text(result.output)

            # Analyze
            compliance = analyze_compliance(result.output, config.emojis)

            # Save metrics
            metrics = TrialMetrics(
                trial_id=trial_id,
                experiment=experiment,
                parameters={"padding_size": padding, "style": style},
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

        finally:
            teardown_experiment_files(setup)


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
            click.echo(f"  {size:>5} chars: {rate:.1%}")


if __name__ == "__main__":
    main()
