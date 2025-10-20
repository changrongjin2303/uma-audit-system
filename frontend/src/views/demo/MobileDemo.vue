<template>
  <div class="mobile-demo">
    <!-- 移动端导航栏 -->
    <MobileNavbar
      :title="currentTitle"
      :show-back="showBack"
      :show-search="true"
      :tabs="navTabs"
      :active-tab="activeTab"
      @back="handleBack"
      @search-change="handleSearch"
      @tab-change="handleTabChange"
    />

    <!-- 内容区域 -->
    <div class="demo-content" :class="{ 'with-navbar': true }">
      <!-- 表格演示 -->
      <div v-if="activeTab === 'table'" class="demo-section">
        <h3>移动端表格组件</h3>
        <p>自动适配移动端的响应式表格，支持卡片布局和无限滚动</p>

        <MobileTable
          :data="tableData"
          :columns="tableColumns"
          :loading="loading.table"
          :searchable="true"
          :pagination="!infiniteMode"
          :infinite-scroll="infiniteMode"
          :selectable="true"
          title="材料列表"
          @row-click="handleRowClick"
          @load-more="handleLoadMore"
        >
          <!-- 自定义卡片内容 -->
          <template #card="{ row }">
            <div class="custom-card">
              <div class="card-header">
                <h4>{{ row.name }}</h4>
                <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
                  {{ getRiskLabel(row.riskLevel) }}
                </el-tag>
              </div>
              <div class="card-body">
                <div class="card-row">
                  <span class="label">价格:</span>
                  <span class="value price">¥{{ formatPrice(row.price) }}</span>
                </div>
                <div class="card-row">
                  <span class="label">供应商:</span>
                  <span class="value">{{ row.supplier }}</span>
                </div>
                <div class="card-row">
                  <span class="label">更新时间:</span>
                  <span class="value">{{ formatDate(row.updatedAt) }}</span>
                </div>
              </div>
            </div>
          </template>

          <!-- 操作按钮 -->
          <template #actions="{ row }">
            <el-button size="small" type="primary">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </MobileTable>

        <!-- 切换模式 -->
        <div class="mode-switch">
          <el-switch
            v-model="infiniteMode"
            active-text="无限滚动"
            inactive-text="分页模式"
          />
        </div>
      </div>

      <!-- 表单演示 -->
      <div v-else-if="activeTab === 'form'" class="demo-section">
        <h3>移动端表单组件</h3>
        <p>自适应移动端的表单组件，支持分组和各种输入类型</p>

        <MobileForm
          v-model="formData"
          :groups="formGroups"
          :rules="formRules"
          :loading="loading.form"
          @submit="handleFormSubmit"
          @cancel="handleFormCancel"
        >
          <!-- 自定义组件 -->
          <template #customField="{ row }">
            <div class="custom-field">
              <el-slider v-model="formData.rating" :max="5" show-input />
            </div>
          </template>
        </MobileForm>
      </div>

      <!-- 性能监控 -->
      <div v-else-if="activeTab === 'performance'" class="demo-section">
        <h3>性能监控</h3>
        <p>实时监控页面性能和资源使用情况</p>

        <div class="performance-cards">
          <el-card class="performance-card">
            <template #header>
              <span>加载时间</span>
            </template>
            <div class="metric-value">{{ performanceData.loadTime }}ms</div>
            <div class="metric-desc">页面完全加载时间</div>
          </el-card>

          <el-card class="performance-card">
            <template #header>
              <span>渲染时间</span>
            </template>
            <div class="metric-value">{{ Math.round(performanceData.renderTime) }}ms</div>
            <div class="metric-desc">组件渲染时间</div>
          </el-card>

          <el-card class="performance-card">
            <template #header>
              <span>内存使用</span>
            </template>
            <div class="metric-value">{{ formatBytes(performanceData.memoryUsage) }}</div>
            <div class="metric-desc">JavaScript堆内存</div>
          </el-card>

          <el-card class="performance-card">
            <template #header>
              <span>网络状态</span>
            </template>
            <div class="metric-value">
              <el-tag :type="performanceData.networkStatus === 'online' ? 'success' : 'danger'">
                {{ performanceData.networkStatus }}
              </el-tag>
            </div>
            <div class="metric-desc">连接类型: {{ performanceData.connectionType }}</div>
          </el-card>
        </div>

        <!-- 性能测试 -->
        <div class="performance-test">
          <h4>性能测试</h4>
          <el-button @click="runPerformanceTest" :loading="performanceTesting">
            运行性能测试
          </el-button>
          
          <div v-if="testResults.length > 0" class="test-results">
            <h5>测试结果</h5>
            <ul>
              <li v-for="(result, index) in testResults" :key="index">
                {{ result.name }}: {{ result.duration }}ms
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 响应式演示 -->
      <div v-else-if="activeTab === 'responsive'" class="demo-section">
        <h3>响应式适配</h3>
        <p>展示不同设备下的界面适配效果</p>

        <div class="responsive-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="设备类型">
              <el-tag :type="getDeviceTagType(responsive.device)">
                {{ responsive.device }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="视口尺寸">
              {{ responsive.viewport.width }} x {{ responsive.viewport.height }}
            </el-descriptions-item>
            <el-descriptions-item label="设备像素比">
              {{ responsive.viewport.devicePixelRatio }}
            </el-descriptions-item>
            <el-descriptions-item label="支持触摸">
              {{ responsive.supportTouch ? '是' : '否' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 触摸手势演示 -->
        <div class="gesture-demo" ref="gestureArea">
          <div class="gesture-info">
            <h4>触摸手势演示</h4>
            <p>在下方区域进行触摸操作</p>
          </div>
          
          <div class="gesture-area" :style="gestureAreaStyle">
            <div class="gesture-feedback">
              {{ gestureInfo || '等待手势操作...' }}
            </div>
          </div>
          
          <div class="gesture-log">
            <h5>手势记录</h5>
            <div v-for="(log, index) in gestureLogs" :key="index" class="log-item">
              {{ log }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 浮动操作按钮 -->
    <el-button
      class="fab"
      type="primary"
      circle
      :icon="RefreshRight"
      @click="refreshData"
      :loading="refreshing"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import { MobileTable, MobileForm, MobileNavbar } from '@/components/mobile'
import { useResponsive, useTouch, DEVICE_TYPES } from '@/utils/mobile'
import { usePerformance, debounce } from '@/utils/performance'
import { RISK_LEVELS } from '@/config'

export default {
  name: 'MobileDemo',
  components: {
    MobileTable,
    MobileForm,
    MobileNavbar,
    RefreshRight
  },
  setup() {
    const gestureArea = ref(null)
    const responsive = useResponsive()
    const performanceData = usePerformance()

    // 状态管理
    const activeTab = ref('table')
    const showBack = ref(false)
    const infiniteMode = ref(false)
    const refreshing = ref(false)
    const performanceTesting = ref(false)

    const loading = reactive({
      table: false,
      form: false
    })

    const testResults = ref([])
    const gestureLogs = ref([])
    const gestureInfo = ref('')

    // 导航配置
    const navTabs = ref([
      { name: 'table', label: '表格', icon: 'Grid' },
      { name: 'form', label: '表单', icon: 'Edit' },
      { name: 'performance', label: '性能', icon: 'Monitor' },
      { name: 'responsive', label: '响应式', icon: 'MobilePhone' }
    ])

    const currentTitle = computed(() => {
      const tab = navTabs.value.find(t => t.name === activeTab.value)
      return tab ? `${tab.label}演示` : '移动端演示'
    })

    // 表格数据
    const tableData = ref([])
    const tableColumns = ref([
      { prop: 'name', label: '材料名称', important: true },
      { prop: 'price', label: '价格', important: true },
      { prop: 'supplier', label: '供应商', important: true },
      { prop: 'riskLevel', label: '风险等级', important: true },
      { prop: 'category', label: '分类' },
      { prop: 'updatedAt', label: '更新时间' }
    ])

    // 表单数据
    const formData = reactive({
      name: '',
      category: '',
      price: null,
      supplier: '',
      description: '',
      quality: 3,
      urgent: false,
      tags: [],
      rating: 3,
      deliveryDate: '',
      files: []
    })

    const formGroups = ref([
      {
        title: '基本信息',
        description: '填写材料的基本信息',
        fields: [
          {
            prop: 'name',
            label: '材料名称',
            type: 'input',
            required: true,
            placeholder: '请输入材料名称',
            clearable: true
          },
          {
            prop: 'category',
            label: '材料分类',
            type: 'select',
            required: true,
            placeholder: '请选择分类',
            options: [
              { label: '建筑材料', value: 'building' },
              { label: '装修材料', value: 'decoration' },
              { label: '机械设备', value: 'machinery' },
              { label: '人工费', value: 'labor' }
            ]
          },
          {
            prop: 'price',
            label: '单价',
            type: 'number',
            required: true,
            min: 0,
            step: 0.01,
            precision: 2
          },
          {
            prop: 'supplier',
            label: '供应商',
            type: 'input',
            placeholder: '请输入供应商名称'
          }
        ]
      },
      {
        title: '详细信息',
        fields: [
          {
            prop: 'description',
            label: '描述',
            type: 'textarea',
            placeholder: '请输入材料描述',
            maxLength: 500,
            showWordLimit: true
          },
          {
            prop: 'quality',
            label: '质量等级',
            type: 'rate',
            max: 5,
            showText: true,
            texts: ['很差', '较差', '一般', '良好', '优秀']
          },
          {
            prop: 'urgent',
            label: '加急处理',
            type: 'switch',
            activeText: '是',
            inactiveText: '否'
          },
          {
            prop: 'tags',
            label: '标签',
            type: 'checkbox',
            options: [
              { label: '环保', value: 'eco' },
              { label: '防火', value: 'fireproof' },
              { label: '防水', value: 'waterproof' },
              { label: '耐用', value: 'durable' }
            ]
          },
          {
            prop: 'deliveryDate',
            label: '交付日期',
            type: 'date',
            placeholder: '选择交付日期'
          },
          {
            prop: 'files',
            label: '相关文件',
            type: 'upload',
            action: '/api/upload',
            accept: '.pdf,.doc,.docx,.jpg,.png',
            limit: 3
          }
        ]
      }
    ])

    const formRules = reactive({
      name: [
        { required: true, message: '请输入材料名称', trigger: 'blur' }
      ],
      category: [
        { required: true, message: '请选择材料分类', trigger: 'change' }
      ],
      price: [
        { required: true, message: '请输入单价', trigger: 'blur' },
        { type: 'number', min: 0, message: '单价不能小于0', trigger: 'blur' }
      ]
    })

    // 触摸手势
    const gestureAreaStyle = computed(() => ({
      background: responsive.supportTouch ? '#e3f2fd' : '#f5f5f5',
      minHeight: '200px',
      borderRadius: '8px',
      border: '2px dashed #ccc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      userSelect: 'none',
      touchAction: 'none'
    }))

    const { touchData, handlers } = useTouch(gestureArea)

    // 设置手势处理器
    handlers.onTap = () => {
      gestureInfo.value = '检测到点击手势'
      addGestureLog('点击手势')
    }

    handlers.onSwipeLeft = (data) => {
      gestureInfo.value = `左滑手势 (距离: ${Math.round(data.distance)}px)`
      addGestureLog(`左滑 ${Math.round(data.distance)}px`)
    }

    handlers.onSwipeRight = (data) => {
      gestureInfo.value = `右滑手势 (距离: ${Math.round(data.distance)}px)`
      addGestureLog(`右滑 ${Math.round(data.distance)}px`)
    }

    handlers.onSwipeUp = (data) => {
      gestureInfo.value = `上滑手势 (距离: ${Math.round(data.distance)}px)`
      addGestureLog(`上滑 ${Math.round(data.distance)}px`)
    }

    handlers.onSwipeDown = (data) => {
      gestureInfo.value = `下滑手势 (距离: ${Math.round(data.distance)}px)`
      addGestureLog(`下滑 ${Math.round(data.distance)}px`)
    }

    handlers.onLongPress = () => {
      gestureInfo.value = '检测到长按手势'
      addGestureLog('长按手势')
    }

    // 方法
    const addGestureLog = (message) => {
      const timestamp = new Date().toLocaleTimeString()
      gestureLogs.value.unshift(`${timestamp} - ${message}`)
      if (gestureLogs.value.length > 10) {
        gestureLogs.value = gestureLogs.value.slice(0, 10)
      }
    }

    const generateMockData = () => {
      return Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        name: `材料${i + 1}`,
        price: Math.random() * 5000 + 100,
        supplier: `供应商${Math.floor(Math.random() * 10) + 1}`,
        category: ['building', 'decoration', 'machinery', 'labor'][Math.floor(Math.random() * 4)],
        riskLevel: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
        updatedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
      }))
    }

    const formatPrice = (price) => {
      return price.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('zh-CN')
    }

    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const getRiskLabel = (level) => {
      return RISK_LEVELS[level]?.label || level
    }

    const getRiskTagType = (level) => {
      const types = {
        low: 'success',
        medium: 'warning',
        high: 'danger',
        critical: 'danger'
      }
      return types[level] || 'info'
    }

    const getDeviceTagType = (device) => {
      const types = {
        [DEVICE_TYPES.MOBILE]: 'success',
        [DEVICE_TYPES.TABLET]: 'warning',
        [DEVICE_TYPES.DESKTOP]: 'info'
      }
      return types[device] || 'info'
    }

    // 事件处理
    const handleBack = () => {
      ElMessage.info('返回上一页')
    }

    const handleSearch = debounce((value) => {
      console.log('搜索:', value)
    }, 300)

    const handleTabChange = ({ name }) => {
      activeTab.value = name
    }

    const handleRowClick = (row) => {
      ElMessage.info(`点击了材料: ${row.name}`)
    }

    const handleLoadMore = () => {
      loading.table = true
      setTimeout(() => {
        const newData = generateMockData()
        tableData.value.push(...newData.slice(0, 20))
        loading.table = false
      }, 1000)
    }

    const handleFormSubmit = (data) => {
      loading.form = true
      setTimeout(() => {
        loading.form = false
        ElNotification.success({
          title: '提交成功',
          message: '表单数据已保存'
        })
        console.log('表单数据:', data)
      }, 1500)
    }

    const handleFormCancel = () => {
      ElMessage.info('取消填写表单')
    }

    const refreshData = async () => {
      refreshing.value = true
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        tableData.value = generateMockData()
        
        ElNotification.success({
          title: '刷新完成',
          message: '数据已更新',
          duration: 2000
        })
      } catch (error) {
        ElNotification.error({
          title: '刷新失败',
          message: error.message
        })
      } finally {
        refreshing.value = false
      }
    }

    const runPerformanceTest = async () => {
      performanceTesting.value = true
      testResults.value = []

      const tests = [
        { name: '大量DOM渲染', fn: testDOMRender },
        { name: '复杂计算', fn: testCalculation },
        { name: '数组操作', fn: testArrayOperation },
        { name: '异步请求', fn: testAsyncRequest }
      ]

      for (const test of tests) {
        const start = performance.now()
        await test.fn()
        const end = performance.now()
        
        testResults.value.push({
          name: test.name,
          duration: Math.round(end - start)
        })
      }

      performanceTesting.value = false
    }

    const testDOMRender = () => {
      const fragment = document.createDocumentFragment()
      for (let i = 0; i < 1000; i++) {
        const div = document.createElement('div')
        div.textContent = `Test ${i}`
        fragment.appendChild(div)
      }
      return Promise.resolve()
    }

    const testCalculation = () => {
      let result = 0
      for (let i = 0; i < 1000000; i++) {
        result += Math.sqrt(i)
      }
      return Promise.resolve()
    }

    const testArrayOperation = () => {
      const arr = Array.from({ length: 10000 }, (_, i) => i)
      const filtered = arr.filter(n => n % 2 === 0)
      const mapped = filtered.map(n => n * 2)
      const reduced = mapped.reduce((sum, n) => sum + n, 0)
      return Promise.resolve()
    }

    const testAsyncRequest = () => {
      return new Promise(resolve => {
        setTimeout(resolve, 100)
      })
    }

    // 生命周期
    onMounted(() => {
      tableData.value = generateMockData()
    })

    return {
      gestureArea,
      responsive,
      performanceData,
      activeTab,
      showBack,
      infiniteMode,
      refreshing,
      performanceTesting,
      loading,
      testResults,
      gestureLogs,
      gestureInfo,
      navTabs,
      currentTitle,
      tableData,
      tableColumns,
      formData,
      formGroups,
      formRules,
      gestureAreaStyle,
      formatPrice,
      formatDate,
      formatBytes,
      getRiskLabel,
      getRiskTagType,
      getDeviceTagType,
      handleBack,
      handleSearch,
      handleTabChange,
      handleRowClick,
      handleLoadMore,
      handleFormSubmit,
      handleFormCancel,
      refreshData,
      runPerformanceTest
    }
  }
}
</script>

<style scoped>
.mobile-demo {
  min-height: 100vh;
  background: #f5f7fa;
}

.demo-content {
  padding: 16px;
}

.demo-content.with-navbar {
  margin-top: 56px;
  padding-top: 20px;
}

.demo-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.demo-section h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.demo-section p {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

/* 自定义卡片样式 */
.custom-card {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-body {
  space-y: 8px;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.card-row .label {
  font-size: 13px;
  color: #909399;
  min-width: 70px;
}

.card-row .value {
  font-size: 14px;
  color: #303133;
  text-align: right;
}

.card-row .value.price {
  color: #409EFF;
  font-weight: 500;
}

.mode-switch {
  margin-top: 16px;
  text-align: center;
}

/* 性能卡片 */
.performance-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.performance-card {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin: 8px 0;
}

.metric-desc {
  font-size: 12px;
  color: #909399;
}

.performance-test {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
  margin-top: 20px;
}

.test-results {
  margin-top: 16px;
}

.test-results ul {
  list-style: none;
  padding: 0;
}

.test-results li {
  padding: 4px 0;
  font-size: 13px;
  color: #606266;
}

/* 响应式信息 */
.responsive-info {
  margin-bottom: 20px;
}

/* 手势演示 */
.gesture-demo {
  margin-top: 20px;
}

.gesture-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.gesture-info p {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #909399;
}

.gesture-area {
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
}

.gesture-feedback {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  text-align: center;
}

.gesture-log {
  max-height: 150px;
  overflow-y: auto;
}

.gesture-log h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.log-item {
  font-size: 12px;
  color: #909399;
  padding: 2px 0;
  border-bottom: 1px solid #f0f2f5;
}

/* 浮动操作按钮 */
.fab {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .demo-content {
    padding: 12px;
  }

  .demo-content.with-navbar {
    margin-top: 104px; /* 导航栏 + 选项卡高度 */
  }

  .demo-section {
    padding: 16px;
    margin-bottom: 12px;
  }

  .performance-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .performance-card {
    font-size: 13px;
  }

  .metric-value {
    font-size: 20px;
  }

  .fab {
    bottom: 16px;
    right: 16px;
    width: 48px;
    height: 48px;
  }
}

@media (max-width: 375px) {
  .performance-cards {
    grid-template-columns: 1fr;
  }
  
  .card-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .card-row .value {
    text-align: left;
  }
}
</style>