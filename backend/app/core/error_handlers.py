"""
全局错误处理器
"""
import traceback
from typing import Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.core.exceptions import (
    BaseCustomException,
    BusinessException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    DatabaseException,
    ExternalServiceException,
    AIServiceException,
    FileProcessingException,
    RateLimitException,
    ConfigurationException
)


async def custom_exception_handler(request: Request, exc: BaseCustomException) -> JSONResponse:
    """自定义异常处理器"""
    
    # 记录错误日志
    logger.error(f"自定义异常: {exc.error_code} - {exc.message}")
    logger.debug(f"异常详情: {exc.details}")
    logger.debug(f"请求路径: {request.url}")
    
    # 根据异常类型确定HTTP状态码
    status_code_map = {
        ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        AuthenticationException: status.HTTP_401_UNAUTHORIZED,
        AuthorizationException: status.HTTP_403_FORBIDDEN,
        ResourceNotFoundException: status.HTTP_404_NOT_FOUND,
        DatabaseException: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ExternalServiceException: status.HTTP_502_BAD_GATEWAY,
        AIServiceException: status.HTTP_503_SERVICE_UNAVAILABLE,
        FileProcessingException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        RateLimitException: status.HTTP_429_TOO_MANY_REQUESTS,
        ConfigurationException: status.HTTP_500_INTERNAL_SERVER_ERROR,
        BusinessException: status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    response_data = {
        "error": exc.error_code,
        "message": exc.message,
        "details": exc.details,
        "request_id": getattr(request.state, "request_id", None)
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    logger.debug(f"请求路径: {request.url}")
    
    # 如果detail是字符串，转换为标准格式
    if isinstance(exc.detail, str):
        detail = {
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "details": {}
        }
    else:
        detail = exc.detail
    
    # 添加请求ID
    if isinstance(detail, dict):
        detail["request_id"] = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=detail,
        headers=getattr(exc, "headers", None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    
    logger.warning(f"验证错误: {exc.errors()}")
    logger.debug(f"请求路径: {request.url}")
    
    # 安全地尝试读取请求体，避免客户端断开连接错误
    try:
        body = await request.body()
        logger.debug(f"请求体: {body}")
    except Exception as e:
        logger.debug(f"无法读取请求体: {e}")
    
    # 格式化验证错误
    field_errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # 跳过'body'
        field_errors[field] = error["msg"]
    
    response_data = {
        "error": "VALIDATION_ERROR",
        "message": "请求数据验证失败",
        "field_errors": field_errors,
        "details": {"raw_errors": exc.errors()},
        "request_id": getattr(request.state, "request_id", None)
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """数据库异常处理器"""
    
    logger.error(f"数据库错误: {str(exc)}")
    logger.debug(f"错误类型: {type(exc)}")
    logger.debug(f"请求路径: {request.url}")
    logger.debug(traceback.format_exc())
    
    # 根据具体的数据库错误类型返回不同的错误信息
    error_message = "数据库操作失败"
    error_code = "DATABASE_ERROR"
    
    # 常见数据库错误的友好提示
    error_str = str(exc).lower()
    if "unique constraint" in error_str or "duplicate" in error_str:
        error_message = "数据已存在，不能重复创建"
        error_code = "DUPLICATE_DATA"
    elif "foreign key constraint" in error_str:
        error_message = "数据关联约束失败，请检查相关数据"
        error_code = "FOREIGN_KEY_CONSTRAINT"
    elif "not null constraint" in error_str:
        error_message = "必填字段不能为空"
        error_code = "NOT_NULL_CONSTRAINT"
    elif "timeout" in error_str:
        error_message = "数据库连接超时，请稍后重试"
        error_code = "DATABASE_TIMEOUT"
    
    response_data = {
        "error": error_code,
        "message": error_message,
        "details": {},
        "request_id": getattr(request.state, "request_id", None)
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}")
    logger.error(f"请求路径: {request.url}")
    logger.error(traceback.format_exc())
    
    response_data = {
        "error": "INTERNAL_ERROR",
        "message": "服务器内部错误，请稍后重试",
        "details": {
            "exception_type": type(exc).__name__
        },
        "request_id": getattr(request.state, "request_id", None)
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    
    # 自定义异常处理器
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    
    # HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 数据库异常处理器
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # 通用异常处理器（最后添加）
    app.add_exception_handler(Exception, general_exception_handler)