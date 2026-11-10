"""Talent Transformation Engine — executive HR AI scenario dashboard."""
from __future__ import annotations

import io
from dataclasses import replace

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine.capacity_model import CapacityInputs, calculate_capacity
from engine.hr_families import HR_FAMILIES, get_family_profile
from engine.onet_repository import ONET_ATTRIBUTION, load_tasks
from engine.skills_mapper import expertise_pipeline_gap, skill_transition
from engine.task_analyzer import COLORS, enrich_tasks, quadrant

st.set_page_config(page_title="Talent Transformation Engine", page_icon="◈", layout="wide")


def theme(dark: bool) -> None:
    bg, panel, text, muted, line = ("#101827", "#172234", "#F3F6FA", "#AAB9D1", "#2A3D5E") if dark else ("#F7F8FC", "#FFFFFF", "#172234", "#63718A", "#D9E0EB")
    st.markdown(
        """<style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono&family=DM+Sans:wght@400;500;700&family=Libre+Baskerville:wght@400;700&display=swap');
        .stApp {background:%s;color:%s;font-family:'DM Sans',sans-serif} h1,h2,h3 {font-family:'Libre Baskerville',serif!important;color:%s!important}
        [data-testid='stSidebar'] {background:%s} [data-testid='stMetric'] {background:%s;border:1px solid %s;padding:14px;border-radius:7px}
        .eyebrow {color:#38C6B7;font:.72rem 'DM Mono';letter-spacing:.13em;text-transform:uppercase}
        .subtle {color:%s}.brief {border:1px solid %s;border-left:4px solid #38C6B7;border-radius:7px;background:%s;padding:18px 22px;margin:14px 0 22px}.brief h3 {margin:0 0 7px}.brief p {margin:4px 0}
        </style>""" % (bg, text, text, panel, panel, line, muted, line, panel),
        unsafe_allow_html=True,
    )


def validate_upload(uploaded: object) -> tuple[pd.DataFrame | None, str | None]:
    if uploaded is None:
        return None, None
    try:
        raw = uploaded.getvalue()
        if b"\x00" in raw[:4096]:
            return None, "This appears to be a binary file; upload a UTF-8 CSV."
        frame = pd.read_csv(io.BytesIO(raw))
    except (UnicodeDecodeError, pd.errors.ParserError, OSError) as error:
        return None, "Could not read this CSV: {}".format(error)
    required = {"task", "automation_potential", "judgment_intensity"}
    missing = required.difference(frame.columns)
    if missing:
        return None, "Missing required columns: {}.".format(", ".join(sorted(missing)))
    if not frame["automation_potential"].between(0, 1).all() or not frame["judgment_intensity"].between(0, 1).all():
        return None, "automation_potential and judgment_intensity must be numbers from 0 to 1."
    frame["importance"] = frame.get("importance", 1.0)
    frame["hours_weight"] = frame["importance"]
    return frame, None


def weighted(frame: pd.DataFrame, column: str) -> float:
    return float((frame[column] * frame["hours_weight"]).sum() / frame["hours_weight"].sum())


def all_families(tasks: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, family in HR_FAMILIES.items():
        profile = get_family_profile(label, tasks)
        rows.append({"Label": label, "Family": family.name, "AI exposure": profile.automation_potential,
                     "Cognitive intensity": profile.judgment_intensity, "Time-savings potential": profile.time_savings_potential,
                     "Coverage": family.coverage, "Zone": quadrant(profile.automation_potential, profile.judgment_intensity)})
    return pd.DataFrame(rows)


def figure_style(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(title=title, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_family="DM Sans", margin=dict(l=20, r=20, t=55, b=30), legend_title_text="")
    return fig


def pilot_plan() -> pd.DataFrame:
    return pd.DataFrame(
        [("0–30 days", "Validate task scope and baseline", "HR process owner + Data & AI", "Task time, quality and control baseline"),
         ("31–60 days", "Run a bounded workflow pilot", "Product owner + HR operations", "Adoption, cycle time and exceptions"),
         ("61–90 days", "Decide on scale and capability actions", "HR leadership + risk partners", "Realised capacity, fairness and learning impact")],
        columns=["Timing", "Action", "Accountable owner", "Decision evidence"],
    )


with st.sidebar:
    st.markdown("<div class='eyebrow'>Scenario controls</div>", unsafe_allow_html=True)
    dark = st.toggle("Dark canvas", value=True)
    theme(dark)
    label = st.selectbox("HR job family", list(HR_FAMILIES), format_func=lambda item: "{} · {}".format(item, HR_FAMILIES[item].name))
    profile = get_family_profile(label)
    team = st.slider("Team size", 1, 1000, 50)
    salary = st.number_input("Average salary (USD)", 30000, 350000, int(profile.default_salary), 1000)
    adoption = st.slider("AI adoption rate", 0, 100, 60) / 100
    with st.expander("Reinvestment assumptions", expanded=True):
        maturity = st.slider("Change-management maturity", 0, 100, 55) / 100
        growth = st.slider("Growth vs. efficiency priority", 0, 100, 50) / 100
    with st.expander("Cost and time assumptions"):
        multiplier = st.slider("Loaded-cost multiplier", 1.0, 2.5, 1.30, .05)
        tooling = st.number_input("AI tooling cost / seat / year", 0, 10000, 1200, 100)
        hours = st.slider("Weekly hours", 20, 60, 40)
        weeks = st.slider("Productive weeks / year", 40, 52, 46)
    with st.expander("Custom task inventory"):
        template = pd.DataFrame({"task": ["Example task"], "automation_potential": [.55], "judgment_intensity": [.40], "importance": [1.0]})
        st.download_button("Download CSV template", template.to_csv(index=False), "task_inventory_template.csv", "text/csv")
        uploaded = st.file_uploader("Upload CSV", type=["csv"])

custom, upload_error = validate_upload(uploaded)
if upload_error:
    st.sidebar.error(upload_error)
tasks = enrich_tasks(profile.tasks if custom is None else custom)
time_savings = weighted(tasks, "time_savings")
inputs = CapacityInputs(team, hours, weeks, time_savings, adoption, salary, multiplier, maturity, growth, tooling)
result = calculate_capacity(inputs)
baseline = calculate_capacity(replace(inputs, adoption_rate=0, ai_tooling_cost_per_seat=0))
gap = expertise_pipeline_gap(tasks, adoption)
exposure, cognition = weighted(tasks, "automation_potential"), weighted(tasks, "judgment_intensity")
zone = quadrant(exposure, cognition)
hourly_cost = salary * multiplier / (hours * weeks)

play = {"Automate and redeploy": "Pilot automation with deliberate capacity redeployment",
        "Augment and elevate": "Pilot AI augmentation with accountable human oversight",
        "Human advantage": "Use AI for preparation; protect accountable professional judgment",
        "Optimise and sustain": "Optimise service operations before major automation"}[zone]
guardrail = "Protect supervised practice and shadowing." if gap.index >= 30 else "Monitor learning pathways as adoption grows."

st.markdown("<div class='eyebrow'>People strategy scenario modelling</div>", unsafe_allow_html=True)
st.title("Talent Transformation Engine")
st.markdown("<p class='subtle'>Translate task-level AI exposure into capacity, capability and workforce-pipeline choices across the HR function.</p>", unsafe_allow_html=True)
st.markdown("""<div class='brief'><h3>%s: %s</h3><p><b>Why now:</b> %s annual hours of potential capacity · %s O*NET coverage · %s pipeline gap (%s/100).</p><p><b>Guardrails:</b> Keep accountable human ownership of consequential employment decisions. %s</p></div>""" % (play, profile.family.name, format(result.annual_hours_freed, ",.0f"), profile.family.coverage, gap.band, format(gap.index, ".0f"), guardrail), unsafe_allow_html=True)

st.markdown("#### Scenario at a glance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hours freed / week", format(result.weekly_hours_freed, ",.0f"), format(time_savings, ".0%") + " task time-savings potential")
c2.metric("FTE capacity reinvested", format(result.net_fte_reinvestment, ".1f"), format(result.fte_capacity_saved, ".1f") + " gross")
c3.metric("Cost-per-outcome efficiency", format(result.efficiency_gain, ".1%"), "net of AI tooling")
c4.metric("Capacity leak", format(result.leak_rate, ".0%"), "freed capacity not assigned")

st.markdown("#### Baseline vs. selected scenario")
scenario_table = pd.DataFrame({"Measure": ["AI adoption", "Annual hours freed", "Retained FTE capacity", "Cost / outcome", "Pipeline gap"],
    "Baseline": ["0%", "0", "0.0", "USD " + format(baseline.cost_per_outcome_before, ",.2f"), "0"],
    "Selected scenario": [format(adoption, ".0%"), format(result.annual_hours_freed, ",.0f"), format(result.net_fte_reinvestment, ".1f"), "USD " + format(result.cost_per_outcome_after, ",.2f"), "{} · {}".format(format(gap.index, ".0f"), gap.band)]})
st.dataframe(scenario_table, width="stretch", hide_index=True)

left, right = st.columns(2)
with left:
    breakdown = tasks.groupby("task_bucket", as_index=False).hours_weight.sum()
    breakdown["share"] = breakdown.hours_weight / breakdown.hours_weight.sum()
    fig = px.pie(breakdown, names="task_bucket", values="share", hole=.62, color="task_bucket", color_discrete_map=COLORS)
    st.plotly_chart(figure_style(fig, "Task evolution breakdown"), width="stretch")
with right:
    allocation = pd.DataFrame({"Allocation": ["Leak", "Core efficiency", "Growth / innovation", "Total freed"],
        "Hours": [result.leak_hours, result.core_hours, result.growth_hours, result.annual_hours_freed],
        "Share": [result.leak_rate, (1-result.leak_rate)*(1-growth), (1-result.leak_rate)*growth, 1]})
    fig = px.bar(allocation, x="Hours", y="Allocation", orientation="h", text=allocation.apply(lambda row: "{} hrs<br>{:.0%}".format(format(row["Hours"], ",.0f"), row["Share"]), axis=1), color="Allocation",
                 color_discrete_map={"Leak": "#E76F51", "Core efficiency": "#7D8CFF", "Growth / innovation": "#38C6B7", "Total freed": "#AAB9D1"})
    fig.update_traces(textposition="outside")
    st.plotly_chart(figure_style(fig, "Annual capacity allocation · capacity equivalent, not cash savings"), width="stretch")

families = all_families(load_tasks())
fig = px.scatter(families, x="AI exposure", y="Cognitive intensity", hover_name="Family", hover_data={"Label": True, "Coverage": True, "Time-savings potential": ":.1%"}, color="Zone", color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_traces(marker={"size": 12, "opacity": .78})
selected = families[families.Label == label]
fig.add_trace(go.Scatter(x=selected["AI exposure"], y=selected["Cognitive intensity"], mode="markers+text", text=[label], textposition="middle right", marker={"size": 19, "color": "#F4B840", "symbol": "diamond"}, name="Selected family"))
fig.add_vline(x=.5, line_dash="dot"); fig.add_hline(y=.5, line_dash="dot")
st.plotly_chart(figure_style(fig, "Cognitive intensity vs. AI exposure"), width="stretch")
st.info("**{}** sits in **{}**: AI exposure is {}; cognitive intensity is {}. The recommendation above translates this position into an action.".format(profile.family.name, zone, format(exposure, ".0%"), format(cognition, ".0%")))

ranked = families.sort_values("Time-savings potential")
fig = px.bar(ranked, x="Time-savings potential", y="Label", orientation="h", color="Zone", color_discrete_sequence=px.colors.qualitative.Safe, text=ranked["Time-savings potential"].map("{:.0%}".format))
fig.update_traces(textposition="outside")
st.plotly_chart(figure_style(fig, "HR families ranked by time-savings potential"), width="stretch")

tabs = st.tabs(["Decision drivers", "Sensitivity", "Skills & pipeline", "90-day pilot", "Risk register", "Evidence & methodology"])
with tabs[0]:
    st.markdown("#### Which tasks drive this result?")
    drivers = tasks.copy()
    drivers["Capacity contribution"] = drivers["hours_weight"] * drivers["time_savings"]
    drivers["Pipeline contribution"] = np.where(drivers["judgment_intensity"] < .40, drivers["hours_weight"] * drivers["automation_potential"] * adoption, 0)
    columns = [item for item in ["task", "task_bucket", "automation_potential", "judgment_intensity", "Capacity contribution", "Pipeline contribution", "exposure_rationale"] if item in drivers]
    st.dataframe(drivers.sort_values("Capacity contribution", ascending=False)[columns], width="stretch", hide_index=True)
    st.caption("Capacity contribution is a weighted prioritisation signal, not a claim about realised time savings.")
with tabs[1]:
    st.markdown("#### Sensitivity to adoption and change maturity")
    sensitivity = []
    for tested_adoption in np.linspace(0, 1, 5):
        for tested_maturity in (.30, .55, .80):
            scenario = calculate_capacity(replace(inputs, adoption_rate=float(tested_adoption), change_maturity=tested_maturity))
            sensitivity.append({"Adoption": tested_adoption, "Change maturity": format(tested_maturity, ".0%"), "Retained FTE capacity": scenario.net_fte_reinvestment})
    fig = px.line(pd.DataFrame(sensitivity), x="Adoption", y="Retained FTE capacity", color="Change maturity", markers=True)
    fig.update_xaxes(tickformat=".0%")
    st.plotly_chart(figure_style(fig, "Retained capacity under different assumptions"), width="stretch")
    st.caption("Higher change maturity reduces capacity leakage; these are scenario assumptions, not forecasts.")
with tabs[2]:
    skills = skill_transition(label, adoption)
    fig = px.bar(skills, x="shift", y="skill", orientation="h", color="direction", color_discrete_map={"Declining": "#E76F51", "Emerging": "#38C6B7"})
    st.plotly_chart(figure_style(fig, "Skills taxonomy evolution at current adoption"), width="stretch")
    a, b, c = st.columns(3)
    a.metric("Expertise Pipeline Gap", format(gap.index, ".0f") + "/100", gap.band)
    b.metric("Entry-level erosion", format(gap.entry_level_erosion, ".0%"), "low-judgment work exposed")
    c.metric("Judgment premium", format(gap.judgment_premium, ".0%"), "contextual judgment value")
    low = tasks[tasks["judgment_intensity"] < .40].sort_values("automation_potential", ascending=False)
    st.markdown("**Low-judgment tasks most exposed to AI**")
    st.dataframe(low[[item for item in ["task", "automation_potential", "exposure_rationale"] if item in low]], width="stretch", hide_index=True)
    st.info(gap.action)
with tabs[3]:
    st.markdown("#### {}: proposed 90-day pilot".format(profile.family.name))
    st.dataframe(pilot_plan(), width="stretch", hide_index=True)
    st.markdown("**Decision gate:** scale only if the pilot demonstrates realised capacity, maintained service quality, and acceptable fairness, privacy and learning-pathway outcomes.")
with tabs[4]:
    risks = [("Employment and fairness", "AI influences a consequential people decision.", "Human decision owner, testing and documented escalation.", "High"),
        ("Data and privacy", "Sensitive employee or applicant data enters a workflow.", "Minimise data, access controls, retention and privacy review.", "High"),
        ("Capacity leakage", "Freed time is not deliberately reassigned.", "Named reinvestment owner and monthly realised-capacity review.", "Medium"),
        ("Evidence quality", "{} O*NET coverage may not reflect local work design.".format(profile.family.coverage), "Validate task mix with practitioners and time-use data.", "Medium")]
    if gap.index >= 30:
        risks.append(("Expertise pipeline", "Foundational work may disappear before judgment develops.", "Protect rotations, shadowing and supervised exceptions.", "High" if gap.index >= 50 else "Medium"))
    st.dataframe(pd.DataFrame(risks, columns=["Risk", "Trigger", "Mitigation", "Priority"]), width="stretch", hide_index=True)
    st.caption("This is a governance prompt for human review. It does not replace legal, privacy, employee-relations or labour-relations advice.")
with tabs[5]:
    st.markdown("#### Evidence confidence")
    st.metric("O*NET coverage", profile.family.coverage, "Strong = dedicated occupation; Good = related occupations; Partial = material source gap")
    st.markdown("#### Task inventory and source rationale")
    columns = [item for item in ["onet_task_id", "occupation", "task", "exposure_rating", "automation_potential", "judgment_intensity", "exposure_category", "exposure_rationale", "task_bucket"] if item in tasks]
    st.dataframe(tasks[columns], width="stretch", hide_index=True)
    st.download_button("Download task inventory", tasks.to_csv(index=False), "{}_tasks.csv".format(label.lower()), "text/csv")
    st.markdown("""#### Methodology
**Current scenario:** {} people × {} weekly hours × {} task time-savings potential × {} adoption = **{} hours freed per week**.

`leak = clamp(.40 − .30 × maturity + .10 × (1 − adoption), .05, .60)` = **{}**. The retained capacity split is **{} core efficiency / {} growth**.

Exposure ratings are manually applied from Eloundou et al. (2023): E0=.08, E1=.85, E2=.55, E3=.45. Judgment intensity is a separate internal 0–1 measure. {}""".format(team, hours, format(time_savings, ".1%"), format(adoption, ".0%"), format(result.weekly_hours_freed, ",.0f"), format(result.leak_rate, ".1%"), format(1-growth, ".0%"), format(growth, ".0%"), ONET_ATTRIBUTION))
