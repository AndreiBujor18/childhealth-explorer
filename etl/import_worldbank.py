"""Load country metadata and the World Bank study series first."""
from etl.import_source import main

if __name__ == '__main__':
    main('worldbank')
