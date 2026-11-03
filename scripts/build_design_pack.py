"""Build the diagrams for the components currently implemented."""
from pathlib import Path
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent
INK = colors.HexColor('#183246')
MUTED = colors.HexColor('#52697b')
GREEN = colors.HexColor('#17695f')
PALE = colors.HexColor('#eaf4f1')
LINE = colors.HexColor('#d8e3ea')


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


def main():
    fonts()
    diagrams = ROOT / 'docs/diagrams'
    diagrams.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(database(), str(diagrams / 'database-erd.svg'))


if __name__ == '__main__':
    main()
