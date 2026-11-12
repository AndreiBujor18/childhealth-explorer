"""Use the project's secret-free connection factory for Alembic."""
from alembic import context
from app.database import get_engine
from app.models import Base

if context.is_offline_mode():
    context.configure(dialect_name='postgresql', target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    def migrate(connection):
        context.configure(connection=connection, target_metadata=Base.metadata,
                          compare_type=True, compare_server_default=True)
        with context.begin_transaction():
            context.run_migrations()
    existing = context.config.attributes.get('connection')
    if existing is not None:
        migrate(existing)
    else:
        with get_engine().connect() as connection:
            migrate(connection)
