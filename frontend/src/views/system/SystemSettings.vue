<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="basicForm" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicForm.systemName" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input v-model="basicForm.description" type="textarea" />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="basicForm.version" disabled />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="AI配置" name="ai">
          <el-form :model="aiForm" label-width="120px">
            <el-form-item label="OpenAI API Key">
              <el-input v-model="aiForm.openaiKey" type="password" show-password />
            </el-form-item>
            <el-form-item label="通义千问API Key">
              <el-input v-model="aiForm.qwenKey" type="password" show-password />
            </el-form-item>
            <el-form-item label="默认AI服务">
              <el-select v-model="aiForm.defaultService">
                <el-option label="OpenAI" value="openai" />
                <el-option label="通义千问" value="qwen" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="数据库" name="database">
          <el-form :model="dbForm" label-width="120px">
            <el-form-item label="数据库类型">
              <el-input v-model="dbForm.type" disabled />
            </el-form-item>
            <el-form-item label="连接状态">
              <el-tag :type="dbForm.connected ? 'success' : 'danger'">
                {{ dbForm.connected ? '已连接' : '未连接' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="备份策略">
              <el-select v-model="dbForm.backupStrategy">
                <el-option label="每日备份" value="daily" />
                <el-option label="每周备份" value="weekly" />
                <el-option label="手动备份" value="manual" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div style="margin-top: 20px;">
        <el-button type="primary">保存设置</el-button>
        <el-button>重置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('basic')

const basicForm = ref({
  systemName: '材料价格AI分析系统',
  description: '基于AI的智能价格分析平台',
  version: '1.0.0'
})

const aiForm = ref({
  openaiKey: '',
  qwenKey: '',
  defaultService: 'openai'
})

const dbForm = ref({
  type: 'PostgreSQL',
  connected: true,
  backupStrategy: 'daily'
})
</script>

<style scoped>
.system-settings {
  padding: 20px;
  max-width: 800px;
}
</style>
