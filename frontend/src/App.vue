<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useAppStore } from '@/store/app'

const userStore = useUserStore()
const appStore = useAppStore()

onMounted(async () => {
  // 初始化主题 - 立即应用以避免闪烁
  const savedTheme = localStorage.getItem('theme') || 'light'
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
    document.documentElement.classList.add('el-dark')
    document.body.setAttribute('data-theme', 'dark')
  }
  appStore.setTheme(savedTheme)
  
  // 应用启动时检查用户登录状态
  if (!userStore.token) {
    // 如果没有token，自动进行测试登录
    try {
      await userStore.login({ username: 'admin', password: 'password' })
      console.log('自动登录成功')
    } catch (error) {
      console.log('自动登录失败:', error)
    }
  } else {
    await userStore.checkLoginStatus()
  }
})
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>