#!/usr/bin/env python3
"""
测试运行脚本
用法:
    python run_tests.py              # 运行所有测试
    python run_tests.py --unit       # 只运行单元测试
    python run_tests.py --coverage   # 运行测试并生成覆盖率报告
    python run_tests.py --fast       # 快速测试（跳过慢速测试）
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"运行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="运行测试套件")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--fast", action="store_true", help="跳过慢速测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--file", help="运行特定测试文件")
    parser.add_argument("--function", help="运行特定测试函数")
    
    args = parser.parse_args()
    
    # 设置工作目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查pytest是否安装
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest未安装，请先安装：pip install pytest pytest-asyncio")
        return False
    
    # 构建pytest命令
    cmd = ["pytest"]
    
    # 添加基本选项
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.extend(["-q", "--tb=short"])
    
    # 添加测试范围
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.fast:
        cmd.extend(["-m", "not slow"])
    
    # 添加覆盖率
    if args.coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=60"  # 最低覆盖率要求
        ])
    
    # 添加特定文件或函数
    if args.file:
        cmd.append(f"tests/{args.file}")
        if args.function:
            cmd.append(f"-k {args.function}")
    elif args.function:
        cmd.extend(["-k", args.function])
    
    # 添加其他有用的选项
    cmd.extend([
        "--strict-markers",
        "--strict-config",
        "--disable-warnings"
    ])
    
    print("🧪 开始运行测试...")
    print(f"📝 命令: {' '.join(cmd)}")
    print("=" * 60)
    
    # 运行测试
    success = run_command(cmd)
    
    print("=" * 60)
    if success:
        print("✅ 测试运行完成")
        if args.coverage:
            print("📊 覆盖率报告已生成: htmlcov/index.html")
    else:
        print("❌ 测试运行失败")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)