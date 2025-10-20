"""add_price_type_fields_to_base_materials

Revision ID: 465b2c4aeedf
Revises: 2d7ecf790c2c
Create Date: 2025-09-11 16:13:03.325676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '465b2c4aeedf'
down_revision = '2d7ecf790c2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new price type fields to base_materials table
    op.add_column('base_materials', sa.Column('price_type', sa.String(length=20), nullable=True, comment='信息价类型 (provincial/municipal)'))
    op.add_column('base_materials', sa.Column('price_date', sa.String(length=10), nullable=True, comment='信息价期数 (YYYY-MM)'))
    op.add_column('base_materials', sa.Column('price_source', sa.String(length=50), nullable=True, comment='信息价来源描述'))
    
    # Create index for price_type and price_date combination
    op.create_index('ix_base_materials_price_type_date', 'base_materials', ['price_type', 'price_date'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_base_materials_price_type_date', table_name='base_materials')
    
    # Drop columns
    op.drop_column('base_materials', 'price_source')
    op.drop_column('base_materials', 'price_date')
    op.drop_column('base_materials', 'price_type')