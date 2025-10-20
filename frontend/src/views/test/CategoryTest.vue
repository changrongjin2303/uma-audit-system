<template>
  <div class="category-test">
    <el-card>
      <template #header>
        <h3>材料分类API测试</h3>
      </template>
      
      <el-space direction="vertical" alignment="flex-start" :size="20" style="width: 100%">
        <!-- 测试信息来源类型API -->
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>测试信息来源类型API</span>
              <el-button @click="testSourceTypes" :loading="loading.sourceTypes">测试</el-button>
            </div>
          </template>
          
          <div>
            <p><strong>请求URL:</strong> /api/v1/material-categories/source-types</p>
            <p><strong>状态:</strong> {{ results.sourceTypes.status || '未测试' }}</p>
            <pre v-if="results.sourceTypes.data">{{ JSON.stringify(results.sourceTypes.data, null, 2) }}</pre>
            <pre v-if="results.sourceTypes.error" style="color: red">{{ results.sourceTypes.error }}</pre>
          </div>
        </el-card>

        <!-- 测试分类树API -->
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>测试分类树API</span>
              <el-button @click="testCategoryTree" :loading="loading.categoryTree">测试</el-button>
            </div>
          </template>
          
          <div>
            <p><strong>请求URL:</strong> /api/v1/material-categories/tree</p>
            <p><strong>状态:</strong> {{ results.categoryTree.status || '未测试' }}</p>
            <pre v-if="results.categoryTree.data">{{ JSON.stringify(results.categoryTree.data, null, 2) }}</pre>
            <pre v-if="results.categoryTree.error" style="color: red">{{ results.categoryTree.error }}</pre>
          </div>
        </el-card>

        <!-- 测试年月分类API -->
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>测试年月分类API</span>
              <el-select v-model="testSourceType" placeholder="选择信息来源" style="margin-right: 10px">
                <el-option label="市造价信息正刊" value="municipal" />
                <el-option label="省造价信息正刊" value="provincial" />
              </el-select>
              <el-button @click="testYearMonthCategories" :loading="loading.yearMonth" :disabled="!testSourceType">测试</el-button>
            </div>
          </template>
          
          <div>
            <p><strong>请求URL:</strong> /api/v1/material-categories/year-month/{{ testSourceType || '{sourceType}' }}</p>
            <p><strong>状态:</strong> {{ results.yearMonth.status || '未测试' }}</p>
            <pre v-if="results.yearMonth.data">{{ JSON.stringify(results.yearMonth.data, null, 2) }}</pre>
            <pre v-if="results.yearMonth.error" style="color: red">{{ results.yearMonth.error }}</pre>
          </div>
        </el-card>

        <!-- 认证状态 -->
        <el-card shadow="never">
          <template #header>
            <span>认证状态</span>
          </template>
          
          <div>
            <p><strong>Token:</strong> {{ token ? '已设置' : '未设置' }}</p>
            <p><strong>用户信息:</strong> {{ user ? user.username : '未登录' }}</p>
            <el-button v-if="!token" @click="testLogin" type="primary">测试登录</el-button>
          </div>
        </el-card>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSourceTypes, getCategoryTree, getYearMonthCategories } from '@/api/categories'
import { login } from '@/api/auth'
import { getToken, setToken, getUser, setUser } from '@/utils/auth'

const loading = reactive({
  sourceTypes: false,
  categoryTree: false,
  yearMonth: false
})

const results = reactive({
  sourceTypes: {},
  categoryTree: {},
  yearMonth: {}
})

const testSourceType = ref('municipal')
const token = ref('')
const user = ref(null)

// 检查认证状态
const checkAuth = () => {
  token.value = getToken()
  user.value = getUser()
}

// 测试登录
const testLogin = async () => {
  try {
    const response = await login({
      username: 'admin',
      password: 'admin123'
    })
    
    if (response.data && response.data.access_token) {
      setToken(response.data.access_token)
      setUser(response.data.user)
      checkAuth()
      ElMessage.success('登录成功')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败: ' + error.message)
  }
}

// 测试信息来源类型API
const testSourceTypes = async () => {
  loading.sourceTypes = true
  results.sourceTypes = {}
  
  try {
    const response = await getSourceTypes()
    results.sourceTypes = {
      status: '成功',
      data: response.data
    }
    ElMessage.success('信息来源类型获取成功')
  } catch (error) {
    results.sourceTypes = {
      status: '失败',
      error: error.message || error.toString()
    }
    ElMessage.error('信息来源类型获取失败')
  } finally {
    loading.sourceTypes = false
  }
}

// 测试分类树API
const testCategoryTree = async () => {
  loading.categoryTree = true
  results.categoryTree = {}
  
  try {
    const response = await getCategoryTree()
    results.categoryTree = {
      status: '成功',
      data: response.data
    }
    ElMessage.success('分类树获取成功')
  } catch (error) {
    results.categoryTree = {
      status: '失败',
      error: error.message || error.toString()
    }
    ElMessage.error('分类树获取失败')
  } finally {
    loading.categoryTree = false
  }
}

// 测试年月分类API
const testYearMonthCategories = async () => {
  if (!testSourceType.value) {
    ElMessage.warning('请选择信息来源类型')
    return
  }
  
  loading.yearMonth = true
  results.yearMonth = {}
  
  try {
    const response = await getYearMonthCategories(testSourceType.value)
    results.yearMonth = {
      status: '成功',
      data: response.data
    }
    ElMessage.success('年月分类获取成功')
  } catch (error) {
    results.yearMonth = {
      status: '失败',
      error: error.message || error.toString()
    }
    ElMessage.error('年月分类获取失败')
  } finally {
    loading.yearMonth = false
  }
}

onMounted(() => {
  checkAuth()
})
</script>

<style scoped>
.category-test {
  padding: 20px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.4;
}
</style>