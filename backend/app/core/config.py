from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union
import os
import secrets


def generate_secret_key() -> str:
    """生成安全的密钥"""
    return secrets.token_urlsafe(64)


class Settings(BaseSettings):
    """系统配置类"""
    
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"],
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # 基本配置
    PROJECT_NAME: str = "造价材料审计系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # CORS配置
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/uma_audit"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT安全配置
    SECRET_KEY: str = generate_secret_key()  # 默认生成安全密钥
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API安全限制
    API_RATE_LIMIT: int = 100  # 每分钟请求次数
    API_BURST_LIMIT: int = 20   # 突发请求次数  
    MAX_CONCURRENT_REQUESTS: int = 50
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["xlsx", "xls", "csv", "pdf", "doc", "docx"]
    
    # AI服务配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 通义千问配置
    DASHSCOPE_API_KEY: Optional[str] = None
    DASHSCOPE_MODEL: str = "qwen3-max"
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 百度文心一言配置
    BAIDU_API_KEY: Optional[str] = None
    BAIDU_SECRET_KEY: Optional[str] = None
    
    # 搜索配置
    BING_SEARCH_API_KEY: Optional[str] = None
    BAIDU_SEARCH_API_KEY: Optional[str] = None
    
    # AI分析配置
    AI_TIMEOUT: int = 30  # 秒
    AI_RETRY_TIMES: int = 3
    AI_MAX_CONCURRENT: int = 5
    AI_COST_LIMIT: float = 0.1  # 单次分析成本上限(元)
    
    # 系统限制
    MAX_MATERIALS_PER_BATCH: int = 50000
    API_CALL_RATE_LIMIT: int = 100  # 每分钟
    MAX_QUERY_COST: float = 0.1  # 单次查询成本上限（元）
    
    # 数据安全配置
    DATA_ENCRYPTION_KEY: Optional[str] = None
    BACKUP_ENCRYPTION: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 365
    
    # 数据保留策略
    PROJECT_DATA_RETENTION_DAYS: int = 1095  # 3年
    SYSTEM_LOG_RETENTION_DAYS: int = 365  # 1年
    
    # 监控和日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    LOG_FILE_MAX_SIZE: str = "100MB"
    LOG_FILE_BACKUP_COUNT: int = 10
    
    @property
    def cors_origins_list(self) -> List[str]:
        """解析CORS_ORIGINS配置"""
        if isinstance(self.CORS_ORIGINS, str):
            import json
            try:
                return json.loads(self.CORS_ORIGINS)
            except:
                return [self.CORS_ORIGINS]
        return self.CORS_ORIGINS
    


settings = Settings()