#!/usr/bin/env python3
"""
数据库备份脚本
"""
import os
import sys
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import yaml
import json
from typing import Dict, List, Optional
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.core.config import settings


class DatabaseBackup:
    """数据库备份管理器"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析数据库URL
        self.db_config = self._parse_database_url(settings.DATABASE_URL)
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置备份日志"""
        log_file = self.backup_dir / "backup.log"
        logger.add(
            str(log_file),
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
    
    def _parse_database_url(self, database_url: str) -> Dict[str, str]:
        """解析数据库连接URL"""
        # postgresql://user:password@host:port/database
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            return {
                "host": parsed.hostname or "localhost",
                "port": str(parsed.port or 5432),
                "database": parsed.path.lstrip('/'),
                "username": parsed.username,
                "password": parsed.password,
                "scheme": parsed.scheme
            }
        except Exception as e:
            logger.error(f"解析数据库URL失败: {e}")
            raise
    
    def create_backup(self, backup_name: Optional[str] = None, 
                     compress: bool = True) -> str:
        """创建数据库备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"uma_audit_backup_{timestamp}"
        
        backup_file = self.backup_dir / f"{backup_name}.sql"
        
        try:
            logger.info(f"开始创建数据库备份: {backup_name}")
            
            # 构建pg_dump命令
            cmd = [
                "pg_dump",
                "-h", self.db_config["host"],
                "-p", self.db_config["port"],
                "-U", self.db_config["username"],
                "-d", self.db_config["database"],
                "--verbose",
                "--clean",
                "--create",
                "--if-exists",
                "-f", str(backup_file)
            ]
            
            # 设置环境变量
            env = os.environ.copy()
            if self.db_config["password"]:
                env["PGPASSWORD"] = self.db_config["password"]
            
            # 执行备份命令
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode != 0:
                raise Exception(f"备份失败: {result.stderr}")
            
            # 压缩备份文件
            if compress:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原始文件
                backup_file.unlink()
                backup_file = Path(compressed_file)
            
            # 记录备份信息
            backup_info = {
                "name": backup_name,
                "file": str(backup_file),
                "timestamp": timestamp,
                "size": backup_file.stat().st_size,
                "compressed": compress,
                "database": self.db_config["database"],
                "host": self.db_config["host"]
            }
            
            info_file = self.backup_dir / f"{backup_name}.json"
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.success(f"备份创建成功: {backup_file}")
            logger.info(f"备份大小: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
            
            return str(backup_file)
            
        except subprocess.TimeoutExpired:
            logger.error("备份超时")
            raise
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            # 清理失败的备份文件
            if backup_file.exists():
                backup_file.unlink()
            raise
    
    def restore_backup(self, backup_file: str, target_database: Optional[str] = None):
        """恢复数据库备份"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_file}")
        
        target_db = target_database or self.db_config["database"]
        
        try:
            logger.info(f"开始恢复数据库备份: {backup_file} -> {target_db}")
            
            # 如果是压缩文件，先解压
            temp_file = None
            if backup_path.suffix == '.gz':
                temp_file = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_file = temp_file
            else:
                restore_file = backup_path
            
            # 构建psql命令
            cmd = [
                "psql",
                "-h", self.db_config["host"],
                "-p", self.db_config["port"],
                "-U", self.db_config["username"],
                "-d", target_db,
                "-f", str(restore_file)
            ]
            
            # 设置环境变量
            env = os.environ.copy()
            if self.db_config["password"]:
                env["PGPASSWORD"] = self.db_config["password"]
            
            # 执行恢复命令
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            # 清理临时文件
            if temp_file and temp_file.exists():
                temp_file.unlink()
            
            if result.returncode != 0:
                raise Exception(f"恢复失败: {result.stderr}")
            
            logger.success(f"数据库恢复成功: {target_db}")
            
        except subprocess.TimeoutExpired:
            logger.error("恢复超时")
            raise
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            raise
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        
        for info_file in self.backup_dir.glob("*.json"):
            try:
                with open(info_file) as f:
                    backup_info = json.load(f)
                    
                # 检查备份文件是否存在
                backup_file = Path(backup_info["file"])
                if backup_file.exists():
                    backup_info["exists"] = True
                    backup_info["size"] = backup_file.stat().st_size
                else:
                    backup_info["exists"] = False
                
                backups.append(backup_info)
                
            except Exception as e:
                logger.warning(f"读取备份信息失败 {info_file}: {e}")
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """清理过期备份"""
        backups = self.list_backups()
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # 按时间排序，保留最近的备份
        sorted_backups = sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        
        deleted_count = 0
        for i, backup in enumerate(sorted_backups):
            backup_time = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")
            
            # 保留最近的几个备份，或者在时间范围内的备份
            if i < keep_count and backup_time >= cutoff_date:
                continue
            
            # 删除过期备份
            try:
                backup_file = Path(backup["file"])
                info_file = self.backup_dir / f"{backup['name']}.json"
                
                if backup_file.exists():
                    backup_file.unlink()
                if info_file.exists():
                    info_file.unlink()
                
                deleted_count += 1
                logger.info(f"已删除过期备份: {backup['name']}")
                
            except Exception as e:
                logger.error(f"删除备份失败 {backup['name']}: {e}")
        
        logger.info(f"清理完成，删除了 {deleted_count} 个过期备份")
        return deleted_count
    
    def get_backup_statistics(self) -> Dict:
        """获取备份统计信息"""
        backups = self.list_backups()
        
        total_size = sum(backup.get("size", 0) for backup in backups if backup.get("exists", False))
        
        stats = {
            "total_backups": len(backups),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "oldest_backup": None,
            "newest_backup": None,
            "avg_size_mb": 0
        }
        
        if backups:
            stats["oldest_backup"] = min(backups, key=lambda x: x["timestamp"])["timestamp"]
            stats["newest_backup"] = max(backups, key=lambda x: x["timestamp"])["timestamp"]
            
            if stats["total_backups"] > 0:
                stats["avg_size_mb"] = round(stats["total_size_mb"] / stats["total_backups"], 2)
        
        return stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库备份管理")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 创建备份
    create_parser = subparsers.add_parser("create", help="创建备份")
    create_parser.add_argument("--name", help="备份名称")
    create_parser.add_argument("--no-compress", action="store_true", help="不压缩备份")
    
    # 恢复备份
    restore_parser = subparsers.add_parser("restore", help="恢复备份")
    restore_parser.add_argument("backup_file", help="备份文件路径")
    restore_parser.add_argument("--target-db", help="目标数据库名称")
    
    # 列出备份
    subparsers.add_parser("list", help="列出所有备份")
    
    # 清理备份
    cleanup_parser = subparsers.add_parser("cleanup", help="清理过期备份")
    cleanup_parser.add_argument("--keep-days", type=int, default=30, help="保留天数")
    cleanup_parser.add_argument("--keep-count", type=int, default=10, help="保留数量")
    
    # 统计信息
    subparsers.add_parser("stats", help="显示备份统计信息")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    backup_manager = DatabaseBackup()
    
    try:
        if args.command == "create":
            backup_file = backup_manager.create_backup(
                backup_name=args.name,
                compress=not args.no_compress
            )
            print(f"备份创建成功: {backup_file}")
            
        elif args.command == "restore":
            backup_manager.restore_backup(
                args.backup_file,
                target_database=args.target_db
            )
            print("数据库恢复成功")
            
        elif args.command == "list":
            backups = backup_manager.list_backups()
            print(f"\n共找到 {len(backups)} 个备份:\n")
            
            for backup in backups:
                status = "✅" if backup.get("exists", False) else "❌"
                size_mb = backup.get("size", 0) / 1024 / 1024
                print(f"{status} {backup['name']}")
                print(f"   时间: {backup['timestamp']}")
                print(f"   大小: {size_mb:.2f} MB")
                print(f"   文件: {backup['file']}")
                print()
                
        elif args.command == "cleanup":
            deleted = backup_manager.cleanup_old_backups(
                keep_days=args.keep_days,
                keep_count=args.keep_count
            )
            print(f"清理完成，删除了 {deleted} 个过期备份")
            
        elif args.command == "stats":
            stats = backup_manager.get_backup_statistics()
            print(f"\n📊 备份统计信息:")
            print(f"   总备份数: {stats['total_backups']}")
            print(f"   总大小: {stats['total_size_mb']} MB")
            print(f"   平均大小: {stats['avg_size_mb']} MB")
            print(f"   最早备份: {stats['oldest_backup']}")
            print(f"   最新备份: {stats['newest_backup']}")
            
    except Exception as e:
        logger.error(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()