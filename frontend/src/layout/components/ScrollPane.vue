<template>
  <div class="scroll-container">
    <div
      class="scroll-wrapper"
      ref="scrollWrapper"
      @wheel="handleScroll"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const scrollWrapper = ref(null)

const handleScroll = (e) => {
  const eventDelta = e.wheelDelta || -e.deltaY * 40
  const $scrollWrapper = scrollWrapper.value
  $scrollWrapper.scrollLeft = $scrollWrapper.scrollLeft + eventDelta / 4
}
</script>

<style lang="scss" scoped>
.scroll-container {
  white-space: nowrap;
  position: relative;
  overflow: hidden;
  width: 100%;
}

.scroll-wrapper {
  overflow: hidden;
}
</style>