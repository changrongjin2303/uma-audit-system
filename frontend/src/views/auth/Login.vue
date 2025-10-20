<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-overlay"></div>
    </div>
    
    <div class="login-form-container">
      <div class="login-form-wrapper">
        <!-- Logo和标题 -->
        <div class="login-header">
          <div class="login-logo">
            <img src="/logo.png" alt="Logo" class="logo-image">
          </div>
          <h2 class="login-title">材料价格AI分析系统</h2>
          <p class="login-subtitle">基于AI的智能识别平台</p>
        </div>

        <!-- 登录表单 -->
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          auto-complete="on"
          label-position="left"
        >
          <el-form-item prop="username">
            <el-input
              ref="usernameRef"
              v-model="loginForm.username"
              placeholder="请输入用户名"
              name="username"
              type="text"
              tabindex="1"
              auto-complete="on"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              ref="passwordRef"
              v-model="loginForm.password"
              :type="passwordType"
              placeholder="请输入密码"
              name="password"
              tabindex="2"
              auto-complete="on"
              size="large"
              prefix-icon="Lock"
              @keyup.enter="handleLogin"
            >
              <template #suffix>
                <el-icon class="password-icon" @click="showPassword">
                  <component :is="passwordType === 'password' ? 'View' : 'Hide'" />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <!-- 记住密码和忘记密码 -->
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">
              记住密码
            </el-checkbox>
            <router-link to="/forgot-password" class="forgot-password">
              忘记密码？
            </router-link>
          </div>

          <!-- 登录按钮 -->
          <el-button
            :loading="loading"
            type="primary"
            size="large"
            style="width: 100%; margin-bottom: 30px;"
            @click.prevent="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>

          <!-- 其他操作 -->
          <div class="login-footer">
            <span class="login-tip">还没有账号？</span>
            <router-link to="/register" class="register-link">
              立即注册
            </router-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { validUsername } from '@/utils/validate'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loginFormRef = ref()
const usernameRef = ref()
const passwordRef = ref()
const passwordType = ref('password')
const loading = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  remember: true
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ]
}

// 方法
const showPassword = () => {
  passwordType.value = passwordType.value === 'password' ? '' : 'password'
  nextTick(() => {
    passwordRef.value.focus()
  })
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        await userStore.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        ElMessage.success('登录成功')
        
        // 登录成功后跳转
        const redirect = route.query.redirect || '/dashboard'
        router.push(redirect)
        
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

// 页面加载时聚焦到用户名输入框
onMounted(() => {
  if (loginForm.username === '') {
    usernameRef.value.focus()
  } else if (loginForm.password === '') {
    passwordRef.value.focus()
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  position: fixed;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/login-bg.jpg') center center/cover no-repeat;
  
  .login-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
  }
}

.login-form-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 0 20px;
}

.login-form-wrapper {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 40px 30px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .login-logo {
    margin-bottom: 20px;
    
    .logo-image {
      width: 64px;
      height: 64px;
      border-radius: 12px;
    }
  }

  .login-title {
    font-size: 24px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 8px;
  }

  .login-subtitle {
    font-size: 14px;
    color: $text-secondary;
    margin-bottom: 0;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
    
    :deep(.el-input__wrapper) {
      padding: 12px 15px;
      border-radius: 8px;
    }
    
    :deep(.el-input__inner) {
      font-size: 14px;
    }
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .forgot-password {
    color: $primary-color;
    text-decoration: none;
    font-size: 13px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.password-icon {
  cursor: pointer;
  color: $text-placeholder;
  
  &:hover {
    color: $text-secondary;
  }
}

.login-footer {
  text-align: center;
  
  .login-tip {
    font-size: 13px;
    color: $text-secondary;
    margin-right: 8px;
  }
  
  .register-link {
    color: $primary-color;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

// 响应式设计
@media (max-width: $breakpoint-sm) {
  .login-form-wrapper {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .login-header {
    .login-title {
      font-size: 20px;
    }
    
    .login-subtitle {
      font-size: 13px;
    }
  }
}

// 深色主题适配
.dark {
  .login-form-wrapper {
    background: rgba(30, 30, 30, 0.95);
    color: #fff;
    
    .login-title {
      color: #fff;
    }
  }
}

// 动画效果
.login-form-wrapper {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
