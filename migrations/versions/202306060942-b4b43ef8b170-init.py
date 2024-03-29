"""init

Revision ID: b4b43ef8b170
Revises: 
Create Date: 2023-06-06 09:42:40.298774

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b4b43ef8b170"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "athletes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bib", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("when", sa.Date(), nullable=True),
        sa.Column("prize", sa.String(), nullable=True),
        sa.Column("slots", sa.String(), nullable=True),
        sa.Column("registration", sa.String(), nullable=True),
        sa.Column("deadline", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("events")
    op.drop_table("athletes")
    # ### end Alembic commands ###
