"""Load saved WHO under-five mortality observations."""
from etl.import_source import main, import_results

def import_all(session_factory=None):
    return import_results('who', session_factory)


if __name__ == '__main__':
    main('who')
