"""Skill transition map and the explicitly original Expertise Pipeline Gap."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
import pandas as pd
from .onet_repository import weighted_mean

@dataclass(frozen=True)
class PipelineGap:
    index: float; band: str; action: str; entry_level_erosion: float; judgment_premium: float

_ACTIONS = [(30,"Low","Protect learning-by-doing and monitor adoption."),(50,"Moderate","Add supervised practice and apprenticeship rotations."),(70,"Elevated","Fund deliberate judgment-building pathways before redesigning entry roles."),(101,"Critical","Ring-fence developmental work and redesign the expert pipeline now.")]
def expertise_pipeline_gap(tasks: pd.DataFrame, adoption_rate: float) -> PipelineGap:
    low = tasks[tasks.judgment_intensity < .40]
    erosion = adoption_rate * (weighted_mean(low, "automation_potential") if not low.empty else 0.0)
    premium = min(1.0, weighted_mean(tasks, "judgment_intensity") * (1 + .5 * adoption_rate))
    index = 100 * sqrt(erosion * premium)
    band, action = next((b,a) for limit,b,a in _ACTIONS if index < limit)
    return PipelineGap(index, band, action, erosion, premium)

def skill_transition(label: str, adoption_rate: float) -> pd.DataFrame:
    legacy = ["Transaction processing", "Policy lookup", "Manual reporting", "Template drafting"]
    emerging = ["AI workflow design", "Evidence-based judgment", "Exception governance", "Workforce insight storytelling"]
    return pd.DataFrame([{"skill": s, "direction": "Declining", "shift": -round(v*adoption_rate)} for s,v in zip(legacy,[45,35,30,25])] + [{"skill": s, "direction": "Emerging", "shift": round(v*adoption_rate)} for s,v in zip(emerging,[55,45,35,30])])
