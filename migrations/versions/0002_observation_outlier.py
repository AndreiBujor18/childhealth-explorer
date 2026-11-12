"""Mark, rather than discard, plausible observations outside IQR fences."""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('observation', sa.Column('is_outlier', sa.Boolean(), nullable=False,
                                         server_default=sa.false()))


def downgrade():
    op.drop_column('observation', 'is_outlier')
