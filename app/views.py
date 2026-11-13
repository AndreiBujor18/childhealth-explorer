"""Jinja configuration and display formatting; no database access."""
from pathlib import Path
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / 'templates'))


def format_value(value):
    return f'{value:,.4f}'.rstrip('0').rstrip('.') if value is not None else '-'


def source_label(value):
    return {'who': 'WHO', 'owid': 'Our World in Data', 'unicef': 'UNICEF',
            'worldbank': 'World Bank'}.get(value, value)


templates.env.filters['measurement'] = format_value
templates.env.filters['source_label'] = source_label
