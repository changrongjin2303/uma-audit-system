# 生产环境恢复计划

## 🚨 当前开发环境简化项目清单

在调试过程中，我们为了解决开发环境问题做了以下简化，这些在生产环境中都需要恢复：

### 1. 安全性简化

#### 1.1 CORS 配置
**当前状态 (开发环境)**:
```python
# main.py - 允许所有来源
if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ❌ 生产环境安全风险
        allow_credentials=False,
    )
```

**生产环境恢复**:
```python
# 恢复严格的 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # 仅允许指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)
```

#### 1.2 可信主机验证
**当前状态 (开发环境)**:
```python
# main.py - 允许所有主机
if settings.DEBUG:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # ❌ 安全风险
```

**生产环境恢复**:
```python
# 恢复严格的主机验证
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS  # 仅允许配置的主机
)
```

#### 1.3 API 认证
**当前状态 (开发环境)**:
```python
# materials.py - 移除了认证
# current_user: SimpleUser = Depends(get_current_active_user),  # ❌ 被注释掉
```

**生产环境恢复**:
```python
# 恢复 API 认证
@router.get("/")
async def get_base_materials(
    # ... 其他参数
    current_user: SimpleUser = Depends(get_current_active_user),  # ✅ 恢复认证
    db: AsyncSession = Depends(get_db)
):
```

### 2. 网络配置简化

#### 2.1 前端请求地址
**当前状态 (开发环境)**:
```javascript
// request.js - 直接访问 localhost
const service = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // ❌ 硬编码地址
  withCredentials: false
})
```

**生产环境恢复**:
```javascript
// 使用环境变量或代理
const service = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? '/api/v1'  // 生产环境使用相对路径
    : 'http://localhost:8000/api/v1',
  withCredentials: true  // 生产环境携带认证信息
})
```

## 📋 生产环境恢复步骤

### 阶段 1: 恢复安全配置 (1-2小时)

1. **恢复 CORS 严格模式**
   ```bash
   # 1. 编辑 main.py，恢复条件判断
   # 2. 配置 settings.py 中的 CORS_ORIGINS 列表
   # 3. 重启后端服务
   # 4. 测试跨域请求是否正常
   ```

2. **恢复主机验证**
   ```bash
   # 1. 恢复 TrustedHostMiddleware 严格配置
   # 2. 配置 ALLOWED_HOSTS 环境变量
   # 3. 测试不同主机访问情况
   ```

3. **恢复 API 认证**
   ```bash
   # 1. 取消注释 get_current_active_user 依赖
   # 2. 确保前端正确发送 Authorization 头
   # 3. 测试登录后的 API 访问
   ```

### 阶段 2: 恢复网络配置 (30分钟)

1. **恢复前端代理模式**
   ```bash
   # 1. 修改 request.js 使用环境判断
   # 2. 恢复 vite.config.js 代理配置
   # 3. 测试代理是否正常工作
   ```

2. **恢复认证携带**
   ```bash
   # 1. 设置 withCredentials: true
   # 2. 确保 token 正确发送
   # 3. 测试认证流程
   ```

### 阶段 3: 安全性测试 (2小时)

1. **跨域安全测试**
   - 测试未授权域名访问被拒绝
   - 测试恶意跨域请求被阻止

2. **认证安全测试**
   - 测试无 token 访问被拒绝
   - 测试过期 token 处理
   - 测试权限验证

3. **主机安全测试**
   - 测试非法主机头被拒绝
   - 测试Host头攻击防护

## 🛠 自动化恢复脚本

创建恢复脚本 `restore-production.sh`:

```bash
#!/bin/bash
echo "🔄 开始恢复生产环境配置..."

# 1. 恢复后端安全配置
echo "📝 恢复后端 CORS 和认证配置"
# sed 命令批量替换配置...

# 2. 恢复前端网络配置  
echo "🌐 恢复前端网络配置"
# sed 命令修改 baseURL...

# 3. 重启服务
echo "🚀 重启服务"
docker-compose restart backend frontend

# 4. 运行安全测试
echo "🔍 运行安全测试"
./run-security-tests.sh

echo "✅ 生产环境恢复完成！"
```

## ⚠️ 风险评估

### 高风险项
1. **CORS 配置错误** → 可能导致跨域攻击
2. **认证绕过** → 可能导致未授权访问
3. **主机验证失效** → 可能导致 Host 头攻击

### 中风险项  
1. **网络配置错误** → 可能导致服务不可用
2. **Token 处理错误** → 可能导致认证失败

### 缓解措施
1. **分阶段恢复**: 逐步恢复，每步测试
2. **回滚计划**: 准备快速回滚到当前工作状态
3. **监控告警**: 部署后密切监控安全日志
4. **灰度发布**: 小范围测试后再全量发布

## 📅 建议实施时机

**最佳时机**: 功能开发完成后，部署前统一恢复
**紧急情况**: 如需立即部署，可先恢复认证，其他配置后续优化

## ✅ 验收标准

- [ ] 所有 API 需要正确认证
- [ ] CORS 仅允许授权域名
- [ ] 主机验证正常工作
- [ ] 前端代理配置正确
- [ ] 安全测试全部通过
- [ ] 功能测试无回退

---
**更新时间**: 2025-08-31  
**负责人**: Claude AI  
**状态**: 待实施