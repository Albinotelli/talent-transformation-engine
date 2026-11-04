"""Talent Transformation Engine — an auditable HR scenario-modelling dashboard."""
from __future__ import annotations

import io
from pathlib import Path
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

def css(dark: bool) -> None:
    bg, panel, text, muted, line = ("#101418", "#182027", "#F3EEE5", "#A8B2B8", "#34434B") if dark else ("#F7F4EE", "#FFFFFF", "#182027", "#5F6B72", "#DFDDD5")
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono&family=DM+Sans:wght@400;500;700&family=Libre+Baskerville:wght@400;700&display=swap');
    .stApp {{background:{bg};color:{text};font-family:'DM Sans',sans-serif}} h1,h2,h3,.metric-value {{font-family:'Libre Baskerville',serif!important;color:{text}!important}}
    [data-testid='stSidebar'] {{background:{panel}}} [data-testid='stMetric'] {{background:{panel};border:1px solid {line};padding:16px;border-radius:5px}}
    .eyebrow {{font-family:'DM Mono';font-size:.72rem;color:#45C6A8;letter-spacing:.12em;text-transform:uppercase}} .intro {{color:{muted};max-width:900px;font-size:1.05rem}}
    .notice {{border-left:3px solid #45C6A8;background:{panel};padding:16px 20px;margin:14px 0;color:{text}}} .small {{color:{muted};font-size:.82rem}}
    </style>""", unsafe_allow_html=True)

def validate_upload(uploaded: object) -> tuple[pd.DataFrame | None, str | None]:
    if uploaded is None: return None, None
    try:
        raw = uploaded.getvalue()
        if b"\x00" in raw[:4096]: return None, "This appears to be a binary file; upload a UTF-8 CSV."
        frame = pd.read_csv(io.BytesIO(raw))
    except (UnicodeDecodeError, pd.errors.ParserError, OSError) as error:
        return None, f"Could not read this CSV: {error}"
    needed = {"task", "automation_potential", "judgment_intensity"}
    missing = needed - set(frame.columns)
    if missing: return None, f"Missing required columns: {', '.join(sorted(missing))}."
    if not frame.automation_potential.between(0, 1).all() or not frame.judgment_intensity.between(0, 1).all(): return None, "automation_potential and judgment_intensity must be numbers from 0 to 1."
    frame["importance"] = frame.get("importance", 1.0); frame["onet_rank"] = frame.get("onet_rank", 1); frame["hours_weight"] = frame["importance"]
    return frame, None

def family_comparison(tasks: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for label, family in HR_FAMILIES.items():
        p=get_family_profile(label, tasks)
        rows.append({"Label":label,"Family":family.name,"AI exposure":p.automation_potential,"Cognitive intensity":p.judgment_intensity,"Time-savings potential":p.time_savings_potential,"Default salary":p.default_salary,"Coverage":family.coverage,"Zone":quadrant(p.automation_potential,p.judgment_intensity)})
    return pd.DataFrame(rows)

def chart_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(title=title, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="DM Sans", margin=dict(l=20,r=20,t=55,b=20), legend_title_text="")
    return fig

with st.sidebar:
    st.markdown("<div class='eyebrow'>Scenario controls</div>", unsafe_allow_html=True)
    dark=st.toggle("Dark canvas", value=True); css(dark)
    label=st.selectbox("HR job family", list(HR_FAMILIES), format_func=lambda x:f"{x} · {HR_FAMILIES[x].name}")
    profile=get_family_profile(label)
    team=st.slider("Team size",1,1000,50)
    salary=st.number_input("Average salary (USD)",30000,350000,int(profile.default_salary),1000)
    adoption=st.slider("AI adoption rate",0,100,60)/100
    with st.expander("Reinvestment assumptions",True):
        maturity=st.slider("Change-management maturity",0,100,55)/100
        growth=st.slider("Growth vs efficiency priority",0,100,50)/100
    with st.expander("Cost and time assumptions"):
        multiplier=st.slider("Loaded-cost multiplier",1.0,2.5,1.30,.05)
        tooling=st.number_input("AI tooling cost / seat / year",0,10000,1200,100)
        hours=st.slider("Weekly hours",20,60,40)
        weeks=st.slider("Productive weeks / year",40,52,46)
    with st.expander("Custom task inventory"):
        template=pd.DataFrame({"task":["Example task"],"automation_potential":[.55],"judgment_intensity":[.40],"importance":[1.0]})
        st.download_button("Download CSV template",template.to_csv(index=False),"task_inventory_template.csv","text/csv")
        uploaded=st.file_uploader("Upload CSV",type=["csv"])

custom, upload_error=validate_upload(uploaded)
if upload_error: st.sidebar.error(upload_error)
tasks=profile.tasks if custom is None else custom
tasks=enrich_tasks(tasks)
time_savings=float((tasks.time_savings*tasks.hours_weight).sum()/tasks.hours_weight.sum())
inputs=CapacityInputs(team,hours,weeks,time_savings,adoption,salary,multiplier,maturity,growth,tooling)
result=calculate_capacity(inputs)
gap=expertise_pipeline_gap(tasks,adoption)

st.markdown("<div class='eyebrow'>People strategy scenario modelling</div>",unsafe_allow_html=True)
st.title("Talent Transformation Engine")
st.markdown("<p class='intro'>Translate task-level AI exposure into capacity, capability and workforce-pipeline choices across the HR function.</p>",unsafe_allow_html=True)
st.markdown("<div class='notice'><b>What this is and isn’t.</b> O*NET task statements and occupation references are real public source material. Exposure ratings and judgment intensity are analyst-applied interpretations of a published rubric, not observed AI productivity data. This is a framework demonstrator for structured discussion, not a validated forecasting tool or a substitute for legal, workforce or employment decisions.</div>",unsafe_allow_html=True)

c1,c2,c3,c4=st.columns(4)
c1.metric("Hours freed / week",f"{result.weekly_hours_freed:,.0f}",f"{time_savings:.0%} task time-savings potential")
c2.metric("FTE capacity reinvested",f"{result.net_fte_reinvestment:,.1f}",f"{result.fte_capacity_saved:,.1f} gross")
c3.metric("Cost-per-outcome efficiency",f"{result.efficiency_gain:.1%}","net of AI tooling")
c4.metric("Capacity leak",f"{result.leak_rate:.0%}","unreinvested freed capacity")

left,right=st.columns(2)
with left:
    breakdown=tasks.groupby("task_bucket",as_index=False).hours_weight.sum(); breakdown["share"]=breakdown.hours_weight/breakdown.hours_weight.sum()
    fig=px.pie(breakdown,names="task_bucket",values="share",hole=.62,color="task_bucket",color_discrete_map=COLORS)
    st.plotly_chart(chart_layout(fig,"Task evolution breakdown"),width="stretch")
with right:
    allocation=pd.DataFrame({"Allocation":["Leak","Core efficiency","Growth / innovation","Total freed"],"Hours":[result.leak_hours,result.core_hours,result.growth_hours,result.annual_hours_freed],"kind":["Leak","Core","Growth","Total"]})
    fig=px.bar(allocation,x="Hours",y="Allocation",orientation="h",color="kind",color_discrete_map={"Leak":"#E76F51","Core":"#7D8CFF","Growth":"#45C6A8","Total":"#F4B860"})
    st.plotly_chart(chart_layout(fig,"Annual capacity reinvestment allocation"),width="stretch")

comparison=family_comparison(load_tasks())
fig=px.scatter(comparison,x="AI exposure",y="Cognitive intensity",hover_name="Family",color="Zone",size=np.where(comparison.Label==label,26,14),color_discrete_sequence=px.colors.qualitative.Safe)
fig.add_vline(x=.5,line_dash="dot"); fig.add_hline(y=.5,line_dash="dot")
st.plotly_chart(chart_layout(fig,"HR function: exposure × cognitive intensity"),width="stretch")

ranked=comparison.sort_values("Time-savings potential")
fig=px.bar(ranked,x="Time-savings potential",y="Label",orientation="h",color="Zone",color_discrete_sequence=px.colors.qualitative.Safe)
st.plotly_chart(chart_layout(fig,"All 15 HR families ranked by time-savings potential"),width="stretch")

tabs=st.tabs(["Task inventory","HR comparison","Skills transition","Family sources","Methodology"])
with tabs[0]:
    st.caption("Every displayed rating has an explicit rationale in data/rescore_tasks.py. Source links lead to O*NET occupation pages.")
    cols=[c for c in ["onet_task_id","occupation","task","exposure_rating","automation_potential","judgment_intensity","exposure_category","exposure_rationale","task_bucket"] if c in tasks]
    st.dataframe(tasks[cols],width="stretch",hide_index=True)
    st.download_button("Download task inventory",tasks.to_csv(index=False),f"{label.lower()}_tasks.csv","text/csv")
with tabs[1]:
    display=comparison.copy()
    for c in ["AI exposure","Cognitive intensity","Time-savings potential"]: display[c]=display[c].map("{:.1%}".format)
    display["Default salary"]=display["Default salary"].map("${:,.0f}".format)
    st.dataframe(display,width="stretch",hide_index=True)
    st.download_button("Download HR comparison",comparison.to_csv(index=False),"hr_function_comparison.csv","text/csv")
with tabs[2]:
    skills=skill_transition(label,adoption)
    fig=px.bar(skills,x="shift",y="skill",orientation="h",color="direction",color_discrete_map={"Declining":"#E76F51","Emerging":"#45C6A8"})
    st.plotly_chart(chart_layout(fig,"Skills taxonomy evolution: demand shift at current adoption"),width="stretch")
    gauge=go.Figure(go.Indicator(mode="gauge+number",value=gap.index,title={"text":f"Expertise Pipeline Gap · {gap.band}"},gauge={"axis":{"range":[0,100]},"bar":{"color":"#F4B860"},"steps":[{"range":[0,30],"color":"#45C6A8"},{"range":[30,50],"color":"#F4B860"},{"range":[50,70],"color":"#E98B50"},{"range":[70,100],"color":"#E76F51"}]}))
    st.plotly_chart(chart_layout(gauge,"Entry-level erosion × judgment premium"),width="stretch")
    st.info(gap.action)
with tabs[3]:
    sources=pd.DataFrame([{"Label":f.label,"Job family":f.name,"Framework evidence":f.frameworks,"O*NET-SOC sources":", ".join(f.occupations),"Coverage":f.coverage} for f in HR_FAMILIES.values()])
    st.dataframe(sources,width="stretch",hide_index=True)
    st.caption("Partial: HRIS lacks O*NET task coverage for system configuration; EX lacks a dedicated employee-experience occupation. Good: assembled from adjacent occupational task sources.")
with tabs[4]:
    st.markdown(f"""### Live methodology and assumptions
    **Current scenario:** {team} people × {hours} weekly hours × {time_savings:.1%} time-savings potential × {adoption:.0%} adoption = **{result.weekly_hours_freed:,.0f} hours/week freed**.

    `annual hours = weekly hours freed × productive weeks`; `FTE saved = annual hours / ({hours} × {weeks})`.
    `leak = clamp(0.40 − 0.30 × maturity + 0.10 × (1 − adoption), 0.05, 0.60)` = **{result.leak_rate:.1%}**. Retained capacity splits **{1-growth:.0%} core / {growth:.0%} growth**.

    Eloundou et al. (2023) ratings are manually applied: E0=0.08 (no direct exposure, including physical, legal-human, or consequential decisions); E1=0.85 (LLM alone saves ≥50%); E2=0.55 (software integration required); E3=0.45 (image capability required). Judgment intensity is a separate internal 0–1 measure: <.40 transaction/low judgment, .40–.69 applied analysis, ≥.70 consequential or live professional judgment.

    Pipeline gap = `100 × sqrt(entry-level erosion × judgment premium)` where erosion is adoption × exposure of low-judgment tasks and premium is `min(1, weighted judgment × (1 + .5 × adoption))`.

    {ONET_ATTRIBUTION}""")
