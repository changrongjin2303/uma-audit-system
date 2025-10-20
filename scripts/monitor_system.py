#!/usr/bin/env python3
"""
系统监控脚本
"""
import asyncio
import psutil
import time
import json
import aiohttp
import asyncpg
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from dataclasses import dataclass, asdict
from loguru import logger
import sys

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from backend.app.core.config import settings


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: List[float]


@dataclass
class DatabaseMetrics:
    """数据库指标数据类"""
    timestamp: str
    active_connections: int
    max_connections: int
    database_size_mb: float
    table_count: int
    slow_queries: int
    cache_hit_ratio: float


@dataclass
class ApplicationMetrics:
    """应用指标数据类"""
    timestamp: str
    response_time_ms: float
    status_code: int
    is_healthy: bool
    error_rate: float
    active_users: int


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, output_dir: str = "monitoring"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.output_dir / "system_metrics.jsonl"
        self.alerts_file = self.output_dir / "alerts.log"
        
        # 设置日志
        self._setup_logging()
        
        # 监控阈值
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_ms": 5000.0,
            "error_rate": 10.0
        }
    
    def _setup_logging(self):
        """设置监控日志"""
        log_file = self.output_dir / "monitor.log"
        logger.add(
            str(log_file),
            rotation="50 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存指标
            memory = psutil.virtual_memory()
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            
            # 网络指标
            network = psutil.net_io_counters()
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 负载平均值
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_percent=disk.percent,
                disk_used_gb=disk.used / 1024 / 1024 / 1024,
                disk_free_gb=disk.free / 1024 / 1024 / 1024,
                network_sent_mb=network.bytes_sent / 1024 / 1024,
                network_recv_mb=network.bytes_recv / 1024 / 1024,
                process_count=process_count,
                load_average=list(load_avg)
            )
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
            raise
    
    async def collect_database_metrics(self) -> Optional[DatabaseMetrics]:
        """收集数据库指标"""
        try:
            # 解析数据库连接URL
            import urllib.parse
            parsed = urllib.parse.urlparse(settings.DATABASE_URL.replace("postgresql://", "postgres://"))
            
            # 连接数据库
            conn = await asyncpg.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/'),
                user=parsed.username,
                password=parsed.password
            )
            
            try:
                # 获取连接数
                active_connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                
                max_connections = await conn.fetchval("SHOW max_connections")
                max_connections = int(max_connections)
                
                # 获取数据库大小
                database_size = await conn.fetchval(
                    "SELECT pg_database_size(current_database())"
                )
                database_size_mb = database_size / 1024 / 1024
                
                # 获取表数量
                table_count = await conn.fetchval(
                    "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
                )
                
                # 获取慢查询数量（假设慢查询定义为执行时间>1秒）
                slow_queries = await conn.fetchval(
                    """
                    SELECT count(*) FROM pg_stat_statements 
                    WHERE mean_time > 1000
                    """
                ) or 0
                
                # 获取缓存命中率
                cache_stats = await conn.fetchrow(
                    """
                    SELECT 
                        sum(heap_blks_hit) as hits,
                        sum(heap_blks_hit + heap_blks_read) as total
                    FROM pg_statio_user_tables
                    """
                )
                
                if cache_stats and cache_stats['total'] > 0:
                    cache_hit_ratio = (cache_stats['hits'] / cache_stats['total']) * 100
                else:
                    cache_hit_ratio = 0.0
                
                return DatabaseMetrics(
                    timestamp=datetime.now().isoformat(),
                    active_connections=active_connections,
                    max_connections=max_connections,
                    database_size_mb=database_size_mb,
                    table_count=table_count,
                    slow_queries=slow_queries,
                    cache_hit_ratio=cache_hit_ratio
                )
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"收集数据库指标失败: {e}")
            return None
    
    async def collect_application_metrics(self) -> Optional[ApplicationMetrics]:
        """收集应用指标"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # 健康检查
                async with session.get("http://localhost:8000/health") as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    is_healthy = response.status == 200
                    
                    # 获取应用统计信息（如果可用）
                    try:
                        async with session.get("http://localhost:8000/metrics") as metrics_response:
                            if metrics_response.status == 200:
                                metrics_data = await metrics_response.json()
                                system_stats = metrics_data.get("system", {})
                                error_rate = system_stats.get("error_rate_percent", 0.0)
                                active_users = 0  # TODO: 实现活跃用户统计
                            else:
                                error_rate = 0.0
                                active_users = 0
                    except:
                        error_rate = 0.0
                        active_users = 0
                    
                    return ApplicationMetrics(
                        timestamp=datetime.now().isoformat(),
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        is_healthy=is_healthy,
                        error_rate=error_rate,
                        active_users=active_users
                    )
                    
        except Exception as e:
            logger.error(f"收集应用指标失败: {e}")
            return None
    
    def check_alerts(self, system_metrics: SystemMetrics, 
                    db_metrics: Optional[DatabaseMetrics],
                    app_metrics: Optional[ApplicationMetrics]):
        """检查告警条件"""
        alerts = []
        
        # 系统告警
        if system_metrics.cpu_percent > self.thresholds["cpu_percent"]:
            alerts.append(f"CPU使用率过高: {system_metrics.cpu_percent:.1f}%")
        
        if system_metrics.memory_percent > self.thresholds["memory_percent"]:
            alerts.append(f"内存使用率过高: {system_metrics.memory_percent:.1f}%")
        
        if system_metrics.disk_percent > self.thresholds["disk_percent"]:
            alerts.append(f"磁盘使用率过高: {system_metrics.disk_percent:.1f}%")
        
        # 数据库告警
        if db_metrics:
            connection_ratio = db_metrics.active_connections / db_metrics.max_connections
            if connection_ratio > 0.8:
                alerts.append(f"数据库连接数过高: {db_metrics.active_connections}/{db_metrics.max_connections}")
            
            if db_metrics.cache_hit_ratio < 90:
                alerts.append(f"数据库缓存命中率过低: {db_metrics.cache_hit_ratio:.1f}%")
        
        # 应用告警
        if app_metrics:
            if not app_metrics.is_healthy:
                alerts.append(f"应用健康检查失败: HTTP {app_metrics.status_code}")
            
            if app_metrics.response_time_ms > self.thresholds["response_time_ms"]:
                alerts.append(f"应用响应时间过长: {app_metrics.response_time_ms:.1f}ms")
            
            if app_metrics.error_rate > self.thresholds["error_rate"]:
                alerts.append(f"应用错误率过高: {app_metrics.error_rate:.1f}%")
        
        # 记录告警
        if alerts:
            timestamp = datetime.now().isoformat()
            with open(self.alerts_file, 'a') as f:
                for alert in alerts:
                    f.write(f"{timestamp} | ALERT | {alert}\n")
                    logger.warning(f"告警: {alert}")
    
    def save_metrics(self, system_metrics: SystemMetrics,
                    db_metrics: Optional[DatabaseMetrics],
                    app_metrics: Optional[ApplicationMetrics]):
        """保存指标数据"""
        try:
            metrics_data = {
                "system": asdict(system_metrics),
                "database": asdict(db_metrics) if db_metrics else None,
                "application": asdict(app_metrics) if app_metrics else None
            }
            
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metrics_data, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"保存指标数据失败: {e}")
    
    async def run_once(self):
        """运行一次监控检查"""
        try:
            logger.info("开始收集系统指标")
            
            # 收集各类指标
            system_metrics = self.collect_system_metrics()
            db_metrics = await self.collect_database_metrics()
            app_metrics = await self.collect_application_metrics()
            
            # 检查告警
            self.check_alerts(system_metrics, db_metrics, app_metrics)
            
            # 保存指标
            self.save_metrics(system_metrics, db_metrics, app_metrics)
            
            logger.info("系统指标收集完成")
            
            return {
                "system": asdict(system_metrics),
                "database": asdict(db_metrics) if db_metrics else None,
                "application": asdict(app_metrics) if app_metrics else None
            }
            
        except Exception as e:
            logger.error(f"监控检查失败: {e}")
            raise
    
    async def run_continuous(self, interval: int = 60):
        """持续监控"""
        logger.info(f"开始持续监控，间隔 {interval} 秒")
        
        while True:
            try:
                await self.run_once()
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("接收到停止信号，退出监控")
                break
            except Exception as e:
                logger.error(f"监控异常: {e}")
                await asyncio.sleep(interval)
    
    def get_recent_metrics(self, hours: int = 24) -> List[Dict]:
        """获取最近的指标数据"""
        if not self.metrics_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = []
        
        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        timestamp_str = data.get("system", {}).get("timestamp")
                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            if timestamp >= cutoff_time:
                                recent_metrics.append(data)
                    except:
                        continue
            
            return sorted(recent_metrics, key=lambda x: x["system"]["timestamp"])
            
        except Exception as e:
            logger.error(f"读取指标数据失败: {e}")
            return []


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="系统监控")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只运行一次")
    parser.add_argument("--output-dir", default="monitoring", help="输出目录")
    parser.add_argument("--recent", type=int, help="显示最近N小时的数据")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(output_dir=args.output_dir)
    
    try:
        if args.recent:
            # 显示最近的监控数据
            metrics = monitor.get_recent_metrics(hours=args.recent)
            print(f"\n📊 最近 {args.recent} 小时的监控数据:\n")
            
            for data in metrics[-10:]:  # 显示最近10条
                system = data["system"]
                print(f"时间: {system['timestamp']}")
                print(f"CPU: {system['cpu_percent']:.1f}%")
                print(f"内存: {system['memory_percent']:.1f}%")
                print(f"磁盘: {system['disk_percent']:.1f}%")
                
                if data["application"]:
                    app = data["application"]
                    print(f"应用: 响应时间 {app['response_time_ms']:.1f}ms, 健康状态 {'✅' if app['is_healthy'] else '❌'}")
                
                print("-" * 50)
                
        elif args.once:
            # 运行一次
            result = await monitor.run_once()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            # 持续监控
            await monitor.run_continuous(interval=args.interval)
            
    except KeyboardInterrupt:
        print("\n监控已停止")
    except Exception as e:
        logger.error(f"监控失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())