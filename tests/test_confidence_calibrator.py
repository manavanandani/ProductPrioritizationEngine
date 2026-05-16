"""Tests for multi-source confidence calibration."""

import pytest
from src.models.feature import Feature, ProductPillar, ComplexityLevel, TelemetrySignals, MarketData, EffortEstimate
from src.engine.confidence_calibrator import ConfidenceCalibrator


def test_confidence_triangulation():
    calibrator = ConfidenceCalibrator()

    # Feature with high telemetry, strong feedback, and market parity
    feat_high = Feature(
        feature_id="HIGH-01",
        title="High Signal Feature",
        pillar=ProductPillar.CORE_PLATFORM,
        description="High signal test",
        telemetry=TelemetrySignals(
            monthly_active_users_impacted=150000,
            ticket_volume_per_month=90,
            gong_sales_mentions=30,
            engagement_dropoff_rate=0.20,
        ),
        market=MarketData(
            competitor_offering_count=4,
            churn_risk_score=0.30,
            revenue_opportunity_arr_k=400.0,
        ),
        effort=EffortEstimate(eng_weeks=4.0, design_weeks=1.0),
    )

    conf_high, details_high = calibrator.calibrate(feat_high)
    assert 0.70 <= conf_high <= 1.00
    assert details_high.data_source_count == 3

    # Feature with weak signal
    feat_low = Feature(
        feature_id="LOW-01",
        title="Low Signal Feature",
        pillar=ProductPillar.GROWTH,
        description="Low signal test",
        telemetry=TelemetrySignals(
            monthly_active_users_impacted=2000,
            ticket_volume_per_month=3,
            gong_sales_mentions=0,
            engagement_dropoff_rate=0.01,
        ),
        market=MarketData(
            competitor_offering_count=0,
            churn_risk_score=0.01,
            revenue_opportunity_arr_k=0.0,
        ),
        effort=EffortEstimate(eng_weeks=2.0, design_weeks=1.0),
    )

    conf_low, details_low = calibrator.calibrate(feat_low)
    assert conf_low <= 0.50
    assert details_low.data_source_count <= 1
