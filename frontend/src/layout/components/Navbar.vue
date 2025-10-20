<template>
  <div class="navbar">
    <!-- 左侧 -->
    <div class="navbar-left">
      <!-- 面包屑导航 -->
      <breadcrumb class="breadcrumb-container" />
    </div>

    <!-- 右侧 -->
    <div class="navbar-right">
      <!-- 全屏按钮 -->
      <div class="right-menu-item hover-effect" @click="toggleFullscreen">
        <el-icon>
          <FullScreen v-if="!isFullscreen" />
          <Aim v-else />
        </el-icon>
      </div>

      <!-- 通知消息 -->
      <div class="right-menu-item hover-effect">
        <el-badge :value="12" :max="99" class="item">
          <el-icon>
            <Bell />
          </el-icon>
        </el-badge>
      </div>

      <!-- 主题切换 -->
      <div class="right-menu-item hover-effect" @click="toggleTheme">
        <el-icon>
          <Sunny v-if="theme === 'light'" />
          <Moon v-else />
        </el-icon>
      </div>

      <!-- 用户头像和下拉菜单 -->
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <el-avatar :size="35" :src="userStore.userInfo.avatar">
            {{ userStore.displayName.charAt(0) }}
          </el-avatar>
          <span class="user-name">{{ userStore.displayName }}</span>
          <el-icon class="el-icon-caret-bottom">
            <CaretBottom />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <router-link to="/profile">
              <el-dropdown-item>
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
            </router-link>
            <router-link to="/profile/settings">
              <el-dropdown-item>
                <el-icon><Setting /></el-icon>
                账户设置
              </el-dropdown-item>
            </router-link>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAppStore } from '@/store/app'
import { useUserStore } from '@/store/user'
import Breadcrumb from './Breadcrumb.vue'

const appStore = useAppStore()
const userStore = useUserStore()

const isFullscreen = ref(false)

// 计算属性
const theme = computed(() => appStore.theme)

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
      isFullscreen.value = false
    }
  }
}

const toggleTheme = () => {
  const newTheme = theme.value === 'light' ? 'dark' : 'light'
  appStore.setTheme(newTheme)
  ElMessage.success(`已切换到${newTheme === 'light' ? '浅色' : '深色'}主题`)
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await userStore.logout()
    ElMessage.success('已退出登录')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出登录失败:', error)
    }
  }
}

// 监听全屏状态变化
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})
</script>

<style lang="scss" scoped>
.navbar {
  height: $navbar-height;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  position: relative;
  z-index: 1000;

  .navbar-left {
    display: flex;
    align-items: center;
    flex: 1;
  }

  .navbar-right {
    display: flex;
    align-items: center;
    height: 100%;

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;

      &.hover-effect {
        cursor: pointer;
        transition: background 0.3s;

        &:hover {
          background: rgba(0, 0, 0, 0.025);
        }
      }
    }
  }
}

.breadcrumb-container {
  margin-left: 16px;
}

.avatar-container {
  margin-right: 10px;

  .avatar-wrapper {
    margin-top: 5px;
    position: relative;
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    transition: background-color 0.3s;

    &:hover {
      background-color: rgba(0, 0, 0, 0.025);
    }

    .user-name {
      margin: 0 8px 0 10px;
      font-size: 14px;
      color: $text-primary;
      font-weight: 500;
    }

    .el-icon-caret-bottom {
      cursor: pointer;
      position: absolute;
      right: -20px;
      top: 25px;
      font-size: 12px;
      color: $text-secondary;
    }
  }
}

// 移动端适配
@media (max-width: $breakpoint-md) {
  .navbar {
    padding: 0 10px;

    .navbar-right {
      .right-menu-item {
        padding: 0 6px;
        font-size: 16px;
      }
    }

    .avatar-container .avatar-wrapper {
      .user-name {
        display: none;
      }
    }
  }

  .hamburger-container {
    padding: 0 8px;
  }
}

// 深色主题
.dark {
  .navbar {
    background: #1d1e1f;
    border-bottom: 1px solid #363637;

    .hamburger .hamburger,
    .right-menu-item {
      color: #fff;
    }

    .avatar-wrapper .user-name {
      color: #fff;
    }
  }
}
</style>
