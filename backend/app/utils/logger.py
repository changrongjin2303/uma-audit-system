"""
日志管理工具
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import gzip
import glob
from typing import Optional
from loguru import logger

from app.core.config import settings


class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.log_dir = Path(settings.LOG_FILE).parent
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """设置日志配置"""
        # 移除默认处理器
        logger.remove()
        
        # 控制台日志
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True,
            diagnose=True
        )
        
        # 文件日志
        logger.add(
            settings.LOG_FILE,
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=settings.LOG_FILE_MAX_SIZE,
            retention=f"{settings.LOG_FILE_BACKUP_COUNT} files",
            compression="gz",
            diagnose=True,
            backtrace=True
        )
        
        # 错误日志单独文件
        error_log_file = self.log_dir / "error.log"
        logger.add(
            str(error_log_file),
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            diagnose=True,
            backtrace=True
        )
        
        # 审计日志
        audit_log_file = self.log_dir / "audit.log"
        logger.add(
            str(audit_log_file),
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[category]} | {message}",
            filter=lambda record: record.get("extra", {}).get("category") == "audit",
            rotation="50 MB",
            retention=f"{settings.AUDIT_LOG_RETENTION_DAYS} days",
            compression="gz"
        )
    
    def get_log_files(self) -> list:
        """获取所有日志文件"""
        log_files = []
        
        # 获取当前日志文件
        if os.path.exists(settings.LOG_FILE):
            log_files.append({
                "name": Path(settings.LOG_FILE).name,
                "path": settings.LOG_FILE,
                "size": os.path.getsize(settings.LOG_FILE),
                "modified": datetime.fromtimestamp(os.path.getmtime(settings.LOG_FILE)),
                "type": "current"
            })
        
        # 获取归档日志文件
        pattern = str(self.log_dir / "app.log.*")
        for file_path in glob.glob(pattern):
            log_files.append({
                "name": Path(file_path).name,
                "path": file_path,
                "size": os.path.getsize(file_path),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)),
                "type": "archived"
            })
        
        return sorted(log_files, key=lambda x: x["modified"], reverse=True)
    
    def read_log_tail(self, lines: int = 100, log_file: Optional[str] = None) -> list:
        """读取日志文件尾部内容"""
        target_file = log_file or settings.LOG_FILE
        
        if not os.path.exists(target_file):
            return []
            
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.readlines()
                return [line.strip() for line in content[-lines:]]
        except Exception as e:
            logger.error(f"读取日志文件失败: {e}")
            return []
    
    def search_logs(self, keyword: str, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None, log_level: Optional[str] = None) -> list:
        """搜索日志内容"""
        results = []
        
        try:
            with open(settings.LOG_FILE, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 关键词匹配
                    if keyword and keyword.lower() not in line.lower():
                        continue
                    
                    # 日期范围过滤
                    try:
                        # 提取日志时间戳（假设格式为 YYYY-MM-DD HH:mm:ss）
                        log_time_str = line[:19]
                        log_time = datetime.strptime(log_time_str, "%Y-%m-%d %H:%M:%S")
                        
                        if start_date and log_time < start_date:
                            continue
                        if end_date and log_time > end_date:
                            continue
                    except:
                        pass  # 时间解析失败，跳过过滤
                    
                    # 日志级别过滤
                    if log_level and log_level.upper() not in line.upper():
                        continue
                    
                    results.append({
                        "line_number": line_num,
                        "content": line,
                        "timestamp": log_time_str if 'log_time_str' in locals() else None
                    })
        
        except Exception as e:
            logger.error(f"搜索日志失败: {e}")
        
        return results
    
    def cleanup_old_logs(self):
        """清理过期日志文件"""
        try:
            # 清理应用日志
            retention_days = settings.LOG_FILE_BACKUP_COUNT
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            pattern = str(self.log_dir / "app.log.*")
            for file_path in glob.glob(pattern):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"已删除过期日志文件: {file_path}")
            
            # 清理审计日志
            audit_retention_days = settings.AUDIT_LOG_RETENTION_DAYS
            audit_cutoff_date = datetime.now() - timedelta(days=audit_retention_days)
            
            pattern = str(self.log_dir / "audit.log.*")
            for file_path in glob.glob(pattern):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < audit_cutoff_date:
                    os.remove(file_path)
                    logger.info(f"已删除过期审计日志: {file_path}")
                    
        except Exception as e:
            logger.error(f"清理日志失败: {e}")
    
    def get_log_statistics(self) -> dict:
        """获取日志统计信息"""
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "current_log_size": 0,
                "oldest_log": None,
                "newest_log": None,
                "log_levels": {
                    "DEBUG": 0,
                    "INFO": 0,
                    "WARNING": 0,
                    "ERROR": 0,
                    "CRITICAL": 0
                }
            }
            
            log_files = self.get_log_files()
            stats["total_files"] = len(log_files)
            
            for log_file in log_files:
                stats["total_size"] += log_file["size"]
                
                if log_file["type"] == "current":
                    stats["current_log_size"] = log_file["size"]
                
                if not stats["oldest_log"] or log_file["modified"] < stats["oldest_log"]:
                    stats["oldest_log"] = log_file["modified"]
                
                if not stats["newest_log"] or log_file["modified"] > stats["newest_log"]:
                    stats["newest_log"] = log_file["modified"]
            
            # 统计当前日志文件中的日志级别
            if os.path.exists(settings.LOG_FILE):
                with open(settings.LOG_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        for level in stats["log_levels"].keys():
                            if f"| {level: <8} |" in line:
                                stats["log_levels"][level] += 1
                                break
            
            return stats
            
        except Exception as e:
            logger.error(f"获取日志统计失败: {e}")
            return {}


# 创建全局日志管理器实例
log_manager = LogManager()


def audit_log(action: str, resource: str, user_id: Optional[int] = None, 
              details: Optional[dict] = None):
    """记录审计日志"""
    logger.bind(category="audit").info(
        f"Action: {action} | Resource: {resource} | User: {user_id} | Details: {details or {}}"
    )


def security_log(event: str, ip_address: str, user_agent: str, 
                 user_id: Optional[int] = None, details: Optional[dict] = None):
    """记录安全日志"""
    logger.bind(category="security").warning(
        f"Security Event: {event} | IP: {ip_address} | User: {user_id} | "
        f"User-Agent: {user_agent} | Details: {details or {}}"
    )


def performance_log(operation: str, duration: float, details: Optional[dict] = None):
    """记录性能日志"""
    logger.bind(category="performance").info(
        f"Performance: {operation} | Duration: {duration:.3f}s | Details: {details or {}}"
    )