<template>
  <div class="error-page">
    <div class="error-container">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-message">抱歉，您访问的页面不存在。</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.error-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-container {
  text-align: center;
}

.error-code {
  font-size: 120px;
  color: #409EFF;
  margin: 0;
}

.error-title {
  font-size: 24px;
  color: #303133;
  margin: 20px 0;
}

.error-message {
  color: #606266;
  margin-bottom: 30px;
}
</style>