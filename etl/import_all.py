"""Load all saved study snapshots, World Bank country metadata first."""
from etl.import_source import import_source
import logging

SOURCES = ['worldbank', 'who', 'owid', 'unicef']


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    for source in SOURCES:
        import_source(source)


if __name__ == '__main__':
    main()
