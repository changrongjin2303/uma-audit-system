"""Add contract period fields to projects

Revision ID: 7b3a1c8f9c21
Revises: 1e7e189f80bd
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3a1c8f9c21'
down_revision = '1e7e189f80bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加合同工期字段（字符串格式 YYYY-MM）
    op.add_column('projects', sa.Column('contract_start_date', sa.String(length=20), nullable=True, comment='合同工期开始 (YYYY-MM)'))
    op.add_column('projects', sa.Column('contract_end_date', sa.String(length=20), nullable=True, comment='合同工期结束 (YYYY-MM)'))


def downgrade() -> None:
    # 回滚删除字段
    op.drop_column('projects', 'contract_end_date')
    op.drop_column('projects', 'contract_start_date')

