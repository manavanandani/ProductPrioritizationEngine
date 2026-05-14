"""Tests for telemetry and feedback signal ingestion."""

import pytest
from src.models.feature import Feature, ProductPillar, ComplexityLevel, TelemetrySignals, MarketData, EffortEstimate
from src.engine.signal_ingestion import SignalIngestionService


@pytest.fixture
def sample_feature():
    return Feature(
        feature_id="TEST-001",
        title="Sample Test Feature",
        pillar=ProductPillar.GROWTH,
        description="Test description",
        telemetry=TelemetrySignals(
            monthly_active_users_impacted=50000,
            ticket_volume_per_month=40,
            gong_sales_mentions=10,
            engagement_dropoff_rate=0.25,
        ),
        market=MarketData(
            competitor_offering_count=3,
            churn_risk_score=0.20,
            revenue_opportunity_arr_k=250.0,
        ),
        effort=EffortEstimate(
            eng_weeks=3.0,
            design_weeks=1.0,
            infra_complexity=ComplexityLevel.LOW,
            cross_team_dependencies=0,
        ),
    )


def test_normalized_reach_computation(sample_feature):
    service = SignalIngestionService()
    reach = service.compute_normalized_reach(sample_feature)
    # 50,000 + 40*15 (600) + 10*250 (2500) = 53,100 -> 53.1k
    assert reach == pytest.approx(53.1, rel=1e-2)


def test_impact_levels(sample_feature):
    service = SignalIngestionService()
    impact = service.compute_data_driven_impact(sample_feature)
    assert impact in [0.5, 1.0, 2.0, 3.0]
    assert impact >= 2.0  # Significant revenue & drop-off
