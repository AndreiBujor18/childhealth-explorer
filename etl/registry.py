"""Add a source adapter here; validation and consumers do not depend on its JSON."""
from etl.extract_unicef import UnicefAdapter
from etl.extract_worldbank import WorldBankAdapter

ADAPTERS = {'unicef': UnicefAdapter, 'worldbank': WorldBankAdapter}


def get_adapter(source, client):
    try:
        factory = ADAPTERS[source]
    except KeyError as exc:
        raise ValueError(f'Unregistered source: {source}') from exc
    return factory(client)
