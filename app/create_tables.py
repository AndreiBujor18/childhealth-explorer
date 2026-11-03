"""Create the laboratory tables without importing observations."""
from app.database import get_engine
from app.models import Base


def main():
    Base.metadata.create_all(get_engine())
    print('Tables created: source, country, indicator, observation, import_log.')


if __name__ == '__main__':
    main()
