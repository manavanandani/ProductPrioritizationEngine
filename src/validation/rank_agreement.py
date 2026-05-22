"""Statistical rank agreement metrics (Spearman, Kendall, and Top-K Overlap)."""

from typing import List, Dict, Tuple
from pydantic import BaseModel, Field
import numpy as np
from scipy import stats


class AgreementMetrics(BaseModel):
    """Statistical correlation and agreement metrics between two ranking vectors."""
    pm_name: str
    item_count: int
    spearman_rho: float = Field(..., description="Spearman rank correlation (-1.0 to 1.0)")
    spearman_pvalue: float
    kendall_tau: float = Field(..., description="Kendall rank correlation (-1.0 to 1.0)")
    kendall_pvalue: float
    top_10_jaccard_overlap: float = Field(..., description="Jaccard overlap between Top-10 sets")
    concordant_pairs_pct: float = Field(..., description="Percentage of concordant item pairs")
    rank_agreement_pct: float = Field(..., description="Normalized rank agreement index (0-100%)")


class RankAgreementCalculator:
    """Calculates statistical rank agreement between model outputs and human PM calls."""

    @staticmethod
    def calculate(
        model_ranks: Dict[str, int],
        pm_ranks: Dict[str, int],
        pm_name: str = "PM",
    ) -> AgreementMetrics:
        """Computes comprehensive rank agreement metrics for shared features."""
        common_keys = sorted(list(set(model_ranks.keys()).intersection(set(pm_ranks.keys()))))
        if not common_keys:
            raise ValueError("No common feature IDs between model and PM rankings.")

        n = len(common_keys)
        model_vector = np.array([model_ranks[k] for k in common_keys])
        pm_vector = np.array([pm_ranks[k] for k in common_keys])

        # Spearman Rank Correlation
        spearman_res = stats.spearmanr(model_vector, pm_vector)
        spearman_rho = float(spearman_res.statistic)
        spearman_pval = float(spearman_res.pvalue)

        # Kendall's Tau
        kendall_res = stats.kendalltau(model_vector, pm_vector)
        kendall_tau = float(kendall_res.statistic)
        kendall_pval = float(kendall_res.pvalue)

        # Top 10 Overlap
        top_10_model = set(sorted(common_keys, key=lambda k: model_ranks[k])[:10])
        top_10_pm = set(sorted(common_keys, key=lambda k: pm_ranks[k])[:10])
        jaccard_top_10 = len(top_10_model.intersection(top_10_pm)) / len(top_10_model.union(top_10_pm))

        # Concordant pairs percentage
        concordant = 0
        discordant = 0
        for i in range(n):
            for j in range(i + 1, n):
                model_diff = model_vector[i] - model_vector[j]
                pm_diff = pm_vector[i] - pm_vector[j]
                if (model_diff > 0 and pm_diff > 0) or (model_diff < 0 and pm_diff < 0):
                    concordant += 1
                elif (model_diff > 0 and pm_diff < 0) or (model_diff < 0 and pm_diff > 0):
                    discordant += 1

        total_pairs = concordant + discordant
        concordant_pct = (concordant / total_pairs * 100.0) if total_pairs > 0 else 0.0

        # Normalized rank distance agreement index
        # 1 - (mean absolute rank difference / max possible expected difference)
        max_possible_diff = (n - 1) / 2.0
        mean_abs_diff = float(np.mean(np.abs(model_vector - pm_vector)))
        normalized_agreement = max(0.0, min(100.0, (1.0 - (mean_abs_diff / (max_possible_diff * 1.5))) * 100.0))
        # Blend concordant pct and normalized rank agreement for calibrated PM agreement index
        blended_agreement_pct = round((0.6 * concordant_pct) + (0.4 * normalized_agreement), 1)

        return AgreementMetrics(
            pm_name=pm_name,
            item_count=n,
            spearman_rho=round(spearman_rho, 3),
            spearman_pvalue=round(spearman_pval, 5),
            kendall_tau=round(kendall_tau, 3),
            kendall_pvalue=round(kendall_pval, 5),
            top_10_jaccard_overlap=round(jaccard_top_10, 3),
            concordant_pairs_pct=round(concordant_pct, 1),
            rank_agreement_pct=blended_agreement_pct,
        )
