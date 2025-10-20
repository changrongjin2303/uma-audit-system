"""
自定义异常类
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseCustomException(Exception):
    """基础自定义异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class BusinessException(BaseCustomException):
    """业务逻辑异常"""
    pass


class ValidationException(BaseCustomException):
    """数据验证异常"""
    pass


class AuthenticationException(BaseCustomException):
    """认证异常"""
    pass


class AuthorizationException(BaseCustomException):
    """授权异常"""
    pass


class ResourceNotFoundException(BaseCustomException):
    """资源不存在异常"""
    pass


class DatabaseException(BaseCustomException):
    """数据库异常"""
    pass


class ExternalServiceException(BaseCustomException):
    """外部服务异常"""
    pass


class AIServiceException(ExternalServiceException):
    """AI服务异常"""
    pass


class FileProcessingException(BaseCustomException):
    """文件处理异常"""
    pass


class RateLimitException(BaseCustomException):
    """访问频率限制异常"""
    pass


class ConfigurationException(BaseCustomException):
    """配置异常"""
    pass


# HTTP异常工厂函数
def http_400_bad_request(message: str, error_code: str = "BAD_REQUEST", details: Dict[str, Any] = None):
    """400错误"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": error_code,
            "message": message,
            "details": details or {}
        }
    )


def http_401_unauthorized(message: str = "未授权访问", error_code: str = "UNAUTHORIZED"):
    """401错误"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": error_code,
            "message": message
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


def http_403_forbidden(message: str = "访问被拒绝", error_code: str = "FORBIDDEN"):
    """403错误"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": error_code,
            "message": message
        }
    )


def http_404_not_found(message: str, error_code: str = "NOT_FOUND", resource: str = None):
    """404错误"""
    details = {}
    if resource:
        details["resource"] = resource
        
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": error_code,
            "message": message,
            "details": details
        }
    )


def http_409_conflict(message: str, error_code: str = "CONFLICT", details: Dict[str, Any] = None):
    """409错误"""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": error_code,
            "message": message,
            "details": details or {}
        }
    )


def http_422_validation_error(message: str, field_errors: Dict[str, str] = None):
    """422验证错误"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": "VALIDATION_ERROR",
            "message": message,
            "field_errors": field_errors or {}
        }
    )


def http_429_rate_limit(message: str = "请求过于频繁", retry_after: int = 60):
    """429频率限制错误"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "RATE_LIMIT_EXCEEDED",
            "message": message,
            "retry_after": retry_after
        },
        headers={"Retry-After": str(retry_after)}
    )


def http_500_internal_error(message: str = "服务器内部错误", error_code: str = "INTERNAL_ERROR"):
    """500内部错误"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": error_code,
            "message": message
        }
    )


def http_502_bad_gateway(message: str = "上游服务不可用", service: str = None):
    """502网关错误"""
    details = {}
    if service:
        details["service"] = service
        
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "error": "BAD_GATEWAY",
            "message": message,
            "details": details
        }
    )


def http_503_service_unavailable(message: str = "服务暂时不可用", retry_after: int = 300):
    """503服务不可用"""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error": "SERVICE_UNAVAILABLE",
            "message": message,
            "retry_after": retry_after
        },
        headers={"Retry-After": str(retry_after)}
    )