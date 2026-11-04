"""Capacity, allocation and cost-per-outcome calculations."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CapacityInputs:
    team_size: int; weekly_hours: float; productive_weeks_per_year: float; time_savings_potential: float
    adoption_rate: float; salary: float; loaded_cost_multiplier: float; change_maturity: float
    growth_priority: float; ai_tooling_cost_per_seat: float

@dataclass(frozen=True)
class CapacityResult:
    weekly_hours_freed: float; annual_hours_freed: float; fte_capacity_saved: float; financial_value: float
    leak_rate: float; leak_hours: float; core_hours: float; growth_hours: float; net_fte_reinvestment: float
    cost_per_outcome_before: float; cost_per_outcome_after: float; efficiency_gain: float

def calculate_capacity(i: CapacityInputs) -> CapacityResult:
    annual_hours_per_fte = i.weekly_hours * i.productive_weeks_per_year
    weekly_freed = i.team_size * i.weekly_hours * i.time_savings_potential * i.adoption_rate
    annual_freed = weekly_freed * i.productive_weeks_per_year
    fte = annual_freed / annual_hours_per_fte if annual_hours_per_fte else 0.0
    hourly = i.salary * i.loaded_cost_multiplier / annual_hours_per_fte if annual_hours_per_fte else 0.0
    leak = min(.60, max(.05, .40 - .30 * i.change_maturity + .10 * (1 - i.adoption_rate)))
    retained = annual_freed * (1 - leak)
    core = retained * (1 - i.growth_priority)
    growth = retained * i.growth_priority
    loaded_cost = i.team_size * i.salary * i.loaded_cost_multiplier
    team_hours = i.team_size * annual_hours_per_fte
    tooling = i.team_size * i.ai_tooling_cost_per_seat
    before = loaded_cost / team_hours if team_hours else 0.0
    after = (loaded_cost + tooling) / (team_hours + retained) if team_hours + retained else 0.0
    return CapacityResult(weekly_freed, annual_freed, fte, annual_freed * hourly, leak, annual_freed * leak, core, growth, retained / annual_hours_per_fte if annual_hours_per_fte else 0.0, before, after, 1 - after / before if before else 0.0)
