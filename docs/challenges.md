# Task 1.5 - Topic-specific challenges and solutions

Topic: **Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality**.

These two challenges extend the general integration issues described in the lab: inconsistent identifiers, missing values, duplicates, pagination and API outages.

| Topic-specific challenge | Why it arises | Proposed solution |
|---|---|---|
| Different definitions and reference populations | DTP3 and first-dose measles coverage refer to particular vaccines and recommended ages. Under-five mortality concerns a different population. These indicators do not automatically share a denominator or definition. | Keep indicators separate and document their source, definition, unit and age group. Align observations by country and year using consistently defined series. Combine vaccination percentages only if a justified method is available. |
| Confusing association with a causal effect | The project compares country-level aggregates. Mortality differences may be associated with vaccination, economic resources and access to basic services simultaneously; a simple correlation does not isolate each factor's contribution. | Include GDP per capita, health expenditure, water and sanitation. Present associations and statistical estimates, discuss unmeasured factors and avoid interpreting model estimates as causal effects of interventions. |

Lab 1 requires identifying challenges and proposing solutions. Full implementation and evaluation will accompany data loading, analysis and ML in later stages.
