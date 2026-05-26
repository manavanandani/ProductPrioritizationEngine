"""Command-line interface for the ProductPrioritizationEngine."""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .models.feature import Feature
from .engine.rice_scorer import RICEScorer
from .engine.roadmap_planner import RoadmapPlanner
from .validation.benchmark_runner import PMBenchmarkRunner
from .reporting.terminal_formatter import TerminalFormatter
from .reporting.executive_summary import ExecutiveSummaryGenerator


def load_features(file_path: str) -> List[Feature]:
    """Loads feature catalog from JSON file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Feature catalog file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Feature(**item) for item in data]


def load_baselines(file_path: str):
    """Loads PM baseline rankings from JSON file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Baselines file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_score(args):
    """Executes feature scoring and displays ranked results."""
    features = load_features(args.features)
    scorer = RICEScorer()
    scores = scorer.score_catalog(features)
    formatter = TerminalFormatter()
    formatter.print_scoring_table(features, scores, top_n=args.top)


def cmd_validate(args):
    """Validates model against 3 independent PM baselines."""
    features = load_features(args.features)
    baselines = load_baselines(args.baselines)
    scorer = RICEScorer()
    scores = scorer.score_catalog(features)
    runner = PMBenchmarkRunner(baselines_data=baselines)
    report = runner.evaluate(scores)
    formatter = TerminalFormatter()
    formatter.print_benchmark_table(report)


def cmd_roadmap(args):
    """Plans quarterly roadmap with capacity constraints."""
    features = load_features(args.features)
    scorer = RICEScorer()
    scores = scorer.score_catalog(features)
    planner = RoadmapPlanner(quarter_capacity_weeks=args.capacity)
    roadmap = planner.build_roadmap(features, scores, quarter_name=args.quarter)
    formatter = TerminalFormatter()
    formatter.print_roadmap_table(roadmap)


def cmd_export(args):
    """Generates and exports executive markdown briefing."""
    features = load_features(args.features)
    baselines = load_baselines(args.baselines)
    scorer = RICEScorer()
    scores = scorer.score_catalog(features)
    runner = PMBenchmarkRunner(baselines_data=baselines)
    benchmark = runner.evaluate(scores)
    planner = RoadmapPlanner(quarter_capacity_weeks=args.capacity)
    roadmap = planner.build_roadmap(features, scores, quarter_name=args.quarter)
    markdown = ExecutiveSummaryGenerator.generate_markdown_report(roadmap, benchmark, features)

    output_path = Path(args.output)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"✅ Successfully exported Executive Roadmap Briefing to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="prioritize",
        description="ProductPrioritizationEngine - Data-driven RICE feature scoring & PM intuition benchmark",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Score command
    p_score = subparsers.add_parser("score", help="Score and rank features from catalog")
    p_score.add_argument("--features", default="data/features_catalog.json", help="Path to features JSON")
    p_score.add_argument("--top", type=int, default=15, help="Number of top features to display")
    p_score.set_defaults(func=cmd_score)

    # Validate command
    p_val = subparsers.add_parser("validate", help="Benchmark model output against human PM baselines")
    p_val.add_argument("--features", default="data/features_catalog.json", help="Path to features JSON")
    p_val.add_argument("--baselines", default="data/pm_baselines.json", help="Path to PM baselines JSON")
    p_val.set_defaults(func=cmd_validate)

    # Roadmap command
    p_road = subparsers.add_parser("roadmap", help="Generate quarterly roadmap allocation")
    p_road.add_argument("--features", default="data/features_catalog.json", help="Path to features JSON")
    p_road.add_argument("--capacity", type=float, default=45.0, help="Quarterly capacity in eng person-weeks")
    p_road.add_argument("--quarter", default="Q3 Roadmap Review", help="Quarter name")
    p_road.set_defaults(func=cmd_roadmap)

    # Export command
    p_exp = subparsers.add_parser("export", help="Export executive markdown briefing document")
    p_exp.add_argument("--features", default="data/features_catalog.json", help="Path to features JSON")
    p_exp.add_argument("--baselines", default="data/pm_baselines.json", help="Path to PM baselines JSON")
    p_exp.add_argument("--capacity", type=float, default=45.0, help="Quarterly capacity in eng person-weeks")
    p_exp.add_argument("--quarter", default="Q3 Roadmap Review", help="Quarter name")
    p_exp.add_argument("--output", default="ROADMAP_REVIEW_BRIEF.md", help="Output markdown path")
    p_exp.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
