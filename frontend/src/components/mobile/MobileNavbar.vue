<template>
  <div class="mobile-navbar" :class="{ 'is-fixed': fixed }">
    <!-- 顶部导航栏 -->
    <div class="navbar-header" :style="{ background: backgroundColor }">
      <!-- 左侧按钮 -->
      <div class="navbar-left">
        <slot name="left">
          <el-button
            v-if="showBack"
            text
            :icon="ArrowLeft"
            @click="handleBack"
            class="back-button"
          />
          <el-button
            v-else-if="showMenu"
            text
            :icon="Operation"
            @click="toggleSidebar"
            class="menu-button"
          />
        </slot>
      </div>

      <!-- 中间标题 -->
      <div class="navbar-center">
        <slot name="title">
          <h1 class="navbar-title">{{ title }}</h1>
        </slot>
      </div>

      <!-- 右侧按钮 -->
      <div class="navbar-right">
        <slot name="right">
          <el-button
            v-if="showSearch"
            text
            :icon="Search"
            @click="handleSearch"
            class="action-button"
          />
          <el-button
            v-if="showMore"
            text
            :icon="More"
            @click="handleMore"
            class="action-button"
          />
        </slot>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div v-if="searchVisible" class="navbar-search">
      <el-input
        ref="searchInputRef"
        v-model="searchValue"
        placeholder="搜索..."
        clearable
        prefix-icon="Search"
        @blur="handleSearchBlur"
        @keyup.enter="handleSearchEnter"
        class="search-input"
      />
      <el-button
        text
        @click="hideSearch"
        class="search-cancel"
      >
        取消
      </el-button>
    </div>

    <!-- 选项卡栏 -->
    <div v-if="tabs.length > 0" class="navbar-tabs">
      <div class="tabs-container">
        <div
          v-for="(tab, index) in tabs"
          :key="tab.name || index"
          class="tab-item"
          :class="{ active: activeTab === tab.name }"
          @click="handleTabClick(tab, index)"
        >
          <el-icon v-if="tab.icon"><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
          <el-badge
            v-if="tab.badge"
            :value="tab.badge"
            :hidden="tab.badge === 0"
            class="tab-badge"
          />
        </div>
      </div>
      <div
        class="tab-indicator"
        :style="indicatorStyle"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Operation, Search, More } from '@element-plus/icons-vue'

export default {
  name: 'MobileNavbar',
  components: {
    ArrowLeft,
    Operation,
    Search,
    More
  },
  props: {
    // 标题
    title: {
      type: String,
      default: ''
    },
    // 背景颜色
    backgroundColor: {
      type: String,
      default: '#409EFF'
    },
    // 文字颜色
    textColor: {
      type: String,
      default: '#ffffff'
    },
    // 是否固定
    fixed: {
      type: Boolean,
      default: true
    },
    // 是否显示返回按钮
    showBack: {
      type: Boolean,
      default: false
    },
    // 是否显示菜单按钮
    showMenu: {
      type: Boolean,
      default: false
    },
    // 是否显示搜索按钮
    showSearch: {
      type: Boolean,
      default: false
    },
    // 是否显示更多按钮
    showMore: {
      type: Boolean,
      default: false
    },
    // 选项卡配置
    tabs: {
      type: Array,
      default: () => []
    },
    // 当前活跃的选项卡
    activeTab: {
      type: String,
      default: ''
    },
    // 安全区域适配
    safeArea: {
      type: Boolean,
      default: true
    }
  },
  emits: [
    'back',
    'menu-toggle', 
    'search',
    'more',
    'tab-change',
    'search-change',
    'search-enter'
  ],
  setup(props, { emit }) {
    const router = useRouter()
    
    const searchInputRef = ref(null)
    const searchVisible = ref(false)
    const searchValue = ref('')
    const sidebarVisible = ref(false)

    // 计算属性
    const indicatorStyle = computed(() => {
      if (props.tabs.length === 0) return {}
      
      const activeIndex = props.tabs.findIndex(tab => tab.name === props.activeTab)
      if (activeIndex === -1) return {}
      
      const itemWidth = 100 / props.tabs.length
      const translateX = activeIndex * itemWidth
      
      return {
        width: `${itemWidth}%`,
        transform: `translateX(${translateX}%)`
      }
    })

    // 事件处理
    const handleBack = () => {
      emit('back')
      // 默认路由返回
      if (router.currentRoute.value.query.from) {
        router.push(router.currentRoute.value.query.from)
      } else {
        router.back()
      }
    }

    const toggleSidebar = () => {
      sidebarVisible.value = !sidebarVisible.value
      emit('menu-toggle', sidebarVisible.value)
    }

    const handleSearch = () => {
      if (searchVisible.value) {
        hideSearch()
      } else {
        showSearch()
      }
    }

    const showSearch = async () => {
      searchVisible.value = true
      await nextTick()
      if (searchInputRef.value) {
        searchInputRef.value.focus()
      }
    }

    const hideSearch = () => {
      searchVisible.value = false
      searchValue.value = ''
      emit('search-change', '')
    }

    const handleSearchBlur = () => {
      // 延迟隐藏，避免点击取消按钮时冲突
      setTimeout(() => {
        if (!searchValue.value) {
          hideSearch()
        }
      }, 200)
    }

    const handleSearchEnter = () => {
      emit('search-enter', searchValue.value)
    }

    const handleMore = () => {
      emit('more')
    }

    const handleTabClick = (tab, index) => {
      emit('tab-change', { tab, index, name: tab.name })
    }

    // 监听搜索值变化
    watch(searchValue, (newValue) => {
      emit('search-change', newValue)
    })

    // 生命周期
    onMounted(() => {
      // 设置CSS变量
      if (props.safeArea) {
        document.documentElement.style.setProperty('--safe-area-top', 'env(safe-area-inset-top)')
      }
    })

    return {
      searchInputRef,
      searchVisible,
      searchValue,
      sidebarVisible,
      indicatorStyle,
      handleBack,
      toggleSidebar,
      handleSearch,
      showSearch,
      hideSearch,
      handleSearchBlur,
      handleSearchEnter,
      handleMore,
      handleTabClick
    }
  }
}
</script>

<style scoped>
.mobile-navbar {
  width: 100%;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.mobile-navbar.is-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
}

/* 导航栏头部 */
.navbar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  padding-top: var(--safe-area-top, 0);
  background: #409EFF;
  color: white;
}

.navbar-left,
.navbar-right {
  display: flex;
  align-items: center;
  min-width: 60px;
}

.navbar-left {
  justify-content: flex-start;
}

.navbar-right {
  justify-content: flex-end;
}

.navbar-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.navbar-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: inherit;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.back-button,
.menu-button,
.action-button {
  padding: 8px;
  color: inherit;
  font-size: 20px;
  min-width: 44px;
  height: 44px;
}

.back-button:hover,
.menu-button:hover,
.action-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 搜索栏 */
.navbar-search {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__inner) {
  border-radius: 20px;
  background: white;
  height: 36px;
  line-height: 36px;
}

.search-cancel {
  color: #409EFF;
  padding: 8px 12px;
  font-size: 14px;
}

/* 选项卡栏 */
.navbar-tabs {
  position: relative;
  background: white;
  border-bottom: 1px solid #ebeef5;
}

.tabs-container {
  display: flex;
  height: 48px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: color 0.3s ease;
  position: relative;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.tab-item.active {
  color: #409EFF;
  font-weight: 500;
}

.tab-item:active {
  background: rgba(64, 158, 255, 0.1);
}

.tab-item .el-icon {
  font-size: 16px;
}

.tab-badge {
  position: absolute;
  top: 8px;
  right: 20%;
  transform: translateX(50%);
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  height: 2px;
  background: #409EFF;
  transition: all 0.3s ease;
  border-radius: 1px;
}

/* 安全区域适配 */
@supports (padding-top: env(safe-area-inset-top)) {
  .navbar-header {
    padding-top: calc(env(safe-area-inset-top) + 0px);
  }
}

/* 响应式优化 */
@media (max-width: 375px) {
  .navbar-header {
    height: 52px;
    padding: 0 12px;
  }

  .navbar-title {
    font-size: 16px;
    max-width: 150px;
  }

  .back-button,
  .menu-button,
  .action-button {
    min-width: 40px;
    height: 40px;
    font-size: 18px;
  }

  .tabs-container {
    height: 44px;
  }

  .tab-item {
    font-size: 13px;
  }

  .tab-item .el-icon {
    font-size: 14px;
  }
}

@media (orientation: landscape) and (max-height: 500px) {
  .navbar-header {
    height: 48px;
  }
  
  .tabs-container {
    height: 40px;
  }
  
  .navbar-title {
    font-size: 16px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .navbar-search {
    background: #2d3748;
    border-bottom-color: #4a5568;
  }

  .search-input :deep(.el-input__inner) {
    background: #1a202c;
    border-color: #4a5568;
    color: white;
  }

  .navbar-tabs {
    background: #2d3748;
    border-bottom-color: #4a5568;
  }

  .tab-item {
    color: #a0aec0;
  }

  .tab-item.active {
    color: #63b3ed;
  }

  .tab-indicator {
    background: #63b3ed;
  }
}
</style>