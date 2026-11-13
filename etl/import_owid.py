"""Load saved OWID mortality, converted to per 1,000 live births."""
from etl.import_source import main, import_results

def import_all(session_factory=None):
    return import_results('owid', session_factory)


if __name__ == '__main__':
    main('owid')
