"""Command-line interface for CLAUDE.md compliance research."""

import click
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """CLAUDE.md Compliance Research Framework.

    Empirically measure how well Claude follows CLAUDE.md instructions
    under various conditions.
    """
    pass


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name (e.g., 01-scale)")
@click.option("--output", "-o", default="./workspace", help="Output directory")
@click.option("--padding", "-p", type=int, default=1000, help="Padding size in chars")
def generate(experiment: str, output: str, padding: int):
    """Generate CLAUDE.md files for an experiment."""
    click.echo(f"Generating experiment: {experiment}")
    click.echo(f"Output directory: {output}")
    click.echo(f"Padding size: {padding}")

    # TODO: Load config and generate files
    click.echo("Generated experiment files.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--trial", "-t", type=int, default=1, help="Trial number")
@click.option("--timeout", type=int, default=60, help="Timeout in seconds")
def run(experiment: str, trial: int, timeout: int):
    """Run a single experiment trial."""
    click.echo(f"Running {experiment} trial {trial}...")

    # TODO: Setup files, run Claude, analyze output
    click.echo("Trial complete.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--input", "-i", "input_dir", default="./results", help="Results directory")
def analyze(experiment: str, input_dir: str):
    """Analyze experiment results."""
    click.echo(f"Analyzing {experiment}...")
    click.echo(f"Input directory: {input_dir}")

    # TODO: Load metrics, compute aggregates
    click.echo("Analysis complete.")


@main.command()
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--format", "-f", type=click.Choice(["html", "png", "csv"]), default="png")
@click.option("--output", "-o", default="./results/charts", help="Output directory")
def report(experiment: str, format: str, output: str):
    """Generate charts and reports."""
    click.echo(f"Generating {format} report for {experiment}...")

    # TODO: Generate charts
    click.echo(f"Report saved to {output}")


if __name__ == "__main__":
    main()
