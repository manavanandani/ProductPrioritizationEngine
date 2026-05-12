"""Signal ingestion and feature attribute normalization service."""

import math
from typing import Dict, Any
from ..models.feature import Feature, ProductPillar


class SignalIngestionService:
    """Ingests multi-source customer feedback, telemetry, and market signals."""

    def __init__(self, base_monthly_active_users: int = 500_000):
        self.base_mau = base_monthly_active_users

    def compute_normalized_reach(self, feature: Feature) -> float:
        """Computes Reach in hundreds of users impacted per month.
        
        Combines direct MAU exposure with amplifier signals from support tickets
        and sales pipeline blockers.
        """
        raw_users = feature.telemetry.monthly_active_users_impacted
        ticket_amplifier = min(feature.telemetry.ticket_volume_per_month * 15, 50_000)
        sales_amplifier = min(feature.telemetry.gong_sales_mentions * 250, 100_000)
        
        effective_reach_users = raw_users + ticket_amplifier + sales_amplifier
        # Reach metric expressed in thousands (K users)
        normalized_reach = round(effective_reach_users / 1_000.0, 2)
        return max(1.0, normalized_reach)

    def compute_data_driven_impact(self, feature: Feature) -> float:
        """Determines impact multiplier (0.5 to 3.0) using business and funnel signals:
        - 3.0: Massive (High revenue ARR > $500k, extreme churn mitigation > 0.40, or major funnel fix)
        - 2.0: High (Significant revenue $200k-$500k, strong retention signal)
        - 1.0: Medium (Moderate workflow enhancement)
        - 0.5: Low (Minor polish, incremental delta)
        """
        rev_k = feature.market.revenue_opportunity_arr_k
        churn_risk = feature.market.churn_risk_score
        dropoff = feature.telemetry.engagement_dropoff_rate
        
        composite_score = (rev_k / 250.0) + (churn_risk * 2.0) + (dropoff * 2.5)

        # Strategic pillar weights
        if feature.pillar == ProductPillar.MONETIZATION and rev_k > 300:
            composite_score += 0.5
        elif feature.pillar == ProductPillar.GROWTH and dropoff > 0.25:
            composite_score += 0.5

        if composite_score >= 3.0:
            return 3.0
        elif composite_score >= 1.8:
            return 2.0
        elif composite_score >= 0.8:
            return 1.0
        else:
            return 0.5
