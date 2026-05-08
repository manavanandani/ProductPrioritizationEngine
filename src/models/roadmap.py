"""Roadmap planning models and quarterly allocation structures."""

from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field


class RoadmapTier(str, Enum):
    NOW = "Now (Commit: Current Quarter)"
    NEXT = "Next (Target: Next Quarter)"
    LATER = "Later (Backlog: Future Review)"


class RoadmapItem(BaseModel):
    """Allocated feature item within roadmap tiers."""
    feature_id: str
    title: str
    pillar: str
    rank: int
    calibrated_score: float
    effort_weeks: float
    cumulative_capacity: float
    tier: RoadmapTier


class QuarterlyRoadmap(BaseModel):
    """Quarterly roadmap plan with capacity limits and pillar balance."""
    quarter_name: str
    total_capacity_weeks: float
    allocated_now_weeks: float
    allocated_next_weeks: float
    pillar_breakdown: Dict[str, float]
    items: List[RoadmapItem]
    executive_summary: str
