"""Quarterly roadmap planner and resource capacity allocation engine."""

from typing import List, Dict
from ..models.feature import Feature
from ..models.rice import RICEScore
from ..models.roadmap import RoadmapItem, QuarterlyRoadmap, RoadmapTier


class RoadmapPlanner:
    """Allocates prioritized features into quarterly roadmap review buckets based on capacity."""

    def __init__(self, quarter_capacity_weeks: float = 45.0):
        self.quarter_capacity_weeks = quarter_capacity_weeks

    def build_roadmap(
        self,
        features: List[Feature],
        scores: List[RICEScore],
        quarter_name: str = "Q3 Planning Review",
    ) -> QuarterlyRoadmap:
        """Constructs a tiered quarterly roadmap with capacity constraints."""
        feature_map = {f.feature_id: f for f in features}
        score_map = {s.feature_id: s for s in scores}

        # Ensure scores are ranked
        sorted_scores = sorted(scores, key=lambda s: s.rank)

        items: List[RoadmapItem] = []
        cumulative_weeks = 0.0
        allocated_now = 0.0
        allocated_next = 0.0
        pillar_efforts: Dict[str, float] = {}

        for score in sorted_scores:
            feat = feature_map[score.feature_id]
            effort = score.effort
            cumulative_weeks += effort

            if cumulative_weeks <= self.quarter_capacity_weeks:
                tier = RoadmapTier.NOW
                allocated_now += effort
                pillar_efforts[feat.pillar.value] = pillar_efforts.get(feat.pillar.value, 0.0) + effort
            elif cumulative_weeks <= (self.quarter_capacity_weeks * 2.0):
                tier = RoadmapTier.NEXT
                allocated_next += effort
            else:
                tier = RoadmapTier.LATER

            items.append(
                RoadmapItem(
                    feature_id=feat.feature_id,
                    title=feat.title,
                    pillar=feat.pillar.value,
                    rank=score.rank,
                    calibrated_score=score.calibrated_score,
                    effort_weeks=effort,
                    cumulative_capacity=round(cumulative_weeks, 2),
                    tier=tier,
                )
            )

        # Generate executive summary
        now_count = sum(1 for i in items if i.tier == RoadmapTier.NOW)
        next_count = sum(1 for i in items if i.tier == RoadmapTier.NEXT)
        later_count = sum(1 for i in items if i.tier == RoadmapTier.LATER)

        exec_summary = (
            f"Roadmap plan for {quarter_name}: {now_count} committed features in 'Now' "
            f"utilizing {round(allocated_now, 1)}/{self.quarter_capacity_weeks} eng-weeks capacity. "
            f"{next_count} features queued for 'Next' ({round(allocated_next, 1)} eng-weeks). "
            f"{later_count} backlog items categorized as 'Later'."
        )

        return QuarterlyRoadmap(
            quarter_name=quarter_name,
            total_capacity_weeks=self.quarter_capacity_weeks,
            allocated_now_weeks=round(allocated_now, 2),
            allocated_next_weeks=round(allocated_next, 2),
            pillar_breakdown={k: round(v, 2) for k, v in pillar_efforts.items()},
            items=items,
            executive_summary=exec_summary,
        )
