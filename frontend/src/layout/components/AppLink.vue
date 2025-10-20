<template>
  <component :is="linkProps.tag" v-bind="linkProps">
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { isExternal } from '@/utils/validate'

const props = defineProps({
  to: {
    type: String,
    required: true
  }
})

const linkProps = computed(() => {
  if (isExternal(props.to)) {
    return {
      tag: 'a',
      href: props.to,
      target: '_blank',
      rel: 'noopener'
    }
  }
  return {
    tag: 'router-link',
    to: props.to
  }
})
</script>