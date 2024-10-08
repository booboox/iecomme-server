"""Add Post model

Revision ID: 30d787802868
Revises: 6a104d3d1765
Create Date: 2024-10-03 11:35:13.001591

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '30d787802868'
down_revision = '6a104d3d1765'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=120),
               type_=sa.String(length=512),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=512),
               type_=mysql.VARCHAR(length=120),
               existing_nullable=False)

    # ### end Alembic commands ###
