"""Adding Message, Chat; update User

Revision ID: 908baaf1881b
Revises: f50cdfdbf8dc
Create Date: 2024-11-02 16:26:41.249303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '908baaf1881b'
down_revision: Union[str, None] = 'f50cdfdbf8dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('can_write', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'can_write')
    # ### end Alembic commands ###
