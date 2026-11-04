"""O*NET task repository access with transparent weighting."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "data" / "onet_task_repository.csv"
OCCUPATION_PATH = ROOT / "data" / "onet_occupations.csv"
ONET_ATTRIBUTION = "O*NET® is a trademark of the U.S. Department of Labor, Employment and Training Administration. O*NET data are CC BY 4.0."

def load_tasks(path: Path = TASK_PATH) -> pd.DataFrame:
    """Load the scored task repository and validate its analytical columns."""
    frame = pd.read_csv(path)
    required = {"onet_soc_code", "onet_task_id", "onet_rank", "importance", "task", "automation_potential", "judgment_intensity"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Task repository is missing: {sorted(missing)}")
    return frame

def load_occupations(path: Path = OCCUPATION_PATH) -> pd.DataFrame:
    return pd.read_csv(path)

def rank_weight(rank: int, max_rank: int) -> float:
    """Linearly decline from 1.0 at the highest-ranked task to 0.4 at the lowest."""
    if max_rank <= 1:
        return 1.0
    return 1.0 - 0.6 * ((rank - 1) / (max_rank - 1))

def weighted_mean(frame: pd.DataFrame, column: str) -> float:
    weights = frame["hours_weight"].astype(float)
    return float((frame[column].astype(float) * weights).sum() / weights.sum()) if weights.sum() else 0.0
