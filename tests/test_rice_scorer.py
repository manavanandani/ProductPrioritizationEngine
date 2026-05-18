"""Tests for RICE scoring and ranking."""

import pytest
from src.models.feature import Feature, ProductPillar, ComplexityLevel, TelemetrySignals, MarketData, EffortEstimate
from src.engine.rice_scorer import RICEScorer


def test_rice_scorer_ranking():
    scorer = RICEScorer()

    f1 = Feature(
        feature_id="F1",
        title="Quick Win",
        pillar=ProductPillar.GROWTH,
        description="High reach, low effort",
        telemetry=TelemetrySignals(
            monthly_active_users_impacted=100000,
            ticket_volume_per_month=50,
            gong_sales_mentions=20,
            engagement_dropoff_rate=0.30,
        ),
        market=MarketData(competitor_offering_count=3, churn_risk_score=0.20, revenue_opportunity_arr_k=200.0),
        effort=EffortEstimate(eng_weeks=1.0, design_weeks=0.5, infra_complexity=ComplexityLevel.LOW),
    )

    f2 = Feature(
        feature_id="F2",
        title="Heavy Lift",
        pillar=ProductPillar.CORE_PLATFORM,
        description="Low reach, high effort",
        telemetry=TelemetrySignals(
            monthly_active_users_impacted=10000,
            ticket_volume_per_month=10,
            gong_sales_mentions=2,
            engagement_dropoff_rate=0.05,
        ),
        market=MarketData(competitor_offering_count=1, churn_risk_score=0.05, revenue_opportunity_arr_k=50.0),
        effort=EffortEstimate(eng_weeks=10.0, design_weeks=3.0, infra_complexity=ComplexityLevel.HIGH),
    )

    scores = scorer.score_catalog([f2, f1])
    assert len(scores) == 2
    # Quick win should rank #1
    assert scores[0].feature_id == "F1"
    assert scores[0].rank == 1
    assert scores[1].feature_id == "F2"
    assert scores[1].rank == 2
    assert scores[0].calibrated_score > scores[1].calibrated_score
