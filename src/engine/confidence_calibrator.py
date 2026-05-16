"""Confidence calibration engine based on multi-source signal triangulation."""

import math
from ..models.feature import Feature
from ..models.rice import CalibrationDetails


class ConfidenceCalibrator:
    """Calibrates RICE Confidence by triangulating telemetry, market, and feedback signals."""

    def calibrate(self, feature: Feature) -> tuple[float, CalibrationDetails]:
        """Calculates confidence score (0.10 to 1.00) based on signal convergence."""
        sources = 0

        # Source 1: Telemetry volume
        has_telemetry = feature.telemetry.monthly_active_users_impacted >= 5_000
        if has_telemetry:
            sources += 1
        telemetry_depth = min(1.0, math.log10(max(10, feature.telemetry.monthly_active_users_impacted)) / 5.0)

        # Source 2: User feedback / Support volume
        has_support = feature.telemetry.ticket_volume_per_month >= 15
        if has_support:
            sources += 1
        feedback_depth = min(1.0, (feature.telemetry.ticket_volume_per_month / 100.0) * 0.6 + 
                                  (feature.telemetry.gong_sales_mentions / 40.0) * 0.4)

        # Source 3: Direct revenue / churn financial telemetry
        has_market = feature.market.competitor_offering_count >= 1 or feature.market.revenue_opportunity_arr_k > 0
        if has_market:
            sources += 1
        market_depth = min(1.0, (feature.market.competitor_offering_count / 4.0) * 0.5 + 
                                (feature.market.churn_risk_score * 0.5))

        # Triangulation weighting
        triangulation_raw = (0.35 * telemetry_depth) + (0.35 * feedback_depth) + (0.30 * market_depth)

        # Confidence penalties for single-source or low-signal features
        if sources <= 1:
            calibrated_confidence = max(0.30, min(0.50, triangulation_raw * 0.6))
        elif sources == 2:
            calibrated_confidence = max(0.50, min(0.75, triangulation_raw * 0.85))
        else:
            # All 3 sources triangulated
            calibrated_confidence = max(0.70, min(1.00, triangulation_raw * 1.05))

        # Round to nearest 5% tier standard for PM readability (e.g., 0.50, 0.65, 0.80, 0.95, 1.0)
        calibrated_confidence = round(round(calibrated_confidence * 20.0) / 20.0, 2)
        calibrated_confidence = max(0.20, min(1.00, calibrated_confidence))

        details = CalibrationDetails(
            data_source_count=sources,
            telemetry_depth_factor=round(telemetry_depth, 3),
            market_parity_factor=round(market_depth, 3),
            feedback_signal_factor=round(feedback_depth, 3),
            signal_triangulation_score=round(triangulation_raw, 3),
        )

        return calibrated_confidence, details
