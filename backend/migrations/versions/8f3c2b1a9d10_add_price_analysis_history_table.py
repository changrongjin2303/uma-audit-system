"""Add price_analysis_history table for analysis timeline

Revision ID: 8f3c2b1a9d10
Revises: 7b3a1c8f9c21
Create Date: 2025-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f3c2b1a9d10"
down_revision = "7b3a1c8f9c21"
branch_labels = None
depends_on = None


def upgrade() -> None:
  """Create price_analysis_history table."""
  op.create_table(
      "price_analysis_history",
      sa.Column("id", sa.Integer(), primary_key=True, index=True),
      sa.Column(
          "material_id",
          sa.Integer(),
          sa.ForeignKey("project_materials.id", ondelete="CASCADE"),
          nullable=False,
          comment="项目材料ID",
      ),
      sa.Column(
          "status",
          sa.String(length=20),
          nullable=True,
          comment="分析状态(字符串形式，存枚举值)",
      ),
      sa.Column(
          "predicted_price_min",
          sa.Float(),
          nullable=True,
          comment="预测价格下限",
      ),
      sa.Column(
          "predicted_price_max",
          sa.Float(),
          nullable=True,
          comment="预测价格上限",
      ),
      sa.Column(
          "confidence_score",
          sa.Float(),
          nullable=True,
          comment="置信度评分",
      ),
      sa.Column(
          "risk_level",
          sa.String(length=20),
          nullable=True,
          comment="风险等级",
      ),
      sa.Column(
          "analysis_model",
          sa.String(length=50),
          nullable=True,
          comment="使用的AI模型",
      ),
      sa.Column(
          "analysis_cost",
          sa.Float(),
          nullable=True,
          comment="分析成本",
      ),
      sa.Column(
          "analysis_time",
          sa.Float(),
          nullable=True,
          comment="分析耗时（秒）",
      ),
      sa.Column(
          "analysis_reasoning",
          sa.Text(),
          nullable=True,
          comment="分析简要说明/备注",
      ),
      sa.Column(
          "created_at",
          sa.DateTime(timezone=True),
          server_default=sa.func.now(),
          nullable=True,
          comment="历史记录时间",
      ),
  )

  op.create_index(
      "ix_price_analysis_history_material",
      "price_analysis_history",
      ["material_id"],
  )
  op.create_index(
      "ix_price_analysis_history_status",
      "price_analysis_history",
      ["status"],
  )


def downgrade() -> None:
  """Drop price_analysis_history table."""
  op.drop_index("ix_price_analysis_history_status", table_name="price_analysis_history")
  op.drop_index("ix_price_analysis_history_material", table_name="price_analysis_history")
  op.drop_table("price_analysis_history")


