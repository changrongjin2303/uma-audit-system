<template>
  <section class="app-main">
    <transition name="fade-transform" mode="out-in">
      <router-view v-slot="{ Component, route }">
        <keep-alive :include="cachedViews">
          <component
            :is="Component"
            :key="route.fullPath"
          />
        </keep-alive>
      </router-view>
    </transition>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useTagsViewStore } from '@/store/tagsView'

const tagsViewStore = useTagsViewStore()

// 缓存的视图
const cachedViews = computed(() => tagsViewStore.cachedViews)
</script>

<style lang="scss" scoped>
.app-main {
  /* 50 = navbar  */
  min-height: calc(100vh - #{$navbar-height});
  width: 100%;
  position: relative;
  overflow: hidden;
  background-color: $bg-color-page;
  padding: 0;
}

.fixed-header + .app-main {
  padding-top: $navbar-height;
}

// 路由动画
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

// 深色主题样式
.dark .app-main {
  background-color: #1d1e1f;
}
</style>