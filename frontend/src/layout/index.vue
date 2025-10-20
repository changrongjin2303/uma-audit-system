<template>
  <div class="app-wrapper" :class="{ 'mobile': isMobile, 'hideSidebar': !opened }">
    <div
      v-if="isMobile && opened"
      class="drawer-bg"
      @click="handleClickOutside"
    />
    
    <!-- 侧边栏 -->
    <sidebar class="sidebar-container" />
    
    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <navbar />
      
      <!-- 标签页导航 -->
      <tags-view v-if="needTagsView" />
      
      <!-- 页面内容 -->
      <app-main />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import AppMain from './components/AppMain.vue'
import TagsView from './components/TagsView.vue'

const route = useRoute()
const appStore = useAppStore()

const opened = computed(() => appStore.sidebar.opened)
const isMobile = computed(() => appStore.device === 'mobile')
const needTagsView = computed(() => appStore.tagsView)

// 处理移动端侧边栏点击外部关闭
const handleClickOutside = () => {
  appStore.closeSideBar({ withoutAnimation: false })
}

// 监听窗口大小变化
const handleResize = () => {
  const rect = document.body.getBoundingClientRect()
  const isMobile = rect.width < 992
  appStore.toggleDevice(isMobile ? 'mobile' : 'desktop')
  
  if (isMobile) {
    appStore.closeSideBar({ withoutAnimation: true })
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;

  &.mobile {
    .main-container {
      margin-left: 0;
    }
  }
}

.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

.main-container {
  min-height: 100%;
  transition: margin-left 0.28s;
  margin-left: $sidebar-width;
  position: relative;

}

.sidebar-container {
  transition: width 0.28s;
  width: $sidebar-width;
  background-color: $bg-color;
  height: 100%;
  position: fixed;
  font-size: 0;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  overflow: hidden;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);

  .horizontal-collapse-transition {
    transition: 0s width ease-in-out, 0s padding-left ease-in-out, 0s padding-right ease-in-out;
  }

  .scrollbar-wrapper {
    overflow-x: hidden !important;
  }

  .el-scrollbar__bar.is-vertical {
    right: 0;
  }

  .el-scrollbar {
    height: 100%;
  }

  &.has-logo {
    .el-scrollbar {
      height: calc(100% - 50px);
    }
  }

  .is-horizontal {
    display: none;
  }

  a {
    display: inline-block;
    width: 100%;
    overflow: hidden;
  }

  .svg-icon {
    margin-right: 16px;
  }

  .sub-el-icon {
    margin-right: 12px;
    margin-left: -2px;
  }

  .el-menu {
    border: none;
    height: 100%;
    width: 100% !important;
  }
}

// 侧边栏折叠状态
.app-wrapper.hideSidebar {
  .main-container {
    margin-left: $sidebar-width-collapsed;
  }
  
  .sidebar-container {
    width: $sidebar-width-collapsed !important;
  }
}

// 移动端适配
@media (max-width: $breakpoint-md) {
  .app-wrapper.mobile {
    .main-container {
      margin-left: 0;
    }
    
    .sidebar-container {
      transition: transform 0.28s;
      width: $sidebar-width !important;
    }
    
    &.openSidebar {
      position: fixed;
      top: 0;
    }
    
    &.hideSidebar {
      .sidebar-container {
        pointer-events: none;
        transition-duration: 0.3s;
        transform: translate3d(-$sidebar-width, 0, 0);
      }
    }
  }
}

// 深色主题样式
.dark {
  .sidebar-container {
    background-color: #2d2d2d !important;
    box-shadow: 2px 0 6px rgba(0, 0, 0, 0.3);
  }
}
</style>