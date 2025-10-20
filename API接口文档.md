# 造价材料审计系统 - API接口文档

## 📋 目录

1. [接口概述](#接口概述)
2. [认证鉴权](#认证鉴权)
3. [通用响应格式](#通用响应格式)
4. [错误处理](#错误处理)
5. [接口限制](#接口限制)
6. [API接口详情](#api接口详情)

---

## 🔗 接口概述

### 基础信息

- **基础URL**: `https://your-domain.com/api/v1`
- **协议**: HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API版本**: v1.0

### 技术特性

- ✅ RESTful API设计
- ✅ JWT令牌认证
- ✅ 请求频率限制
- ✅ 统一错误处理
- ✅ 自动API文档（Swagger）
- ✅ 跨域请求支持

---

## 🔐 认证鉴权

### 获取访问令牌

**接口**: `POST /auth/login`

**请求参数**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 使用访问令牌

在请求头中添加授权信息：

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 令牌刷新

令牌有效期为30分钟，过期前需要重新登录获取新令牌。

---

## 📄 通用响应格式

### 成功响应

```json
{
  "data": {
    // 具体数据内容
  },
  "message": "操作成功",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 分页响应

```json
{
  "items": [
    // 数据项列表
  ],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

---

## ❌ 错误处理

### 错误响应格式

```json
{
  "error": "ERROR_CODE",
  "message": "错误描述",
  "details": {
    // 详细错误信息
  },
  "request_id": "uuid-string"
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 描述 |
|-----------|-------|------|
| 400 | BAD_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未授权访问 |
| 403 | FORBIDDEN | 访问被拒绝 |
| 404 | NOT_FOUND | 资源不存在 |
| 422 | VALIDATION_ERROR | 数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |

---

## 🚀 接口限制

### 请求频率限制

- **默认限制**: 每分钟100次请求
- **突发限制**: 连续20次请求
- **超限响应**: HTTP 429 状态码

### 文件上传限制

- **单文件大小**: 最大50MB
- **支持格式**: xlsx, xls, csv, pdf, doc, docx
- **总上传大小**: 每次请求最大200MB

---

## 📚 API接口详情

## 1. 用户认证接口

### 1.1 用户注册

**POST** `/auth/register`

创建新用户账户。

**请求参数**:
```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "张三",
  "role": "造价工程师"
}
```

**响应示例**:
```json
{
  "id": 1,
  "username": "test_user",
  "email": "test@example.com",
  "full_name": "张三",
  "role": "造价工程师",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 1.2 用户登录

**POST** `/auth/login`

用户登录获取访问令牌。

**请求参数** (form-data):
```
username: test_user
password: password123
```

**响应示例**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "test_user",
    "email": "test@example.com",
    "role": "造价工程师"
  }
}
```

### 1.3 获取当前用户信息

**GET** `/auth/me`

获取当前登录用户的详细信息。

**响应示例**:
```json
{
  "id": 1,
  "username": "test_user",
  "email": "test@example.com",
  "full_name": "张三",
  "role": "造价工程师",
  "created_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### 1.4 修改密码

**POST** `/auth/change-password`

修改当前用户密码。

**请求参数**:
```json
{
  "old_password": "old_password",
  "new_password": "new_password123"
}
```

## 2. 项目管理接口

### 2.1 创建项目

**POST** `/projects/`

创建新的审计项目。

**请求参数**:
```json
{
  "name": "测试项目",
  "description": "这是一个测试项目",
  "project_code": "TEST001",
  "location": "北京市",
  "budget": 1000000.0,
  "client": "测试客户",
  "contractor": "测试承包商",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**响应示例**:
```json
{
  "id": 1,
  "project_uuid": "uuid-string",
  "name": "测试项目",
  "description": "这是一个测试项目",
  "status": "draft",
  "project_code": "TEST001",
  "location": "北京市",
  "budget": 1000000.0,
  "created_at": "2024-01-01T12:00:00Z",
  "created_by": 1
}
```

### 2.2 获取项目列表

**GET** `/projects/`

获取项目列表，支持分页和搜索。

**查询参数**:
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 20)
- `search`: 搜索关键词
- `status`: 项目状态筛选
- `sort`: 排序字段

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "测试项目",
      "status": "draft",
      "project_code": "TEST001",
      "location": "北京市",
      "budget": 1000000.0,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### 2.3 获取项目详情

**GET** `/projects/{project_id}`

获取指定项目的详细信息。

**响应示例**:
```json
{
  "id": 1,
  "project_uuid": "uuid-string",
  "name": "测试项目",
  "description": "这是一个测试项目",
  "status": "draft",
  "project_code": "TEST001",
  "location": "北京市",
  "budget": 1000000.0,
  "client": "测试客户",
  "contractor": "测试承包商",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "created_by": 1,
  "materials_count": 0,
  "analyzed_count": 0,
  "progress": 0
}
```

### 2.4 上传Excel文件

**POST** `/projects/{project_id}/upload-excel`

上传项目材料清单Excel文件。

**请求参数** (multipart/form-data):
```
file: 文件对象
description: 文件描述 (可选)
```

**响应示例**:
```json
{
  "file_id": "uuid-string",
  "filename": "材料清单.xlsx",
  "size": 102400,
  "upload_time": "2024-01-01T12:00:00Z",
  "analysis_preview": {
    "total_rows": 100,
    "columns": ["材料名称", "规格", "单位", "数量", "单价", "合价"],
    "sample_data": [
      ["水泥", "P.O 42.5", "t", "100", "450", "45000"]
    ]
  }
}
```

### 2.5 导入材料数据

**POST** `/projects/{project_id}/import-materials`

从上传的Excel文件导入材料数据。

**请求参数**:
```json
{
  "file_id": "uuid-string",
  "column_mapping": {
    "name": "材料名称",
    "specification": "规格",
    "unit": "单位",
    "quantity": "数量",
    "unit_price": "单价",
    "total_price": "合价"
  },
  "skip_rows": 1,
  "validate_data": true
}
```

**响应示例**:
```json
{
  "import_id": "uuid-string",
  "status": "completed",
  "total_rows": 100,
  "imported_count": 95,
  "error_count": 5,
  "errors": [
    {
      "row": 10,
      "message": "单价格式不正确",
      "field": "unit_price"
    }
  ]
}
```

## 3. 基准材料管理接口

### 3.1 创建基准材料

**POST** `/base-materials/`

创建新的基准材料。

**请求参数**:
```json
{
  "name": "水泥",
  "specification": "P.O 42.5",
  "unit": "t",
  "category": "建筑材料",
  "subcategory": "胶凝材料",
  "region": "北京",
  "price": 450.0,
  "source": "政府信息价",
  "effective_date": "2024-01-01",
  "remarks": "备注信息"
}
```

### 3.2 批量导入基准材料

**POST** `/base-materials/import`

批量导入基准材料数据。

**请求参数**:
```json
{
  "data_source": "政府信息价",
  "region": "北京",
  "effective_date": "2024-01-01",
  "materials": [
    {
      "name": "水泥",
      "specification": "P.O 42.5",
      "unit": "t",
      "category": "建筑材料",
      "price": 450.0
    }
  ]
}
```

### 3.3 搜索基准材料

**GET** `/base-materials/`

搜索和获取基准材料列表。

**查询参数**:
- `search`: 搜索关键词
- `category`: 材料分类
- `region`: 地区
- `min_price`: 最低价格
- `max_price`: 最高价格
- `source`: 数据来源
- `page`: 页码
- `size`: 每页数量

## 4. 价格分析接口

### 4.1 批量分析项目材料

**POST** `/analysis/{project_id}/analyze`

对项目中的无信息价材料进行批量AI价格分析。

**请求参数**:
```json
{
  "ai_service": "openai",  // 可选: openai, dashscope, baidu
  "analysis_config": {
    "region": "北京",
    "analysis_date": "2024-01-01",
    "include_market_factors": true,
    "confidence_threshold": 0.7
  },
  "material_ids": [1, 2, 3]  // 可选: 指定材料ID，不指定则分析所有无信息价材料
}
```

**响应示例**:
```json
{
  "analysis_id": "uuid-string",
  "status": "started",
  "total_materials": 50,
  "estimated_duration": "10-15分钟",
  "progress_url": "/analysis/{project_id}/progress/{analysis_id}"
}
```

### 4.2 获取分析进度

**GET** `/analysis/{project_id}/progress/{analysis_id}`

获取批量分析的进度信息。

**响应示例**:
```json
{
  "analysis_id": "uuid-string",
  "status": "processing",  // pending, processing, completed, failed
  "progress": 60,  // 进度百分比
  "completed_count": 30,
  "total_count": 50,
  "current_material": "钢筋",
  "estimated_remaining": "5分钟",
  "errors": []
}
```

### 4.3 获取分析结果

**GET** `/analysis/{project_id}/analysis-results`

获取项目的价格分析结果。

**查询参数**:
- `status`: 分析状态筛选
- `confidence_min`: 最低置信度
- `page`: 页码
- `size`: 每页数量

**响应示例**:
```json
{
  "items": [
    {
      "material_id": 1,
      "material_name": "钢筋",
      "specification": "HRB400 φ12",
      "original_price": 4500.0,
      "predicted_price_min": 4200.0,
      "predicted_price_max": 4800.0,
      "predicted_price_avg": 4500.0,
      "confidence_score": 0.85,
      "price_deviation": 0.0,
      "risk_level": "low",
      "data_sources": [
        {
          "name": "钢材网",
          "price": 4500.0,
          "date": "2024-01-01",
          "reliability": 0.9
        }
      ],
      "reasoning": "基于近期市场数据分析，该材料价格合理",
      "recommendations": ["价格合理，建议采用"],
      "analysis_time": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 50,
  "statistics": {
    "analyzed_count": 45,
    "pending_count": 5,
    "success_rate": 90,
    "avg_confidence": 0.82
  }
}
```

### 4.4 分析单个材料

**POST** `/analysis/materials/{material_id}/analyze`

对单个材料进行价格分析。

**请求参数**:
```json
{
  "ai_service": "openai",
  "region": "北京",
  "analysis_date": "2024-01-01"
}
```

## 5. 价格合理性分析接口

### 5.1 项目合理性分析

**POST** `/reasonability/{project_id}/analyze-reasonability`

分析项目材料价格的合理性。

**请求参数**:
```json
{
  "analysis_config": {
    "price_tolerance": 0.15,  // 价格容忍度 15%
    "confidence_threshold": 0.7,
    "include_statistical_analysis": true
  }
}
```

### 5.2 获取不合理材料

**GET** `/reasonability/{project_id}/unreasonable-materials`

获取价格不合理的材料列表。

**查询参数**:
- `risk_level`: 风险等级筛选 (low, medium, high, severe)
- `min_deviation`: 最小价格偏差
- `page`: 页码
- `size`: 每页数量

### 5.3 风险汇总统计

**GET** `/reasonability/{project_id}/risk-summary`

获取项目的价格风险汇总统计。

**响应示例**:
```json
{
  "total_materials": 100,
  "analyzed_materials": 95,
  "risk_distribution": {
    "low": 60,
    "medium": 20,
    "high": 10,
    "severe": 5
  },
  "total_risk_amount": 150000.0,
  "avg_price_deviation": 8.5,
  "recommendation": "建议重点关注高风险和严重风险材料"
}
```

## 6. 报告生成接口

### 6.1 生成审计报告

**POST** `/reports/generate`

生成项目的完整审计报告。

**请求参数**:
```json
{
  "project_id": 1,
  "report_config": {
    "include_charts": true,
    "include_detailed_analysis": true,
    "include_recommendations": true,
    "export_format": "docx"  // docx, pdf
  },
  "custom_settings": {
    "company_name": "XX审计公司",
    "auditor_name": "张三",
    "report_date": "2024-01-01"
  }
}
```

**响应示例**:
```json
{
  "report_id": "uuid-string",
  "status": "generating",
  "estimated_duration": "2-3分钟",
  "download_url": "/reports/{report_id}/download",
  "preview_url": "/reports/{report_id}/preview"
}
```

### 6.2 下载报告

**GET** `/reports/{report_id}/download`

下载生成的审计报告文件。

**响应**: 文件下载流

### 6.3 获取报告列表

**GET** `/reports/`

获取所有生成的报告列表。

**查询参数**:
- `project_id`: 项目ID筛选
- `status`: 报告状态筛选
- `start_date`: 开始日期
- `end_date`: 结束日期
- `page`: 页码
- `size`: 每页数量

### 6.4 批量生成报告

**POST** `/reports/batch-generate`

批量生成多个项目的报告。

**请求参数**:
```json
{
  "project_ids": [1, 2, 3],
  "report_config": {
    "include_charts": true,
    "export_format": "docx"
  },
  "generate_summary": true
}
```

## 7. 系统接口

### 7.1 健康检查

**GET** `/health`

系统健康状态检查，无需认证。

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "uptime_seconds": 86400,
  "total_requests": 10000,
  "error_count": 5,
  "error_rate_percent": 0.05
}
```

### 7.2 系统指标

**GET** `/metrics`

系统性能指标，仅调试模式可用。

### 7.3 AI服务状态

**GET** `/analysis/ai-services/available`

获取可用的AI服务列表及状态。

**响应示例**:
```json
{
  "services": [
    {
      "name": "openai",
      "status": "available",
      "model": "gpt-4",
      "response_time": 1.5,
      "success_rate": 98.5
    },
    {
      "name": "dashscope", 
      "status": "available",
      "model": "qwen-plus",
      "response_time": 2.1,
      "success_rate": 96.8
    }
  ]
}
```

---

## 📝 使用示例

### Python示例

```python
import requests
import json

# 基础配置
BASE_URL = "https://your-domain.com/api/v1"
headers = {"Content-Type": "application/json"}

# 用户登录
login_data = {
    "username": "test_user",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
token = response.json()["access_token"]

# 设置认证头
headers["Authorization"] = f"Bearer {token}"

# 创建项目
project_data = {
    "name": "测试项目",
    "project_code": "TEST001",
    "location": "北京市",
    "budget": 1000000.0
}
response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
project = response.json()

print(f"项目创建成功: {project['id']}")
```

### JavaScript示例

```javascript
// 基础配置
const BASE_URL = "https://your-domain.com/api/v1";

// 用户登录
async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    return data.access_token;
}

// API请求封装
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        },
        ...options
    };
    
    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
    }
    
    return response.json();
}

// 使用示例
async function createProject() {
    try {
        const project = await apiRequest('/projects/', {
            method: 'POST',
            body: JSON.stringify({
                name: '测试项目',
                project_code: 'TEST001',
                location: '北京市',
                budget: 1000000.0
            })
        });
        
        console.log('项目创建成功:', project.id);
        return project;
    } catch (error) {
        console.error('创建项目失败:', error.message);
    }
}
```

---

## 🔍 常见问题

### Q: 如何处理文件上传？

A: 使用multipart/form-data格式上传文件：

```python
files = {'file': open('materials.xlsx', 'rb')}
response = requests.post(
    f"{BASE_URL}/projects/{project_id}/upload-excel",
    files=files,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Q: 如何处理分页数据？

A: 大部分列表接口支持分页，使用page和size参数：

```python
# 获取第2页数据，每页50条
params = {"page": 2, "size": 50}
response = requests.get(f"{BASE_URL}/projects/", params=params, headers=headers)
```

### Q: 如何处理长时间运行的任务？

A: 对于批量分析等长时间任务，先提交任务获取任务ID，然后轮询进度：

```python
# 提交分析任务
response = requests.post(f"{BASE_URL}/analysis/{project_id}/analyze", 
                        json=analysis_config, headers=headers)
analysis_id = response.json()["analysis_id"]

# 轮询进度
while True:
    progress = requests.get(f"{BASE_URL}/analysis/{project_id}/progress/{analysis_id}",
                           headers=headers).json()
    if progress["status"] == "completed":
        break
    time.sleep(5)
```

---

## 📞 技术支持

如需技术支持或API使用帮助，请联系：

- **技术支持邮箱**: api-support@your-company.com
- **开发者社区**: https://developer.your-company.com
- **API状态页**: https://status.your-company.com

---

**更新时间**: 2024-01-01  
**文档版本**: v1.0  
**API版本**: v1.0