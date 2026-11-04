# Talent Transformation Engine

An executive Streamlit scenario-modelling dashboard for translating task-level AI exposure into HR capacity, reinvestment, skill shifts, and expert-pipeline choices.

## What this is and isn’t

This is a **framework demonstrator** for portfolio discussion and structured client conversations. O*NET task statements, occupation references and wage metadata are public source material. Exposure ratings and judgment-intensity scores are analyst-applied interpretations, not observed productivity data or validated forecasts. Do not use outputs for individual employment, pay, selection, or legal decisions.

The bundled repository is a compact, auditable HR task set assembled around nine O*NET occupations. It demonstrates the data model and explicit scoring process. A production study should refresh every task list from the current O*NET release and have subject-matter experts review the ratings.

## Run it

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python data/rescore_tasks.py
streamlit run app.py
```

`engine/` has no Streamlit dependency and can be reused or unit-tested directly. The dashboard covers 15 HR families and treats leadership as a level across every family. Strong coverage means a dedicated O*NET occupation; Good means relevant work is assembled from related occupations; Partial marks a source gap. HRIS is Partial because O*NET covers HR data and records work, not platform configuration; Employee Experience is Partial because it has no dedicated occupation.

| Family | Framework triangulation | Coverage |
|---|---|---|
| HRBP; Talent Acquisition; Employee Relations; Labor Relations | OPM GS-0200; CIPD People practice, Resourcing, Employee relations | Good; Strong; Good; Strong |
| Compensation; Benefits; Payroll | OPM Classification/Compensation and Benefits; CIPD Reward; university HR Operations | Strong; Good; Strong |
| L&D; Talent; OD&D | OPM HR Development/Performance; CIPD L&D, Talent management, OD&D | Strong; Good; Good |
| HR Ops; HRIS; Analytics | OPM HRIS; CIPD People analytics/Workforce planning; university HR Operations | Good; Partial; Good |
| DEI; Employee Experience | CIPD EDI, Employee experience and Wellbeing; university architecture | Strong; Partial |

Occupation metadata, wage figures and source URLs live in `data/onet_occupations.csv`. `engine/hr_families.py` declares every family’s source occupations and maps task IDs as core or supporting. Task hours weights are `importance × rank weight × emphasis`, with rank weight declining linearly from 1.0 to 0.4.

## Exposure and judgment methodology

`data/rescore_tasks.py` is an auditable scoring ledger. It contains an explicit table for every bundled task: ID, rating, judgment score, category, rationale, and family tags. Running it deterministically generates `data/onet_task_repository.csv`.

The manual exposure assessment follows Eloundou, Manning, Mishkin and Rock (2023), *GPTs are GPTs*. Their task-level labels are not released as a reusable public dataset; this project applies their published rubric rather than claiming their numbers.

| Rating | Potential | Interpretation |
|---|---:|---|
| E0 | .08 | No meaningful direct exposure, including physical, legally human, or consequential livelihood decisions |
| E1 | .85 | A general-purpose LLM can directly reduce task time by at least half |
| E2 | .55 | Material time reduction needs software integration or task-specific systems |
| E3 | .45 | Comparable time reduction requires image capability |

`judgment_intensity` is this project’s separate strategic score, not an Eloundou measure: below .40 is transaction/low judgment; .40–.69 applied analysis; .70+ consequential, live, or professionally accountable judgment. Tasks are Human-Led at .70+ judgment, Automated at .65+ potential and below .40 judgment, otherwise Augmented. Capture factors are .10, .80 and .40 respectively.

## Formulas

```text
weekly hours freed = team size × weekly hours × time-savings potential × adoption
annual hours freed = weekly hours freed × productive weeks
FTE capacity saved = annual hours freed / (weekly hours × productive weeks)
leak = clamp(.40 − .30 × change maturity + .10 × (1 − adoption), .05, .60)
cost per outcome after = (loaded team cost + AI tooling cost) / (team hours + retained capacity)
```

The original Expertise Pipeline Gap is a hypothesis: `100 × sqrt(entry-level erosion × judgment premium)`, where erosion is adoption times low-judgment exposure and premium is `min(1, weighted judgment × (1 + .5 × adoption))`. Bands: Low <30, Moderate 30–50, Elevated 50–70, Critical ≥70.

## Assumptions and limitations

- Calibrate task ratings against a second published measure and HR practitioner review.
- Replace O*NET importance-rank time allocation with role-specific time-use data.
- Refresh wages for the selected geography, seniority, and date.
- Adoption, leak, and reinvestment are scenario assumptions, not empirical forecasts.
- Custom uploads validate CSV structure and score ranges, not source provenance or rating quality.

## Attribution and references

O*NET OnLine, National Center for O*NET Development. O*NET data are [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). O*NET® is a trademark of the U.S. Department of Labor, Employment and Training Administration.

Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). *GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models*. Science, 384(6702), 1306–1308. https://arxiv.org/abs/2303.10130
