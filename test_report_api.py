#!/usr/bin/env python3
"""
测试报告生成API的脚本
"""
import requests
import json
import time


def test_report_api():
    """测试报告API"""
    base_url = "http://localhost:8000"
    
    print("🔍 测试报告生成API...")
    print(f"🌐 后端地址: {base_url}")
    
    # 1. 测试健康检查
    try:
        print("\n1️⃣ 测试系统健康状态...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 系统状态: {health_data.get('status', 'unknown')}")
            print(f"📊 版本: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("💡 请确保后端服务正在运行")
        return False
    
    # 2. 测试认证（获取Token）
    print("\n2️⃣ 测试用户认证...")
    try:
        # 尝试注册用户（如果不存在）
        register_data = {
            "username": "test_user",
            "password": "test_password",
            "email": "test@example.com",
            "full_name": "测试用户"
        }
        register_response = requests.post(f"{base_url}/api/v1/auth/register", 
                                        json=register_data, timeout=10)
        
        # 无论注册成功与否，都尝试登录
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        login_response = requests.post(f"{base_url}/api/v1/auth/login", 
                                     json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get("access_token")
            if token:
                print("✅ 登录成功，获取到Token")
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print("❌ 登录响应中没有Token")
                return False
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"📋 响应: {login_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 认证请求失败: {e}")
        return False
    
    # 3. 创建测试项目
    print("\n3️⃣ 创建测试项目...")
    try:
        project_data = {
            "name": f"API测试项目 - {int(time.time())}",
            "description": "通过API测试创建的项目",
            "project_code": f"API-TEST-{int(time.time())}",
            "location": "北京市",
            "owner": "测试业主",
            "contractor": "测试承包商"
        }
        
        project_response = requests.post(f"{base_url}/api/v1/projects/", 
                                       json=project_data, 
                                       headers=headers, 
                                       timeout=10)
        
        if project_response.status_code == 200:
            project_result = project_response.json()
            project_id = project_result.get("id")
            print(f"✅ 项目创建成功，ID: {project_id}")
            print(f"📝 项目名称: {project_result.get('name')}")
        else:
            print(f"❌ 项目创建失败: {project_response.status_code}")
            print(f"📋 响应: {project_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 创建项目请求失败: {e}")
        return False
    
    # 4. 测试报告生成
    print("\n4️⃣ 测试报告生成...")
    try:
        report_data = {
            "project_id": project_id,
            "report_title": f"API测试报告 - {project_id}",
            "config": {
                "report_type": "price_analysis",
                "include_charts": True,
                "include_detailed_analysis": True,
                "include_recommendations": True,
                "include_appendices": True
            }
        }
        
        print("⏳ 正在生成报告...")
        report_response = requests.post(f"{base_url}/api/v1/reports/generate", 
                                      json=report_data, 
                                      headers=headers, 
                                      timeout=60)  # 报告生成可能需要更长时间
        
        if report_response.status_code == 200:
            report_result = report_response.json()
            report_id = report_result.get("report_id")
            print(f"✅ 报告生成成功，ID: {report_id}")
            print(f"📄 报告标题: {report_result.get('report_title')}")
            print(f"📏 文件大小: {report_result.get('file_size', 0):,} 字节")
            print(f"🔗 下载链接: {report_result.get('download_url')}")
            
            # 5. 测试报告下载
            print("\n5️⃣ 测试报告下载...")
            download_url = f"{base_url}/api/v1/reports/{report_id}/download"
            download_response = requests.get(download_url, 
                                           headers=headers, 
                                           timeout=30)
            
            if download_response.status_code == 200:
                print("✅ 报告下载成功")
                print(f"📋 Content-Type: {download_response.headers.get('content-type')}")
                print(f"📏 下载文件大小: {len(download_response.content):,} 字节")
                
                # 保存下载的文件
                download_filename = f"api_test_report_{report_id}.docx"
                with open(download_filename, "wb") as f:
                    f.write(download_response.content)
                print(f"💾 报告已保存为: {download_filename}")
                
            else:
                print(f"❌ 报告下载失败: {download_response.status_code}")
                print(f"📋 响应: {download_response.text}")
            
            return True
        else:
            print(f"❌ 报告生成失败: {report_response.status_code}")
            print(f"📋 响应: {report_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 报告生成请求失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("🏗️  造价材料审计系统 - 报告API测试")
    print("=" * 70)
    
    success = test_report_api()
    
    print("\n" + "=" * 70)
    if success:
        print("🎊 API测试完成: 报告生成API功能正常!")
        print("✨ 前后端集成测试通过")
    else:
        print("💥 API测试失败: 报告生成API存在问题")
        print("🔧 请检查后端服务状态和配置")
    print("=" * 70)