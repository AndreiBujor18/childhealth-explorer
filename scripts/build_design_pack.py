"""Build Lab 1 diagrams, the prototype dataset and the four-page report.

Uses optional authoring dependencies in requirements-design.txt.
Run from the repository root with a Python interpreter containing these tools.
"""
import csv
import json
from copy import deepcopy
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image,
)

ROOT = Path(__file__).resolve().parent.parent
INK = colors.HexColor('#183246')
MUTED = colors.HexColor('#52697b')
GREEN = colors.HexColor('#17695f')
PALE = colors.HexColor('#eaf4f1')
LINE = colors.HexColor('#d8e3ea')
BLUE = colors.HexColor('#346ca7')


def fonts():
    font_dir = Path('C:/Windows/Fonts')
    pdfmetrics.registerFont(TTFont('Calibri', str(font_dir / 'calibri.ttf')))
    pdfmetrics.registerFont(TTFont('CalibriBold', str(font_dir / 'calibrib.ttf')))
    pdfmetrics.registerFontFamily('Calibri', normal='Calibri', bold='CalibriBold', italic='Calibri', boldItalic='CalibriBold')


def label(drawing, x, y, text, size=10, bold=False, color=INK):
    drawing.add(String(x, y, text, fontName='CalibriBold' if bold else 'Calibri', fontSize=size, fillColor=color))


def box(drawing, x, y, w, h, title, lines=(), planned=False):
    drawing.add(Rect(x, y, w, h, rx=7, ry=7, fillColor=colors.white if planned else PALE,
                     strokeColor=LINE if planned else GREEN, strokeWidth=.8,
                     strokeDashArray=[3, 2] if planned else None))
    label(drawing, x + 11, y + h - 19, title, 11, True)
    for i, line in enumerate(lines):
        label(drawing, x + 11, y + h - 36 - 13 * i, line, 9.5, color=MUTED)


def arrow(drawing, points, color=MUTED):
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        drawing.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1))
    x, y = points[-1]
    px, py = points[-2]
    if y < py:
        xy = [x - 3, y + 6, x, y, x + 3, y + 6]
    elif x < px:
        xy = [x + 6, y - 3, x, y, x + 6, y + 3]
    else:
        xy = [x - 6, y - 3, x, y, x - 6, y + 3]
    drawing.add(Polygon(xy, fillColor=color, strokeColor=None))


def architecture():
    d = Drawing(500, 430)
    label(d, 0, 415, 'ChildHealth Explorer / application architecture', 15, True)
    box(d, 0, 335, 158, 58, '1. UNICEF API', ['Vaccination / SDMX-JSON'])
    box(d, 171, 335, 158, 58, '1. World Bank API', ['Mortality and context / JSON'])
    box(d, 342, 335, 158, 58, 'Additional API', ['New adapter, planned'], True)
    arrow(d, [(79, 335), (79, 317), (195, 317), (195, 299)])
    arrow(d, [(250, 335), (250, 299)])
    arrow(d, [(421, 335), (421, 317), (305, 317), (305, 299)])
    box(d, 60, 230, 300, 69, '2. Import Python / ETL', ['Extractors and validation: implemented', 'Loading, upserts, import_log: planned'])
    box(d, 385, 230, 115, 69, 'Raw cache', ['JSON + URL', 'Date + SHA-256'])
    arrow(d, [(360, 264), (385, 264)])
    arrow(d, [(210, 230), (210, 206)])
    box(d, 60, 145, 300, 61, '3. PostgreSQL', ['5 tables created / application data store'])
    arrow(d, [(210, 145), (210, 122)])
    box(d, 60, 60, 300, 62, '4. FastAPI + SQLAlchemy', ['Queries against our database / JSON'], True)
    box(d, 385, 60, 115, 62, 'Analysis / ML', ['Plotly', 'scikit-learn'], True)
    arrow(d, [(360, 92), (385, 92)])
    arrow(d, [(360, 176), (443, 176), (443, 122)])
    label(d, 390, 152, 'DB read', 9, color=MUTED)
    arrow(d, [(210, 60), (210, 38)])
    box(d, 60, -23, 440, 61, '5. Web interface / Jinja2 + HTML + CSS', ['Tables, filters, charts; estimates after model evaluation'], True)
    # Move everything up to keep the SVG viewBox strictly inside its content.
    d.translate(0, 25)
    d.height = 455
    return d


def database():
    d = Drawing(500, 347)
    label(d, 0, 331, 'Database / entity-relationship model', 15, True)
    box(d, 0, 202, 140, 106, 'source', ['PK source_id', 'name (unique)', 'url'])
    box(d, 180, 164, 155, 144, 'indicator', ['PK indicator_id', 'FK source_id', 'code + concept_code', 'name + unit', 'age_group'])
    box(d, 375, 202, 125, 106, 'country', ['PK iso3', 'iso2 / name', 'region / income_group'])
    box(d, 0, 0, 150, 143, 'import_log', ['PK import_id', 'source_name', 'indicator_code', 'url / rows_loaded', 'imported_at'])
    box(d, 205, 0, 210, 141, 'observation', ['PK observation_id', 'FK country_iso3 / indicator_id', 'year / sex / value', 'imported_at'])
    arrow(d, [(140, 254), (180, 254)])
    label(d, 146, 262, '1:N', 9)
    arrow(d, [(257, 164), (257, 141)])
    label(d, 264, 148, '1:N', 9)
    arrow(d, [(437, 202), (437, 175), (352, 175), (352, 141)])
    label(d, 405, 181, '1:N', 9)
    label(d, 207, 15, 'UNIQUE country + indicator + year + sex', 9, True, GREEN)
    label(d, 1, 152, 'Separate audit; no foreign keys', 9, color=MUTED)
    return d


COUNTRIES = {'ROU': 'Romania', 'BGR': 'Bulgaria', 'DEU': 'Germany', 'FRA': 'France', 'POL': 'Poland',
             'ESP': 'Spain', 'GBR': 'United Kingdom', 'SWE': 'Sweden', 'USA': 'United States', 'CAN': 'Canada',
             'BRA': 'Brazil', 'MEX': 'Mexico', 'IND': 'India', 'IDN': 'Indonesia', 'ZAF': 'South Africa',
             'KEN': 'Kenya', 'NGA': 'Nigeria', 'EGY': 'Egypt', 'AUS': 'Australia', 'JPN': 'Japan'}
LABELS = {'IM_DTP3': 'DTP3 vaccination coverage', 'IM_MCV1': 'First-dose measles vaccination coverage',
          'SH.DYN.MORT': 'Under-five mortality', 'NY.GDP.PCAP.PP.KD': 'GDP per capita (PPP)',
          'SH.XPD.CHEX.GD.ZS': 'Current health expenditure', 'SH.H2O.BASW.ZS': 'Basic drinking water access',
          'SH.STA.BASS.ZS': 'Basic sanitation access'}


def prototype_data():
    indicators = json.loads((ROOT / 'config/indicators.json').read_text(encoding='utf-8'))
    data = {'countries': COUNTRIES, 'indicators': {}, 'series': {}}
    for i in indicators:
        unit = i['unit']
        data['indicators'][i['code']] = {'label': LABELS[i['code']], 'unit': unit,
                                       'source': 'UNICEF' if i['source'] == 'unicef' else 'World Bank'}
    with (ROOT / 'docs/evidence/sample_observations.csv').open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            value = round(float(r['value']), 4) if r['value'] else None
            data['series'].setdefault(r['country_iso3'], {}).setdefault(r['indicator_code'], {})[r['year']] = value
    fragment = ROOT / 'docs/prototype/childhealth-ui.html'
    content = fragment.read_text(encoding='utf-8')
    import re
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    content = re.sub(r'(<script type="application/json" id="ch-data">).*?(</script>)',
                     lambda m: m[1] + payload + m[2], content, flags=re.S)
    fragment.write_text(content, encoding='utf-8')
    print(f'Prototype: {len(content.encode())} bytes; {len(data["countries"])} countries.')


def report(arch, erd):
    out = ROOT / 'output/pdf'
    out.mkdir(parents=True, exist_ok=True)
    normal = ParagraphStyle('Body', fontName='Calibri', fontSize=10.5, leading=14.5,
                            textColor=INK, spaceAfter=7, alignment=TA_LEFT)
    heading = ParagraphStyle('Heading', parent=normal, fontName='CalibriBold', fontSize=17,
                             leading=21, spaceBefore=6, spaceAfter=11)
    small = ParagraphStyle('Small', parent=normal, fontSize=9, leading=11.5, textColor=MUTED)
    sub = ParagraphStyle('Sub', parent=normal, fontName='CalibriBold', fontSize=12, spaceBefore=7, leading=16)
    story = []

    def p(text, style=normal):
        return Paragraph(text, style)

    def add(text, style=normal):
        story.append(p(text, style))

    def table(rows, widths):
        cells = [[p(str(c), small if n == 0 else normal) for c in row] for n, row in enumerate(rows)]
        t = Table(cells, colWidths=widths, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PALE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), .7, GREEN), ('LINEBELOW', (0, 1), (-1, -1), .35, LINE),
            ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.extend([t, Spacer(1, 10)])

    add('CHILDHEALTH EXPLORER', small)
    add('Lab 1 - Topic, Environment and Architecture', heading)
    add('Childhood Vaccination, Socioeconomic Conditions, and Under-Five Mortality',
        ParagraphStyle('Title', parent=heading, fontSize=22, leading=26, textColor=GREEN, spaceAfter=16))
    add('Andrei Bujor | 4 November 2026', small)
    add('<link href="https://github.com/AndreiBujor18/childhealth-explorer" color="#17695f">'
        'GitHub: AndreiBujor18/childhealth-explorer</link>', small)
    add('1.2 / Topic and research question', sub)
    add('<b>How are childhood vaccination, socioeconomic conditions and access to basic services associated '
        'with under-five mortality across countries and over time?</b> The project relates to Sustainable '
        'Development Goal 3 (SDG 3) by '
        'examining country-level differences in child health. It uses free annual data from UNICEF '
        '(vaccination) and the World Bank (mortality and socioeconomic indicators), initially covering '
        '20 countries from 2000 to 2023. Students, public health analysts and NGOs will be able to compare '
        'countries, explore trends and estimate under-five mortality. The proposed machine learning (ML) '
        'task compares linear regression and random forest regression using the six explanatory indicators.')
    add('Planned data split: training 2000-2017, validation 2018-2020, testing 2021-2023. Preprocessing '
        'will be fitted on training data only. The models will estimate mortality for the same year '
        'as the input data.', small)
    add('1.3-1.4 / Development environment', sub)
    table([['Tool', 'Version / configuration'], ['Python / Git', '3.14.6 / 2.51.0.windows.1'],
           ['VS Code / pgAdmin', '1.143.0 / 9.18'],
           ['PostgreSQL', '18.6 portable; global_health; gh_user; UTF8'],
           ['Python libraries', 'requests, pandas, SQLAlchemy, psycopg, FastAPI, Jinja2, pytest']], [150, 350])
    add('The project uses the .venv virtual environment; dependency versions are pinned in requirements-lock.txt. '
        'VS Code has the Python, '
        'Jupyter and container extensions. PostgreSQL was extracted from the official EDB Windows ZIP '
        'into .local/pgsql, with data in .local/pgdata. It runs locally on 127.0.0.1:5432. '
        'Credentials are excluded from Git.', small)
    shot = ROOT / 'docs/evidence/screenshots/pgadmin-ready-2026-11-04.jpg'
    if shot.exists():
        w, h = ImageReader(str(shot)).getSize()
        scale = min(500 / w, 165 / h)
        story.append(Image(str(shot), width=w * scale, height=h * scale))
        story.append(Spacer(1, 7))
    add('Figure 1. pgAdmin: global_health / gh_user, SELECT version(), PostgreSQL 18.6 (4 November). '
        'Full-size screenshots: docs/evidence/screenshots/.', small)

    story.append(PageBreak())
    add('1.5 / Topic-specific challenges', heading)
    table([['Challenge', 'Proposed solution'],
           ['Different reference populations and ages', 'Keep DTP3, MCV1 and under-five mortality separate. '
            'Preserve definitions, units and age groups; align records by country and year.'],
           ['Confounding in the vaccination-mortality relationship', 'Include GDP, health spending, water '
            'and sanitation. Discuss unmeasured factors and interpret results as associations.']], [160, 340])
    add('1.6 / Application architecture', heading)
    report_arch = deepcopy(arch)
    report_arch.scale(.78, .78)
    report_arch.width *= .78
    report_arch.height *= .78
    story.append(report_arch)
    add('Only the extract, transform and load (ETL) pipeline will retrieve external data and load observations. '
        'The backend and analysis modules will read PostgreSQL; the interface will use the backend. '
        'This keeps browsing independent of external API availability. Source adapters, validation and '
        'the empty database are implemented. Data loading and the components in dashed boxes are planned.')
    add('Integrating a third API requires a new adapter, registry entry and indicator configuration. '
        'The adapter will return the same fields: source, indicator code, ISO3 country code, year, sex '
        'and value. The existing validation can be reused. Additional data dimensions would require '
        'a schema review.', small)
    add('<b>Folders:</b> app/ - database and models; etl/ - adapters, cache and validation; '
        'config/ - indicator catalog; db/ - schema and export; docs/ - design and evidence; '
        'scripts/ - setup; notebooks/ - analysis; tests/ - checks. Planned UI: Jinja2 and Plotly; '
        'ML: scikit-learn.', small)

    story.append(PageBreak())
    add('1.7 / Indicators and data availability', heading)
    table([['Source / code', 'Indicator and unit', 'Non-null values'],
           ['UNICEF / IM_DTP3', 'DTP3 vaccination coverage (%)', '480 / 480'],
           ['UNICEF / IM_MCV1', 'First-dose measles vaccination coverage (%)', '480 / 480'],
           ['WB / SH.DYN.MORT', 'Under-five mortality per 1,000 live births', '480 / 480'],
           ['WB / NY.GDP.PCAP.PP.KD', 'GDP per capita, PPP; constant 2021 international $', '480 / 480'],
           ['WB / SH.XPD.CHEX.GD.ZS', 'Current health expenditure (% of GDP)', '480 / 480'],
           ['WB / SH.H2O.BASW.ZS', 'At least basic drinking water services (% of population)', '470 / 480'],
           ['WB / SH.STA.BASS.ZS', 'At least basic sanitation services (% of population)', '479 / 480']], [166, 249, 85])
    add('Under-five mortality is the target; the other six indicators are proposed explanatory variables. '
        'The pilot covers 20 countries and 24 years, using data for both sexes combined where applicable. '
        '<b>469 of 480 country-year combinations contain all seven values.</b> These data establish '
        'feasibility; the countries were not selected to form a statistically representative sample.')
    add('Missing values remain NULL. Adapters normalize ISO3 codes and response structures; validation '
        'checks years, duplicates and numeric limits. Pagination, retries and a raw JSON cache support '
        'reliable extraction. Each cached response has a source URL, retrieval timestamp and SHA-256 hash.')
    add('API verification', sub)
    add('All seven indicator URLs for Romania returned HTTP 200 and 24 annual records each on 3 November. '
        'On 4 November, all seven were opened in Chrome and their JSON responses were confirmed. '
        'World Bank returns pagination metadata followed by observations; UNICEF uses SDMX dimensions '
        'and indexed observations. The browser screenshots and automated response checks are stored separately.')
    add('The complete clickable URL catalog is in docs/indicators.md. The 21 October pilot is recorded in '
        'docs/evidence/api_validation.json, coverage.csv and sample_observations.csv. The later Romania '
        'checks are in url-check-2026-11-03.json and browser-url-check-2026-11-04.json in the same folder. '
        'These checks save files without inserting data into PostgreSQL.', small)
    add('Source documentation', sub)
    for title, url in [
        ('UNICEF / SDMX API and response structure', 'https://data.unicef.org/sdmx-api-documentation/'),
        ('UNICEF / Immunization indicators and definitions', 'https://data.unicef.org/topic/child-health/immunization/'),
        ('World Bank / Indicators API', 'https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures'),
        ('EDB / PostgreSQL ZIP binaries', 'https://www.enterprisedb.com/download-postgresql-binaries'),
    ]:
        add(f'<link href="{escape(url)}" color="#17695f">{escape(title)}</link>', small)

    story.append(PageBreak())
    add('1.8-1.9 / Database design and implementation', heading)
    story.append(erd)
    add('Justified changes to the reference schema', sub)
    add('<b>Source-specific codes:</b> UNIQUE(source_id, code) allows different APIs to use the same code. '
        '<b>concept_code:</b> identifies a shared concept without assuming equivalent definitions. '
        '<b>age_group:</b> records the fixed reference population of each indicator. Code and unit fields '
        'have been expanded to accommodate longer metadata.')
    add('Observations remain unique by country, indicator, year and sex; the indicator identifies the source. '
        'Missing values remain NULL. The (indicator_id, year) index is retained. Check constraints enforce years '
        '1900-2100, valid sex codes and nonnegative values. Percentage limits are also checked in Python.')
    add('Implementation and verification', sub)
    add('The five tables are defined by SQLAlchemy models in app/models.py and created by app/create_tables.py. '
        'The schema was exported to db/schema_dump.sql using pg_dump --schema-only. An automated comparison '
        'against db/schema.sql confirmed matching columns, keys, constraints and indexes.')
    add('A read-only check on 4 November confirmed that all five tables exist and are empty, '
        'as required for Lab 1. Evidence: '
        'docs/evidence/database_verification.json and recheck-2026-11-04.json.', small)
    add('import_log is a separate audit table without foreign keys, following the lab design. Database '
        'loading, application endpoints, a database-connected interface and model training will be '
        'implemented in later stages.', small)

    def footer(canvas, doc):
        canvas.setStrokeColor(LINE)
        canvas.line(47, 40, 547, 40)
        canvas.setFont('Calibri', 9)
        canvas.setFillColor(MUTED)
        canvas.drawString(47, 26, 'ChildHealth Explorer | Lab 1 | 4 November 2026')
        canvas.drawRightString(547, 26, f'{doc.page} / 4')

    path = out / 'Lab-1-Report-ChildHealth-Explorer.pdf'
    doc = SimpleDocTemplate(str(path), pagesize=(595.28, 841.89), leftMargin=47, rightMargin=48,
                            topMargin=36, bottomMargin=54, title='ChildHealth Explorer - Lab 1 Report',
                            author='Andrei Bujor', lang='en-GB')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(path)



def main():
    fonts()
    prototype_data()
    diagrams = ROOT / 'docs/diagrams'
    diagrams.mkdir(exist_ok=True)
    arch, erd = architecture(), database()
    renderSVG.drawToFile(arch, str(diagrams / 'application-architecture.svg'))
    renderSVG.drawToFile(erd, str(diagrams / 'database-erd.svg'))
    report(arch, erd)


if __name__ == '__main__':
    main()
