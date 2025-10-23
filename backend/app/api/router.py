from fastapi import APIRouter
from app.api import auth, projects, materials, unmatched_materials, material_category_simplified, matching, analysis, reasonability, reports

api_router = APIRouter()

# 认证相关路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

# 项目相关路由
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["项目管理"]
)

# 基准材料相关路由
api_router.include_router(
    materials.router,
    prefix="/base-materials",
    tags=["基准材料管理"]
)

# 无市场信息价材料相关路由
api_router.include_router(
    unmatched_materials.router,
    prefix="/unmatched-materials",
    tags=["无市场信息价材料管理"]
)

# 材料分类相关路由
api_router.include_router(
    material_category_simplified.router,
    tags=["材料分类管理"]
)

# 材料匹配相关路由
api_router.include_router(
    matching.router,
    prefix="/matching",
    tags=["材料匹配"]
)

# 价格分析相关路由
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["价格分析"]
)

# 价格合理性分析相关路由
api_router.include_router(
    reasonability.router,
    prefix="/reasonability",
    tags=["价格合理性分析"]
)

# 报告生成相关路由
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["报告生成"]
)

@api_router.get("/")
async def root():
    return {"message": "造价材料审计系统 API v1.0"}

@api_router.get("/health")
async def health():
    """API健康检查端点"""
    return {
        "status": "healthy",
        "message": "API服务运行正常",
        "version": "1.0.0"
    }