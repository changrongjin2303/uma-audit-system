"""add needs_review fields to project_materials and projects

Revision ID: 9d4e5f6a7b8c
Revises: 8f3c2b1a9d10
Create Date: 2024-12-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d4e5f6a7b8c'
down_revision = '8f3c2b1a9d10'
branch_labels = None
depends_on = None


def upgrade():
    # 添加 needs_review 字段到 project_materials 表
    op.add_column('project_materials', 
        sa.Column('needs_review', sa.Boolean(), nullable=True, default=False, 
                  comment='是否需人工复核(相似度0.65-0.85)')
    )
    
    # 添加 needs_review_materials 字段到 projects 表
    op.add_column('projects',
        sa.Column('needs_review_materials', sa.Integer(), nullable=True, default=0,
                  comment='需人工复核材料数量(相似度0.65-0.85)')
    )
    
    # 设置默认值
    op.execute("UPDATE project_materials SET needs_review = false WHERE needs_review IS NULL")
    op.execute("UPDATE projects SET needs_review_materials = 0 WHERE needs_review_materials IS NULL")


def downgrade():
    op.drop_column('project_materials', 'needs_review')
    op.drop_column('projects', 'needs_review_materials')
