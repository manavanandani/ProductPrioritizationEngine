"""Tests for quarterly roadmap planning and capacity allocation."""

import pytest
from src.models.feature import Feature, ProductPillar, ComplexityLevel, TelemetrySignals, MarketData, EffortEstimate
from src.engine.rice_scorer import RICEScorer
from src.engine.roadmap_planner import RoadmapPlanner
from src.models.roadmap import RoadmapTier


def test_roadmap_allocation_capacity():
    features = [
        Feature(
            feature_id=f"FEAT-{i}",
            title=f"Feature {i}",
            pillar=ProductPillar.GROWTH if i % 2 == 0 else ProductPillar.MONETIZATION,
            description="Test feature",
            telemetry=TelemetrySignals(
                monthly_active_users_impacted=50000 * i,
                ticket_volume_per_month=20 * i,
                gong_sales_mentions=5 * i,
                engagement_dropoff_rate=0.15,
            ),
            market=MarketData(competitor_offering_count=2, churn_risk_score=0.15, revenue_opportunity_arr_k=150.0),
            effort=EffortEstimate(eng_weeks=5.0, design_weeks=1.0, infra_complexity=ComplexityLevel.LOW),
        )
        for i in range(1, 15)
    ]

    scorer = RICEScorer()
    scores = scorer.score_catalog(features)

    # Capacity of 25 weeks (approx 4-5 features in 'Now')
    planner = RoadmapPlanner(quarter_capacity_weeks=25.0)
    roadmap = planner.build_roadmap(features, scores, quarter_name="Q4 Review")

    assert roadmap.allocated_now_weeks <= 25.0
    now_items = [item for item in roadmap.items if item.tier == RoadmapTier.NOW]
    next_items = [item for item in roadmap.items if item.tier == RoadmapTier.NEXT]
    later_items = [item for item in roadmap.items if item.tier == RoadmapTier.LATER]

    assert len(now_items) > 0
    assert len(next_items) > 0
    assert len(later_items) > 0
    assert len(now_items) + len(next_items) + len(later_items) == 14
