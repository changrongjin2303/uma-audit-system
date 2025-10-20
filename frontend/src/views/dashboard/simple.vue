<template>
  <div class="simple-dashboard">
    <h1>🎉 登录成功！</h1>
    <p>欢迎使用材料价格AI分析系统</p>
    <div class="user-info">
      <h2>当前用户信息：</h2>
      <p>用户名：{{ userStore.userInfo.username }}</p>
      <p>邮箱：{{ userStore.userInfo.email }}</p>
      <p>角色：{{ userStore.userInfo.role }}</p>
    </div>
    
    <div class="quick-actions">
      <h2>快速操作：</h2>
      <router-link to="/charts" class="action-button">
        📊 查看操作流程
      </router-link>
      <router-link to="/mobile" class="action-button">
        📱 移动端演示
      </router-link>
      <router-link to="/test" class="action-button">
        🧪 系统测试
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
</script>

<style scoped>
.simple-dashboard {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.simple-dashboard h1 {
  color: #409eff;
  font-size: 36px;
  margin-bottom: 20px;
}

.simple-dashboard p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
}

.user-info {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin: 30px 0;
  text-align: left;
}

.user-info h2 {
  margin-top: 0;
  color: #333;
}

.user-info p {
  margin: 10px 0;
  font-size: 16px;
}

.quick-actions {
  margin-top: 40px;
}

.quick-actions h2 {
  margin-bottom: 20px;
  color: #333;
}

.action-button {
  display: inline-block;
  margin: 10px;
  padding: 15px 30px;
  background: #409eff;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s;
}

.action-button:hover {
  background: #66b1ff;
  transform: translateY(-2px);
}
</style>
