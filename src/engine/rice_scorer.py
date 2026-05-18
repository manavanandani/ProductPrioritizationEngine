"""RICE score calculation engine with strategic weighting."""

from typing import List, Dict, Optional
from ..models.feature import Feature, ProductPillar
from ..models.rice import RICEScore
from .signal_ingestion import SignalIngestionService
from .confidence_calibrator import ConfidenceCalibrator


class RICEScorer:
    """Computes calibrated RICE scores across product feature candidates."""

    def __init__(
        self,
        pillar_weights: Optional[Dict[ProductPillar, float]] = None,
        base_mau: int = 500_000,
    ):
        self.signal_service = SignalIngestionService(base_monthly_active_users=base_mau)
        self.confidence_calibrator = ConfidenceCalibrator()
        self.pillar_weights = pillar_weights or {
            ProductPillar.GROWTH: 1.10,
            ProductPillar.CORE_PLATFORM: 1.05,
            ProductPillar.MONETIZATION: 1.15,
            ProductPillar.TRUST_AND_SAFETY: 1.00,
        }

    def score_feature(self, feature: Feature) -> RICEScore:
        """Calculates raw and calibrated RICE scores for an individual feature."""
        reach = self.signal_service.compute_normalized_reach(feature)
        impact = self.signal_service.compute_data_driven_impact(feature)
        confidence, _ = self.confidence_calibrator.calibrate(feature)
        effort = max(0.5, feature.effort.total_effort_units)

        raw_rice = round((reach * impact * confidence) / effort, 2)

        # Strategic pillar calibration
        weight = self.pillar_weights.get(feature.pillar, 1.0)
        calibrated_score = round(raw_rice * weight, 2)

        return RICEScore(
            feature_id=feature.feature_id,
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
            raw_rice=raw_rice,
            calibrated_score=calibrated_score,
            rank=0,
        )

    def score_catalog(self, features: List[Feature]) -> List[RICEScore]:
        """Scores all features in a catalog and sorts them in descending order of priority."""
        scores = [self.score_feature(f) for f in features]
        # Sort descending by calibrated score; break ties by raw_rice then effort
        scores.sort(key=lambda s: (s.calibrated_score, s.raw_rice, -s.effort), reverse=True)

        for rank_idx, score in enumerate(scores, start=1):
            score.rank = rank_idx

        return scores
