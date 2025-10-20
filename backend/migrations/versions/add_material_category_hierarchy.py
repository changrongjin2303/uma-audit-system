"""Add material category hierarchy

Revision ID: material_category_hierarchy
Revises: 199a61a88a9d
Create Date: 2025-09-09 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'material_category_hierarchy'
down_revision = '199a61a88a9d'
branch_labels = None
depends_on = None


def upgrade():
    # Create material_categories table
    op.create_table('material_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='分类名称'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='分类代码'),
        sa.Column('level', sa.Integer(), nullable=False, comment='层级 (1=信息来源类型, 2=年月, 3=具体分类)'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父分类ID'),
        sa.Column('source_type', sa.String(length=50), nullable=True, comment='信息来源类型 (municipal/provincial)'),
        sa.Column('year_month', sa.String(length=10), nullable=True, comment='年月 (YYYY-MM)'),
        sa.Column('sort_order', sa.Integer(), nullable=True, comment='排序序号'),
        sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否启用'),
        sa.Column('description', sa.Text(), nullable=True, comment='分类描述'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['parent_id'], ['material_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for material_categories
    op.create_index('ix_material_categories_level_parent', 'material_categories', ['level', 'parent_id'])
    op.create_index('ix_material_categories_source_type', 'material_categories', ['source_type'])
    op.create_index('ix_material_categories_year_month', 'material_categories', ['year_month'])
    op.create_index('ix_material_categories_code', 'material_categories', ['code'])
    op.create_index(op.f('ix_material_categories_id'), 'material_categories', ['id'])

    # Add category_id column to base_materials table
    op.add_column('base_materials', sa.Column('category_id', sa.Integer(), nullable=True, comment='所属分类ID'))
    op.create_foreign_key(None, 'base_materials', 'material_categories', ['category_id'], ['id'])
    
    # Insert default categories
    # 1. 信息来源类型 (Level 1)
    op.execute("""
        INSERT INTO material_categories (name, code, level, source_type, sort_order, is_active) VALUES
        ('市造价信息正刊', 'municipal', 1, 'municipal', 1, true),
        ('省造价信息正刊', 'provincial', 1, 'provincial', 2, true);
    """)


def downgrade():
    # Drop foreign key and column from base_materials
    op.drop_constraint(None, 'base_materials', type_='foreignkey')
    op.drop_column('base_materials', 'category_id')
    
    # Drop indexes
    op.drop_index('ix_material_categories_code', table_name='material_categories')
    op.drop_index('ix_material_categories_year_month', table_name='material_categories')
    op.drop_index('ix_material_categories_source_type', table_name='material_categories')
    op.drop_index('ix_material_categories_level_parent', table_name='material_categories')
    op.drop_index(op.f('ix_material_categories_id'), table_name='material_categories')
    
    # Drop table
    op.drop_table('material_categories')