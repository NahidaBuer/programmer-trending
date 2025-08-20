"""Add comprehensive summary status management

Revision ID: 80a7b12ab76f
Revises: 9b424b5e7b81
Create Date: 2025-08-20 20:39:29.906519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80a7b12ab76f'
down_revision: Union[str, Sequence[str], None] = '9b424b5e7b81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    
    # Create new table with updated schema
    op.create_table('summaries_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('lang', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),  # Made nullable
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PERMANENTLY_FAILED', 'SKIPPED', name='summarystatus'), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('max_retries', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_type', sa.String(), nullable=True),
        sa.Column('generation_duration_ms', sa.Integer(), nullable=True),
        sa.Column('url_retrieval_status', sa.String(), nullable=True),
        sa.Column('response_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )
    
    # Copy existing data
    op.execute("""
        INSERT INTO summaries_new (id, item_id, model, lang, content, status, retry_count, max_retries, created_at)
        SELECT id, item_id, model, lang, content, 'pending', 0, 3, created_at
        FROM summaries
    """)
    
    # Drop old table and rename new table
    op.drop_table('summaries')
    op.rename_table('summaries_new', 'summaries')
    
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    
    # Create old table structure
    op.create_table('summaries_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('lang', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),  # Back to non-nullable
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id')
    )
    
    # Copy existing data (only non-null content)
    op.execute("""
        INSERT INTO summaries_old (id, item_id, model, lang, content, created_at)
        SELECT id, item_id, model, lang, content, created_at
        FROM summaries
        WHERE content IS NOT NULL
    """)
    
    # Drop new table and rename old table
    op.drop_table('summaries')
    op.rename_table('summaries_old', 'summaries')
    
    # ### end Alembic commands ###
