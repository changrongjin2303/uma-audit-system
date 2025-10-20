<template>
  <div class="chart-container">
    <div
      ref="chartRef"
      :style="{
        width: width + 'px',
        height: height + 'px',
        minHeight: '300px'
      }"
      class="chart"
    />
    
    <!-- 空状态 -->
    <div v-if="isEmpty" class="chart-empty">
      <el-empty :description="emptyText" />
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>{{ loadingText }}</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick, watch, computed } from 'vue'
import * as echarts from 'echarts'
import { Loading } from '@element-plus/icons-vue'
import { useAppStore } from '@/store/app'

export default {
  name: 'BaseChart',
  components: {
    Loading
  },
  props: {
    // 图表配置选项
    option: {
      type: Object,
      default: () => ({})
    },
    // 图表宽度
    width: {
      type: [String, Number],
      default: '100%'
    },
    // 图表高度
    height: {
      type: [String, Number],
      default: 400
    },
    // 是否自动调整大小
    autoResize: {
      type: Boolean,
      default: true
    },
    // 主题
    theme: {
      type: String,
      default: 'default'
    },
    // 是否加载中
    loading: {
      type: Boolean,
      default: false
    },
    // 加载提示文本
    loadingText: {
      type: String,
      default: '图表加载中...'
    },
    // 空数据提示文本
    emptyText: {
      type: String,
      default: '暂无数据'
    },
    // 响应式配置
    responsive: {
      type: Boolean,
      default: true
    },
    // 初始化选项
    initOptions: {
      type: Object,
      default: () => ({
        renderer: 'canvas'
      })
    }
  },
  emits: [
    'chart-click',
    'chart-mouseover',
    'chart-mouseout',
    'chart-ready',
    'chart-resize'
  ],
  setup(props, { emit, expose }) {
    const chartRef = ref(null)
    const chartInstance = ref(null)
    const resizeObserver = ref(null)
    const appStore = useAppStore()

    // 计算属性
    const isEmpty = computed(() => {
      if (!props.option || !props.option.series) return true
      const series = Array.isArray(props.option.series) ? props.option.series : [props.option.series]
      return series.every(s => !s.data || s.data.length === 0)
    })

    const computedWidth = computed(() => {
      return typeof props.width === 'string' ? props.width : `${props.width}px`
    })

    // 计算当前主题
    const currentTheme = computed(() => {
      return appStore.theme === 'dark' ? 'dark' : props.theme
    })

    // 初始化图表
    const initChart = async () => {
      if (!chartRef.value || chartInstance.value) return

      try {
        chartInstance.value = echarts.init(
          chartRef.value,
          currentTheme.value,
          {
            ...props.initOptions,
            width: props.width === '100%' ? undefined : props.width,
            height: props.height
          }
        )

        // 绑定事件
        bindEvents()

        // 设置配置
        if (props.option && !isEmpty.value) {
          chartInstance.value.setOption(props.option, true)
        }

        emit('chart-ready', chartInstance.value)
      } catch (error) {
        console.error('图表初始化失败:', error)
      }
    }

    // 绑定图表事件
    const bindEvents = () => {
      if (!chartInstance.value) return

      chartInstance.value.on('click', (params) => {
        emit('chart-click', params)
      })

      chartInstance.value.on('mouseover', (params) => {
        emit('chart-mouseover', params)
      })

      chartInstance.value.on('mouseout', (params) => {
        emit('chart-mouseout', params)
      })
    }

    // 更新图表
    const updateChart = (option, notMerge = false) => {
      if (!chartInstance.value) return

      try {
        chartInstance.value.setOption(option, notMerge)
      } catch (error) {
        console.error('图表更新失败:', error)
      }
    }

    // 调整图表大小
    const resizeChart = () => {
      if (chartInstance.value) {
        try {
          chartInstance.value.resize()
          emit('chart-resize')
        } catch (error) {
          console.error('图表调整大小失败:', error)
        }
      }
    }

    // 显示加载状态
    const showLoading = (text = props.loadingText) => {
      if (chartInstance.value) {
        const isDark = appStore.theme === 'dark'
        chartInstance.value.showLoading('default', {
          text: text,
          color: '#409EFF',
          textColor: isDark ? '#e4e7ed' : '#000',
          maskColor: isDark ? 'rgba(45, 45, 45, 0.8)' : 'rgba(255, 255, 255, 0.8)',
          zlevel: 0,
          fontSize: 12,
          showSpinner: true,
          spinnerRadius: 10,
          lineWidth: 5
        })
      }
    }

    // 隐藏加载状态
    const hideLoading = () => {
      if (chartInstance.value) {
        chartInstance.value.hideLoading()
      }
    }

    // 销毁图表
    const destroyChart = () => {
      if (chartInstance.value) {
        chartInstance.value.dispose()
        chartInstance.value = null
      }
    }

    // 设置响应式监听
    const setupResize = () => {
      if (!props.autoResize || !props.responsive) return

      if (window.ResizeObserver) {
        resizeObserver.value = new ResizeObserver(() => {
          resizeChart()
        })
        
        if (chartRef.value) {
          resizeObserver.value.observe(chartRef.value)
        }
      } else {
        // 兼容性处理
        window.addEventListener('resize', resizeChart)
      }
    }

    // 清理响应式监听
    const cleanupResize = () => {
      if (resizeObserver.value) {
        resizeObserver.value.disconnect()
        resizeObserver.value = null
      } else {
        window.removeEventListener('resize', resizeChart)
      }
    }

    // 监听配置变化
    watch(() => props.option, (newOption) => {
      if (newOption && chartInstance.value && !isEmpty.value) {
        updateChart(newOption)
      }
    }, { deep: true })

    // 监听加载状态
    watch(() => props.loading, (loading) => {
      if (loading) {
        showLoading()
      } else {
        hideLoading()
      }
    })

    // 监听主题变化
    watch(() => props.theme, () => {
      destroyChart()
      nextTick(() => {
        initChart()
      })
    })

    // 监听应用主题变化
    watch(() => appStore.theme, () => {
      destroyChart()
      nextTick(() => {
        initChart()
      })
    })

    // 生命周期
    onMounted(async () => {
      await nextTick()
      await initChart()
      setupResize()
    })

    onBeforeUnmount(() => {
      cleanupResize()
      destroyChart()
    })

    // 暴露方法给父组件
    expose({
      getChart: () => chartInstance.value,
      updateChart,
      resizeChart,
      showLoading,
      hideLoading,
      destroyChart
    })

    return {
      chartRef,
      isEmpty,
      computedWidth
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}

.chart {
  width: 100%;
}

.chart-empty {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  z-index: 100;
}

.chart-loading .el-icon {
  font-size: 24px;
  margin-bottom: 12px;
  color: #409EFF;
}

.chart-loading span {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .chart {
    min-height: 200px !important;
  }
}

/* 深色主题样式 */
.dark .chart-empty {
  background: #2d2d2d;
  color: #e4e7ed;
}

.dark .chart-loading {
  background: rgba(45, 45, 45, 0.8);
}

.dark .chart-loading .el-icon {
  color: #409EFF;
}

.dark .chart-loading span {
  color: #e4e7ed;
}
</style>