"""Load saved OWID mortality, converted to per 1,000 live births."""
from etl.import_source import main

if __name__ == '__main__':
    main('owid')
