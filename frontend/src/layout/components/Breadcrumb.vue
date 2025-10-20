<template>
  <el-breadcrumb class="app-breadcrumb" separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item 
        v-for="(item, index) in breadcrumbList"
        :key="item.path"
      >
        <span
          v-if="item.redirect === 'noRedirect' || index === breadcrumbList.length - 1"
          class="no-redirect"
        >
          {{ item.meta.title }}
        </span>
        <router-link
          v-else
          :to="item.path"
        >
          {{ item.meta.title }}
        </router-link>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const breadcrumbList = ref([])

const getBreadcrumb = () => {
  // 过滤出有效的路由
  let matched = route.matched.filter(item => item.meta && item.meta.title)
  
  const first = matched[0]
  
  // 如果第一个路由不是首页，添加首页
  if (!isDashboard(first)) {
    matched = [{ path: '/dashboard', meta: { title: '首页' } }].concat(matched)
  }
  
  breadcrumbList.value = matched.filter((item) => {
    return item.meta && item.meta.title && item.meta.breadcrumb !== false
  })
}

const isDashboard = (route) => {
  const name = route && route.name
  if (!name) {
    return false
  }
  return name.trim().toLocaleLowerCase() === 'Dashboard'.toLocaleLowerCase()
}

// 监听路由变化
watch(route, getBreadcrumb, { immediate: true })
</script>

<style lang="scss" scoped>
.app-breadcrumb.el-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: $navbar-height;
  margin-left: 8px;

  .no-redirect {
    color: $text-secondary;
    cursor: text;
  }

  a {
    color: $text-regular;
    text-decoration: none;

    &:hover {
      color: $primary-color;
    }
  }
}

.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.3s;
}

.breadcrumb-enter-from,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-leave-active {
  position: absolute;
}

// 深色主题样式
.dark .app-breadcrumb.el-breadcrumb {
  .no-redirect {
    color: #909399;
  }

  a {
    color: #c0c4cc;

    &:hover {
      color: #409EFF;
    }
  }
}
</style>