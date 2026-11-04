"""Task classifications, capture factors, and family comparison metrics."""
from __future__ import annotations
import pandas as pd
from .onet_repository import weighted_mean

CAPTURE_FACTORS = {"Automated": 0.80, "Augmented": 0.40, "Human-Led": 0.10}
COLORS = {"Automated": "#45C6A8", "Augmented": "#7D8CFF", "Human-Led": "#F4B860"}

def categorise(automation: float, judgment: float) -> str:
    if judgment >= 0.70:
        return "Human-Led"
    if automation >= 0.65 and judgment < 0.40:
        return "Automated"
    return "Augmented"

def enrich_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    result = tasks.copy()
    result["task_bucket"] = [categorise(a, j) for a, j in zip(result.automation_potential, result.judgment_intensity)]
    result["capture_factor"] = result.task_bucket.map(CAPTURE_FACTORS)
    result["time_savings"] = result.automation_potential * result.capture_factor
    return result

def overall_time_savings(tasks: pd.DataFrame) -> float:
    return weighted_mean(enrich_tasks(tasks), "time_savings")

def quadrant(automation: float, judgment: float) -> str:
    if automation >= .5 and judgment < .5: return "Automate and redeploy"
    if automation >= .5: return "Augment and elevate"
    if judgment >= .5: return "Human advantage"
    return "Optimise and sustain"
