# ChildHealth Explorer UI prototype

A design proposal for reviewing the interface before implementation. The final stack follows the lab: FastAPI, Jinja2, HTML/CSS, Plotly and scikit-learn, with PostgreSQL for storage.

## Screens and interactions

| Screen | Available for review | Future implementation |
|---|---|---|
| Explore | Country, one of seven indicators, year range, chart and recent values | Filtered SQLAlchemy query, Jinja2 page and Plotly chart |
| Compare countries | Up to three countries in one chart; DTP3 versus mortality in the selected year | PostgreSQL data, shared units and statistical analysis |
| ML estimates | Six-indicator form and planned model selection | A trained and evaluated model called through the backend |

ML calculation is disabled. No model has been trained, no performance has been measured and no predictions are generated at this stage.

## Displayed data

- Real public observations from `docs/evidence/sample_observations.csv`, downloaded on 21 October 2026.
- Twenty countries, 2000-2023, seven indicators, both sexes combined where applicable.
- Data is embedded for design review; the prototype is not connected to PostgreSQL and has not populated its tables.
- Missing values appear as **Unavailable** and are not plotted as zero.
- D3 is used only for prototype charts. The final implementation will use Plotly, following the lab plan.

## Files

- `docs/prototype/childhealth-ui.html`: interactive proposal with embedded public data.
- `docs/prototype/childhealth-ui-initial.html`: initial layout retained for comparison.
- `docs/evidence/screenshots/prototype-english-explore.jpg`, `prototype-english-compare.jpg` and `prototype-english-ml.jpg`: the English interface checked on 4 November.
- `docs/evidence/screenshots/prototype-refined-explore.jpg`: Romania exploration in the revised visual direction.
- `docs/evidence/screenshots/prototype-refined-compare.jpg`: country comparison.
- `docs/evidence/screenshots/prototype-refined-ml.jpg`: proposed ML form.
- `docs/evidence/screenshots/prototype-refined-mobile.jpg`: narrow-screen check.

The prototype text and labels were translated into English on 4 November. Older screenshots retain the language and appearance of the original checks; they are historical evidence.

The visual revision uses Source Sans 3 and Source Serif 4, simple dividers and restrained motion. Fonts load through Google Fonts; fallback fonts apply without CDN access. Design reasoning and customization variables are described in [Visual direction](design-direction.md). Screenshots without the `refined` prefix document the initial version. The PDF report includes a pgAdmin screenshot as installation evidence; the UI remains a separate design extension.

The chart library loads from the public jsDelivr CDN. The prototype makes no requests to health APIs or the project database.

## Visual checks recorded on 3 November 2026

1. Country, indicator and start-year changes update the chart and table.
2. Comparison shows three series; a fourth selection is rejected with a visible message.
3. Poland's water access in 2000-2004 appears as unavailable, matching the sample.
4. ML produces no artificial results and keeps calculation disabled.
5. Checks at 390 px and 320 px showed no horizontal application overflow. On mobile, country and indicator controls each occupy a full row.
6. No JavaScript errors were reported during the browser check.

Reduced motion is handled in both CSS and animation logic. The original visual review used the dark theme; it was not a full accessibility audit or cross-browser assessment.

## Before UI implementation

Review the layout, labels and flows with the project author. Then implement the backend and templates, keeping observations, evaluated estimates and any future forecasts clearly identified.
