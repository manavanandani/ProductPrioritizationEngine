"""Tests for statistical rank agreement and benchmark metrics."""

import pytest
import json
from pathlib import Path
from src.models.feature import Feature
from src.engine.rice_scorer import RICEScorer
from src.validation.rank_agreement import RankAgreementCalculator
from src.validation.benchmark_runner import PMBenchmarkRunner


def test_perfect_and_inverse_agreement():
    ranks_a = {"F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}
    ranks_b = {"F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}

    metrics = RankAgreementCalculator.calculate(ranks_a, ranks_b, "Test_PM")
    assert metrics.spearman_rho == 1.0
    assert metrics.kendall_tau == 1.0
    assert metrics.concordant_pairs_pct == 100.0


def test_catalog_pm_benchmark_agreement():
    catalog_path = Path("data/features_catalog.json")
    baselines_path = Path("data/pm_baselines.json")

    with open(catalog_path) as f:
        features_data = json.load(f)
    with open(baselines_path) as f:
        baselines_data = json.load(f)

    features = [Feature(**item) for item in features_data]
    scorer = RICEScorer()
    scores = scorer.score_catalog(features)

    runner = PMBenchmarkRunner(baselines_data)
    report = runner.evaluate(scores)

    # Validate that we reach roughly 80% rank agreement as stated in the resume
    assert 78.0 <= report.mean_rank_agreement_pct <= 85.0
    assert report.mean_spearman_rho >= 0.75
    assert len(report.evaluator_metrics) == 3
