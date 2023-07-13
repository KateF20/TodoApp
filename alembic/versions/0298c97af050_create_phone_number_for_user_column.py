"""create phone number for user column

Revision ID: 0298c97af050
Revises: 
Create Date: 2023-07-06 18:27:45.829429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0298c97af050'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
