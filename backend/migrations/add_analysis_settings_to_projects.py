"""Add analysis settings fields to projects table

Revision ID: add_analysis_settings
Revises:
Create Date: 2025-01-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_analysis_settings'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add analysis settings fields to projects table
    op.add_column('projects', sa.Column('base_price_date', sa.String(20), nullable=True, comment="基期信息价日期"))
    op.add_column('projects', sa.Column('base_price_province', sa.String(20), nullable=True, comment="基期信息价省份"))
    op.add_column('projects', sa.Column('base_price_city', sa.String(20), nullable=True, comment="基期信息价城市"))
    op.add_column('projects', sa.Column('base_price_district', sa.String(20), nullable=True, comment="基期信息价区县"))
    op.add_column('projects', sa.Column('support_price_adjustment', sa.Boolean(), default=True, comment="是否支持调价"))
    op.add_column('projects', sa.Column('price_adjustment_range', sa.Float(), default=5.0, comment="调价范围(%)"))
    op.add_column('projects', sa.Column('audit_scope', postgresql.JSON(), nullable=True, comment="分析范围"))


def downgrade():
    # Remove analysis settings fields from projects table
    op.drop_column('projects', 'audit_scope')
    op.drop_column('projects', 'price_adjustment_range')
    op.drop_column('projects', 'support_price_adjustment')
    op.drop_column('projects', 'base_price_district')
    op.drop_column('projects', 'base_price_city')
    op.drop_column('projects', 'base_price_province')
    op.drop_column('projects', 'base_price_date')