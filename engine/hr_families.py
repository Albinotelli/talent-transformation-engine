"""The 15 triangulated HR job families and their O*NET task references."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import pandas as pd

from .onet_repository import load_occupations, load_tasks, rank_weight, weighted_mean

Coverage = Literal["Strong", "Good", "Partial"]

@dataclass(frozen=True)
class HRFamily:
    name: str
    label: str
    description: str
    frameworks: str
    occupations: tuple[str, ...]
    coverage: Coverage

@dataclass
class FamilyProfile:
    family: HRFamily
    tasks: pd.DataFrame
    default_salary: float
    automation_potential: float
    judgment_intensity: float
    time_savings_potential: float

_ROWS = [
 ("HR Business Partnering","HRBP","Aligns people strategy and business decisions.","OPM HR Management; CIPD People practice",("11-3121.00","13-1071.00"),"Good"),
 ("Talent Acquisition and Recruitment","TA","Sources, assesses and appoints talent.","OPM Recruitment & Placement; CIPD Resourcing; university Talent Acquisition",("13-1071.00","11-3121.00"),"Strong"),
 ("Employee Relations","ER","Resolves workplace concerns, policy and conduct matters.","OPM Employee Relations; CIPD Employee relations",("13-1071.00","11-3121.00"),"Good"),
 ("Labor Relations","LR","Manages collective bargaining and union relationships.","OPM Labor Relations; CIPD Employee relations",("13-1075.00",),"Strong"),
 ("Compensation and Job Architecture","Comp","Designs pay, classification and job structures.","OPM Classification & Compensation; CIPD Reward",("13-1141.00",),"Strong"),
 ("Benefits and Leave Administration","Benefits","Administers benefits, leave and eligibility.","OPM Employee Benefits; CIPD Reward",("13-1141.00","43-4161.00"),"Good"),
 ("Payroll and Time","Payroll","Processes pay, timekeeping and payroll controls.","University HR Operations; O*NET payroll occupation",("43-3051.00",),"Strong"),
 ("Learning and Development","L&D","Builds workforce capability through learning.","OPM Human Resource Development; CIPD L&D",("13-1151.00",),"Strong"),
 ("Talent Management and Performance","Talent","Runs performance and succession processes.","OPM Performance Management; CIPD Talent management",("13-1071.00","11-3121.00"),"Good"),
 ("Organisation Development and Design","OD&D","Designs organisations, roles and change interventions.","CIPD OD&D; university Talent & Organizational Development",("19-3032.00","11-3121.00"),"Good"),
 ("HR Operations and Shared Services","HR Ops","Delivers reliable employee services and records.","University HR Operations; OPM HR Information Systems",("43-4161.00","13-1071.00"),"Good"),
 ("HR Information Systems and Technology","HRIS","Enables HR data, systems and digital workflow.","OPM HR Information Systems; university HR Operations",("43-4161.00","13-1071.00"),"Partial"),
 ("People Analytics and Workforce Planning","Analytics","Turns workforce data into planning insight.","CIPD People analytics & Workforce planning; OPM HR Information Systems",("13-1071.00","19-3032.00"),"Good"),
 ("Diversity, Equity and Inclusion","DEI","Advances equitable people systems and compliance.","CIPD EDI; O*NET Equal Opportunity Representatives",("13-1041.03",),"Strong"),
 ("Employee Experience and Wellbeing","EX","Improves the employee journey, voice and wellbeing.","CIPD Employee experience & Wellbeing; university HR architecture",("13-1071.00","11-3121.00"),"Partial"),
]
HR_FAMILIES = {row[1]: HRFamily(*row) for row in _ROWS}

def get_family_profile(label: str, tasks: pd.DataFrame | None = None) -> FamilyProfile:
    if label not in HR_FAMILIES:
        raise KeyError(f"Unknown family: {label}")
    family = HR_FAMILIES[label]
    all_tasks = load_tasks() if tasks is None else tasks.copy()
    subset = all_tasks[all_tasks["family_label"].str.split("|").apply(lambda values: label in values)].copy()
    if subset.empty:
        raise ValueError(f"No task references for {label}")
    subset["emphasis_weight"] = subset["family_label"].str.split("|").apply(lambda values: 1.0 if values[0] == label else 0.5)
    subset["rank_weight"] = subset.groupby("onet_soc_code")["onet_rank"].transform(lambda ranks: ranks.apply(lambda r: rank_weight(int(r), int(ranks.max()))))
    subset["hours_weight"] = subset["importance"].astype(float) * subset["rank_weight"] * subset["emphasis_weight"]
    occupations = load_occupations().set_index("onet_soc_code")
    subset["median_wage"] = subset["onet_soc_code"].map(occupations["bls_median_annual_wage"])
    salary = weighted_mean(subset.dropna(subset=["median_wage"]), "median_wage")
    from .task_analyzer import overall_time_savings
    return FamilyProfile(family, subset, salary, weighted_mean(subset, "automation_potential"), weighted_mean(subset, "judgment_intensity"), overall_time_savings(subset))
