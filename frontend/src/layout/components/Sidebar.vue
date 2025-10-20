<template>
  <div class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <router-link to="/home/dashboard" class="sidebar-logo-link">
        <h1 v-show="!isCollapsed" class="sidebar-logo-title">
          材料价格AI分析系统
        </h1>
      </router-link>
      <button class="sidebar-toggle" @click="toggleSidebar" type="button" aria-label="切换侧边栏">
        <el-icon>
          <Expand v-if="isCollapsed" />
          <Fold v-else />
        </el-icon>
      </button>
    </div>
    
    <!-- 菜单 -->
    <el-scrollbar class="sidebar-menu-scrollbar">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :unique-opened="true"
        :collapse-transition="false"
        mode="vertical"
        :background-color="menuColors.backgroundColor"
        :text-color="menuColors.textColor"
        :active-text-color="menuColors.activeTextColor"
      >
        <sidebar-item
          v-for="route in menuRoutes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'
import { useUserStore } from '@/store/user'
import SidebarItem from './SidebarItem.vue'
import { Fold, Expand } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 动态计算菜单颜色
const menuColors = computed(() => {
  if (appStore.theme === 'dark') {
    return {
      backgroundColor: '#2d2d2d',
      textColor: '#e4e7ed',
      activeTextColor: '#ffffff'
    }
  }
  return {
    backgroundColor: '#ffffff',
    textColor: '#303133',
    activeTextColor: '#409EFF'
  }
})

// 计算属性
const isCollapsed = computed(() => !appStore.sidebar.opened)
const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})

// 过滤菜单路由
const menuRoutes = computed(() => {
  return filterRoutes(router.getRoutes())
})

const toggleSidebar = () => {
  appStore.toggleSideBar()
}

// 过滤路由函数
function filterRoutes(routes) {
  const accessedRoutes = []
  
  routes.forEach(route => {
    if (!route.hidden && !route.meta?.hidden) {
      const tmp = { ...route }
      
      // 检查角色权限
      if (hasPermission(route)) {
        if (tmp.children) {
          tmp.children = filterRoutes(tmp.children)
          if (tmp.children.length > 0) {
            accessedRoutes.push(tmp)
          }
        } else {
          accessedRoutes.push(tmp)
        }
      }
    }
  })
  
  return accessedRoutes
}

// 权限检查
function hasPermission(route) {
  if (route.meta && route.meta.roles) {
    return userStore.hasRole(route.meta.roles)
  }
  return true
}
</script>

<style lang="scss" scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  position: relative;
  width: 100%;
  height: 50px;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 15px;
  background-color: #fff;
  border-bottom: 1px solid $border-color-lighter;

  .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    text-decoration: none;
    padding-right: 36px;
  }

  .sidebar-toggle {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: background 0.2s;
    z-index: 2;

    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }

    :deep(.el-icon) {
      font-size: 18px;
      color: $text-secondary;
    }
  }

  .logo-placeholder {
    width: 32px;
    height: 32px;
    margin-right: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .logo-text {
      color: white;
      font-size: 16px;
      font-weight: bold;
    }
  }

  .sidebar-logo-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    white-space: nowrap;
  }
}

.sidebar-menu-scrollbar {
  flex: 1;
  height: 0;

  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
  }
}

// 菜单样式
:deep(.el-menu) {
  border-right: none;

  .el-menu-item {
    height: 50px;
    line-height: 50px;

    &:hover {
      background-color: $primary-light;
    }

    &.is-active {
      background-color: $primary-light;
      border-right: 3px solid $primary-color;
    }
  }

  .el-sub-menu {
    .el-sub-menu__title {
      height: 50px;
      line-height: 50px;

      &:hover {
        background-color: $primary-light;
      }
    }

    .el-menu-item {
      height: 45px;
      line-height: 45px;
      padding-left: 50px;

      &.is-active {
        background-color: $primary-color;
        color: #fff;
        border-right: none;
      }
    }
  }

  // 折叠状态
  &.el-menu--collapse {
    width: $sidebar-width-collapsed;

    .el-sub-menu {
      .el-sub-menu__title {
        span {
          height: 0;
          width: 0;
          overflow: hidden;
          visibility: hidden;
          display: inline-block;
        }
      }
    }
  }
}

// 移动端适配
@media (max-width: $breakpoint-md) {
  .sidebar-logo {
    padding: 0 10px;
    
    .sidebar-logo-title {
      font-size: 14px;
    }
  }
}

// 深色主题样式
.dark .sidebar {
  .sidebar-logo {
    background-color: #2d2d2d;
    border-bottom-color: #4c4d4f;
    
    .sidebar-logo-title {
      color: #e4e7ed;
    }
    
    .logo-placeholder {
      background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
    }
  }
}

.dark :deep(.el-menu) {
  background-color: #2d2d2d !important;
  
  .el-menu-item {
    background-color: #2d2d2d !important;
    color: #e4e7ed !important;
    
    &:hover {
      background-color: #363637 !important;
    }
    
    &.is-active {
      background-color: #409EFF !important;
      color: #fff !important;
    }
  }
  
  .el-sub-menu {
    .el-sub-menu__title {
      background-color: #2d2d2d !important;
      color: #e4e7ed !important;
      
      &:hover {
        background-color: #363637 !important;
      }
    }
    
    .el-menu-item {
      background-color: #2d2d2d !important;
      color: #e4e7ed !important;
      
      &.is-active {
        background-color: #409EFF !important;
        color: #fff !important;
      }
    }
  }
}
</style>
