import time
import asyncio
from typing import Dict, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
from datetime import datetime, timedelta
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API访问频率限制中间件"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # 允许的调用次数
        self.period = period  # 时间周期（秒）
        self.clients: Dict[str, deque] = defaultdict(deque)
        
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 检查是否需要限制
        if request.url.path.startswith("/api/docs") or request.url.path.startswith("/health"):
            return await call_next(request)
            
        # 检查访问频率
        now = time.time()
        client_calls = self.clients[client_ip]
        
        # 清理过期的调用记录
        while client_calls and client_calls[0] <= now - self.period:
            client_calls.popleft()
            
        # 检查是否超过限制
        if len(client_calls) >= self.calls:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls} requests per {self.period} seconds",
                    "retry_after": self.period
                }
            )
            
        # 记录本次调用
        client_calls.append(now)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限制信息到响应头
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(self.calls - len(client_calls))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 添加安全头
        response = await call_next(request)
        
        # 安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} [{user_agent}]"
        )
        
        try:
            response = await call_next(request)
            
            # 记录响应
            process_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} "
                f"({process_time:.3f}s) for {request.method} {request.url.path}"
            )
            
            # 添加处理时间头
            response.headers["X-Process-Time"] = str(f"{process_time:.3f}")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} ({process_time:.3f}s) "
                f"for {request.method} {request.url.path}"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"


class ConcurrencyLimitMiddleware(BaseHTTPMiddleware):
    """并发限制中间件"""
    
    def __init__(self, app, max_concurrent: int = 50):
        super().__init__(app)
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def dispatch(self, request: Request, call_next):
        # 跳过静态文件和健康检查
        if (request.url.path.startswith("/static") or 
            request.url.path in ["/health", "/", "/api/docs", "/api/redoc"]):
            return await call_next(request)
            
        # 检查并发限制
        try:
            async with self.semaphore:
                return await call_next(request)
        except asyncio.TimeoutError:
            logger.warning(f"Concurrency limit exceeded: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "Service temporarily unavailable",
                    "message": f"Server is handling too many requests. Max concurrent: {self.max_concurrent}",
                    "retry_after": 5
                }
            )


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """健康检查中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    async def dispatch(self, request: Request, call_next):
        self.request_count += 1
        
        try:
            response = await call_next(request)
            
            # 记录错误
            if response.status_code >= 400:
                self.error_count += 1
                
            return response
            
        except Exception as e:
            self.error_count += 1
            raise
    
    def get_health_stats(self) -> dict:
        """获取健康统计信息"""
        uptime = datetime.now() - self.start_time
        error_rate = (self.error_count / max(self.request_count, 1)) * 100
        
        return {
            "status": "healthy" if error_rate < 10 else "degraded",
            "uptime_seconds": int(uptime.total_seconds()),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate_percent": round(error_rate, 2)
        }