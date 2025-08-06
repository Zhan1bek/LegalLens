"""add document_chunks

Revision ID: cf286c03c181
Revises: 796c0e62a961
Create Date: 2025-08-06 12:13:54.407615
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql as pg

revision: str = "cf286c03c181"
down_revision: Union[str, Sequence[str], None] = "796c0e62a961"
branch_labels = depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "document_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
    )

    op.create_index(
        "ix_document_chunks_embedding",
        "document_chunks",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding", table_name="document_chunks")
    op.drop_table("document_chunks")
