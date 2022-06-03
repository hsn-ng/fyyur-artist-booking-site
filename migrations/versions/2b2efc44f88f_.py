"""empty message

Revision ID: 2b2efc44f88f
Revises: 9569cc2cba8f
Create Date: 2022-05-31 20:12:25.728584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b2efc44f88f'
down_revision = '9569cc2cba8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artists', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.drop_column('artists', 'seeking')
    op.drop_column('artists', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('description', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('seeking', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('artists', 'seeking_description')
    op.drop_column('artists', 'seeking_venue')
    # ### end Alembic commands ###
