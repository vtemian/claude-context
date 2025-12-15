import pytest
import json
import tempfile
from pathlib import Path
from claude_md_research.metrics import (
    TrialMetrics,
    ExperimentMetrics,
    save_trial_metrics,
    load_experiment_metrics,
    aggregate_metrics,
)


def test_trial_metrics_to_dict():
    trial = TrialMetrics(
        trial_id="scale-p1000-t1",
        experiment="scale",
        parameters={"padding_size": 1000},
        sections_found=10,
        compliance_rates={"😀": 1.0, "😃": 0.8},
        overall_compliance=0.9,
        context_size_chars=5000,
        raw_output_file="raw/test.txt",
    )

    d = trial.to_dict()
    assert d["trial_id"] == "scale-p1000-t1"
    assert d["compliance_rates"]["😀"] == 1.0


def test_save_and_load_metrics():
    trial = TrialMetrics(
        trial_id="test-1",
        experiment="test",
        parameters={},
        sections_found=5,
        compliance_rates={"😀": 0.8},
        overall_compliance=0.8,
        context_size_chars=1000,
        raw_output_file="raw/test.txt",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        save_trial_metrics(trial, tmpdir)

        metrics_file = Path(tmpdir) / "metrics" / "test-1.json"
        assert metrics_file.exists()

        loaded = load_experiment_metrics(tmpdir, "test")
        assert len(loaded.trials) == 1
        assert loaded.trials[0].trial_id == "test-1"
