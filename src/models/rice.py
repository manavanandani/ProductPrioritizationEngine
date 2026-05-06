"""RICE scoring models with telemetry calibration attributes."""

from pydantic import BaseModel, Field


class CalibrationDetails(BaseModel):
    """Detailed telemetry confidence calibration factors."""
    data_source_count: int = Field(..., description="Number of converging signal sources")
    telemetry_depth_factor: float = Field(..., ge=0.0, le=1.0, description="Confidence derived from telemetry volume")
    market_parity_factor: float = Field(..., ge=0.0, le=1.0, description="Confidence derived from market validation")
    feedback_signal_factor: float = Field(..., ge=0.0, le=1.0, description="Confidence derived from user feedback & sales transcripts")
    signal_triangulation_score: float = Field(..., ge=0.0, le=1.0, description="Combined statistical confidence (0 to 1)")


class RICEScore(BaseModel):
    """Computed RICE score and normalized metrics."""
    feature_id: str
    reach: float = Field(..., ge=0.0, description="Estimated monthly reach in normalized units")
    impact: float = Field(..., ge=0.5, le=3.0, description="Impact multiplier: 3=Massive, 2=High, 1=Medium, 0.5=Low")
    confidence: float = Field(..., ge=0.1, le=1.0, description="Calibrated confidence score (0.10 to 1.00)")
    effort: float = Field(..., gt=0.0, description="Composite effort in person-weeks")
    raw_rice: float = Field(..., description="(Reach * Impact * Confidence) / Effort")
    calibrated_score: float = Field(..., description="Pillar-adjusted and risk-calibrated score")
    rank: int = Field(default=0, ge=0, description="Computed priority rank")
