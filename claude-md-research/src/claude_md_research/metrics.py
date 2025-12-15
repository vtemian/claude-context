"""Store and aggregate experiment metrics."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class TrialMetrics:
    """Metrics from a single trial."""

    trial_id: str
    experiment: str
    parameters: dict[str, Any]
    sections_found: int
    compliance_rates: dict[str, float]
    overall_compliance: float
    context_size_chars: int
    raw_output_file: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TrialMetrics":
        return cls(**data)


@dataclass
class ExperimentMetrics:
    """Aggregated metrics for an experiment."""

    experiment: str
    trials: list[TrialMetrics]

    def mean_compliance_by_param(self, param: str) -> dict[Any, float]:
        """Calculate mean compliance grouped by a parameter."""
        groups: dict[Any, list[float]] = {}
        for trial in self.trials:
            key = trial.parameters.get(param)
            if key is not None:
                if key not in groups:
                    groups[key] = []
                groups[key].append(trial.overall_compliance)

        return {k: sum(v) / len(v) for k, v in groups.items()}


def save_trial_metrics(trial: TrialMetrics, results_dir: str) -> None:
    """Save trial metrics to JSON file."""
    metrics_dir = Path(results_dir) / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    filepath = metrics_dir / f"{trial.trial_id}.json"
    with open(filepath, "w") as f:
        json.dump(trial.to_dict(), f, indent=2)


def load_experiment_metrics(results_dir: str, experiment: str) -> ExperimentMetrics:
    """Load all trial metrics for an experiment."""
    metrics_dir = Path(results_dir) / "metrics"
    trials = []

    if metrics_dir.exists():
        for filepath in metrics_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)
                if data.get("experiment") == experiment:
                    trials.append(TrialMetrics.from_dict(data))

    return ExperimentMetrics(experiment=experiment, trials=trials)


def aggregate_metrics(metrics: ExperimentMetrics) -> dict:
    """Calculate aggregate statistics."""
    if not metrics.trials:
        return {}

    all_compliance = [t.overall_compliance for t in metrics.trials]

    return {
        "experiment": metrics.experiment,
        "total_trials": len(metrics.trials),
        "mean_compliance": sum(all_compliance) / len(all_compliance),
        "min_compliance": min(all_compliance),
        "max_compliance": max(all_compliance),
    }
