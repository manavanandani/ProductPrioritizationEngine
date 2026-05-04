"""Feature definition and telemetry signal models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProductPillar(str, Enum):
    GROWTH = "Growth"
    CORE_PLATFORM = "Core Platform"
    MONETIZATION = "Monetization"
    TRUST_AND_SAFETY = "Trust & Safety"


class ComplexityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TelemetrySignals(BaseModel):
    """Raw telemetry and user feedback signals."""
    monthly_active_users_impacted: int = Field(..., ge=0, description="Estimated users in the target workflow per month")
    ticket_volume_per_month: int = Field(..., ge=0, description="Zendesk / Support tickets referencing this pain point")
    gong_sales_mentions: int = Field(..., ge=0, description="Recorded sales/customer call blocker mentions")
    engagement_dropoff_rate: float = Field(..., ge=0.0, le=1.0, description="Funnel drop-off rate attributable to friction")


class MarketData(BaseModel):
    """Competitive intelligence and business risk."""
    competitor_offering_count: int = Field(..., ge=0, description="Top-5 competitors already offering this feature")
    churn_risk_score: float = Field(..., ge=0.0, le=1.0, description="Probability of account churn tied to missing capability")
    revenue_opportunity_arr_k: float = Field(..., ge=0.0, description="Annual Recurring Revenue impact in $K")


class EffortEstimate(BaseModel):
    """Cross-functional engineering and design effort."""
    eng_weeks: float = Field(..., gt=0.0, description="Estimated engineering person-weeks")
    design_weeks: float = Field(..., ge=0.0, description="Product design and research weeks")
    infra_complexity: ComplexityLevel = Field(default=ComplexityLevel.MEDIUM, description="Infrastructure backend complexity")
    cross_team_dependencies: int = Field(default=0, ge=0, description="Number of external partner teams required")

    @property
    def total_effort_units(self) -> float:
        """Weighted effort composite reflecting cross-team coordination overhead."""
        complexity_multipliers = {
            ComplexityLevel.LOW: 1.0,
            ComplexityLevel.MEDIUM: 1.15,
            ComplexityLevel.HIGH: 1.35,
        }
        dep_overhead = 1.0 + (0.10 * self.cross_team_dependencies)
        raw_weeks = self.eng_weeks + (self.design_weeks * 0.75)
        return round(raw_weeks * complexity_multipliers[self.infra_complexity] * dep_overhead, 2)


class Feature(BaseModel):
    """Product feature candidate for roadmap prioritization."""
    feature_id: str = Field(..., description="Unique alphanumeric identifier (e.g., FEAT-101)")
    title: str = Field(..., description="Feature title")
    pillar: ProductPillar = Field(..., description="Primary strategic pillar")
    description: str = Field(..., description="Executive problem statement & proposed solution")
    telemetry: TelemetrySignals = Field(..., description="User feedback and telemetry signals")
    market: MarketData = Field(..., description="Market parity and revenue impact")
    effort: EffortEstimate = Field(..., description="Resource estimates")
