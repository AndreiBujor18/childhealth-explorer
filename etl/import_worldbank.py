"""Load country metadata and the World Bank study series first."""
from etl.import_source import main, import_results

def import_all(session_factory=None):
    return import_results('worldbank', session_factory)


if __name__ == '__main__':
    main('worldbank')
