from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import create_tables
from app.core.middleware import (
    RateLimitMiddleware,
    SecurityMiddleware,
    RequestLoggingMiddleware,
    ConcurrencyLimitMiddleware,
    HealthCheckMiddleware
)
from app.core.error_handlers import register_exception_handlers
from app.api.router import api_router

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation=settings.LOG_FILE_MAX_SIZE,
    retention=settings.LOG_FILE_BACKUP_COUNT
)

# 全局健康检查中间件实例
health_middleware = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    try:
        # 启动时执行
        logger.info("🚀 启动造价材料审计系统... [热重载测试]")
        logger.info(f"📊 配置信息: DEBUG={settings.DEBUG}, LOG_LEVEL={settings.LOG_LEVEL}")
        logger.info("⚡ 热重载功能已启用！代码修改会自动生效")
        
        await create_tables()
        logger.success("✅ 数据库表创建完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 应用启动失败: {e}")
        raise
    finally:
        # 关闭时执行
        logger.info("🔄 正在关闭应用...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    global health_middleware
    
    app = FastAPI(
        title="造价材料审计系统",
        description="基于AI的造价材料审计系统API - 提供材料价格智能分析和审计报告生成功能",
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url=None,  # 禁用默认文档
        redoc_url=None,  # 禁用ReDoc  
        openapi_url="/api/openapi.json" if settings.DEBUG else None
    )
    
    # 健康检查中间件（必须最先添加）
    health_middleware = HealthCheckMiddleware(app)
    app.add_middleware(HealthCheckMiddleware)
    
    # 安全中间件
    app.add_middleware(SecurityMiddleware)
    
    # 并发限制中间件
    app.add_middleware(
        ConcurrencyLimitMiddleware,
        max_concurrent=settings.MAX_CONCURRENT_REQUESTS
    )
    
    # 访问频率限制中间件
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.API_RATE_LIMIT,
        period=60  # 1分钟
    )
    
    # 请求日志中间件
    if settings.DEBUG:
        app.add_middleware(RequestLoggingMiddleware)
    
    # 受信任主机中间件 - 开发环境允许所有主机
    if settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["*"]
        )
    else:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # CORS中间件 - 开发环境允许所有来源
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,  # allow_origins=["*"]时必须为False
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
        )
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 静态文件服务
    if settings.DEBUG:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 注册API路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 完整的Swagger UI（使用本地资源，无外部依赖）
    if settings.DEBUG:
        @app.get("/docs", response_class=HTMLResponse)
        async def custom_swagger_ui_docs():
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <link type="text/css" rel="stylesheet" href="/static/swagger-ui/swagger-ui.css">
                <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
                <title>造价材料审计系统 - API文档</title>
                <style>
                    html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
                    *, *:before, *:after { box-sizing: inherit; }
                    body { margin:0; background: #fafafa; }
                </style>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
                <script>
                    const ui = SwaggerUIBundle({
                        url: '/api/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "BaseLayout",
                        defaultModelsExpandDepth: -1,
                        docExpansion: "list",
                        displayRequestDuration: true,
                        tryItOutEnabled: true,
                        supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                        validatorUrl: null,
                        onComplete: function(swaggerApi, swaggerUi) {
                            console.log("✅ 造价材料审计系统 API文档加载完成");
                        },
                        onFailure: function(data) {
                            console.error("❌ API文档加载失败:", data);
                        }
                    });
                </script>
            </body>
            </html>
            """)
        
        # 兼容旧地址：/api/docs -> /docs
        @app.get("/api/docs", include_in_schema=False)
        async def docs_redirect():
            return RedirectResponse(url="/docs", status_code=302)
    
    @app.get("/")
    async def root():
        """系统根路径"""
        return {
            "message": "造价材料审计系统API服务 - 开发模式热更新测试 ✅",
            "version": settings.VERSION,
            "docs_url": "/api/docs" if settings.DEBUG else None,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """系统健康检查"""
        try:
            # 获取健康统计
            stats = health_middleware.get_health_stats() if health_middleware else {"status": "unknown"}
            
            return {
                "status": "healthy",
                "timestamp": "2025-08-28T00:00:00Z",
                "version": settings.VERSION,
                "environment": "production" if not settings.DEBUG else "development",
                **stats
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-08-28T00:00:00Z"
            }
    
    @app.get("/metrics")
    async def metrics():
        """系统指标（仅调试模式）"""
        if not settings.DEBUG:
            return {"error": "Metrics endpoint disabled in production"}
            
        stats = health_middleware.get_health_stats() if health_middleware else {}
        return {
            "system": stats,
            "config": {
                "max_concurrent": settings.MAX_CONCURRENT_REQUESTS,
                "rate_limit": settings.API_RATE_LIMIT,
                "max_file_size": settings.MAX_FILE_SIZE,
                "ai_timeout": settings.AI_TIMEOUT
            }
        }
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
