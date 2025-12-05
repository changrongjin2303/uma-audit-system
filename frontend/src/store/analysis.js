import { defineStore } from 'pinia'
import { batchAnalyzeMaterials, analyzePricedMaterials } from '@/api/analysis'
import { ElMessage, ElNotification } from 'element-plus'

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    // Key: projectId, Value: { type: 'unpriced'|'priced', status, progress, currentStep, totalSteps, completedSteps, result, error }
    activeTasks: {}
  }),

  getters: {
    getTaskByProjectId: (state) => (projectId) => {
      return state.activeTasks[projectId]
    },
    isAnalyzing: (state) => (projectId) => {
      return state.activeTasks[projectId]?.status === 'running'
    }
  },

  actions: {
    async startUnpricedAnalysis(projectId, modelName, selectedModel, options = {}) {
      if (this.activeTasks[projectId]?.status === 'running') {
        ElMessage.warning('该项目正在进行分析，请稍候...')
        return
      }

      // Initialize task state
      this.activeTasks[projectId] = {
        type: 'unpriced',
        status: 'running',
        progress: 0,
        currentStep: `正在使用 ${modelName} 准备AI价格分析...`,
        totalSteps: 10,
        completedSteps: 0,
        startTime: Date.now(),
        modelName
      }

      // Show notification
      ElNotification({
        title: '后台分析已启动',
        message: `项目正在后台进行AI价格分析，您可以继续其他操作`,
        type: 'info',
        duration: 3000
      })

      // Simulate progress
      const progressInterval = setInterval(() => {
        const task = this.activeTasks[projectId]
        if (!task || task.status !== 'running') {
          clearInterval(progressInterval)
          return
        }

        if (task.progress < 90) {
          task.progress += Math.random() * 5 // Slower progress for background feeling
          if (task.progress > 90) task.progress = 90
          
          const steps = [
            '正在分析材料市场价格...',
            '正在进行价格合理性评估...',
            '正在生成分析结果...',
            '正在更新统计数据...'
          ]
          const stepIndex = Math.floor((task.progress / 100) * steps.length)
          task.currentStep = steps[stepIndex] || steps[steps.length - 1]
          task.completedSteps = Math.floor((task.progress / 100) * task.totalSteps)
        }
      }, 2000)

      try {
        const result = await batchAnalyzeMaterials(projectId, {
          force_reanalyze: true,
          batch_size: 10,
          preferred_provider: selectedModel,
          __skipLoading: true,
          ...options
        })

        clearInterval(progressInterval)
        
        if (this.activeTasks[projectId]) {
            this.activeTasks[projectId].status = 'completed'
            this.activeTasks[projectId].progress = 100
            this.activeTasks[projectId].currentStep = 'AI分析完成！'
            this.activeTasks[projectId].completedSteps = this.activeTasks[projectId].totalSteps
            this.activeTasks[projectId].result = result
        }

        ElNotification({
          title: 'AI分析完成',
          message: `使用 ${modelName} 成功分析了${result.result?.success_count || result.result?.analyzed_count || '若干'}个材料`,
          type: 'success',
          duration: 5000
        })

      } catch (error) {
        clearInterval(progressInterval)
        console.error('批量AI分析失败:', error)
        
        if (this.activeTasks[projectId]) {
            this.activeTasks[projectId].status = 'failed'
            this.activeTasks[projectId].error = error
            this.activeTasks[projectId].currentStep = '分析失败'
        }

        ElNotification({
          title: 'AI分析失败',
          message: error.message || '未知错误',
          type: 'error',
          duration: 0
        })
      }
    },

    async startPricedAnalysis(projectId, options = {}) {
      if (this.activeTasks[projectId]?.status === 'running') {
        ElMessage.warning('该项目正在进行分析，请稍候...')
        return
      }

      this.activeTasks[projectId] = {
        type: 'priced',
        status: 'running',
        progress: 0,
        currentStep: '正在准备市场信息价分析...',
        totalSteps: 8,
        completedSteps: 0,
        startTime: Date.now()
      }

      ElNotification({
        title: '后台分析已启动',
        message: `项目正在后台进行市场信息价分析，您可以继续其他操作`,
        type: 'info',
        duration: 3000
      })

      const progressInterval = setInterval(() => {
        const task = this.activeTasks[projectId]
        if (!task || task.status !== 'running') {
          clearInterval(progressInterval)
          return
        }

        if (task.progress < 90) {
          task.progress += Math.random() * 5
          if (task.progress > 90) task.progress = 90
          
          const steps = [
            '正在匹配市场信息价数据...',
            '正在计算价格差异...',
            '正在生成风险等级...',
            '正在更新分析结果...'
          ]
          const stepIndex = Math.floor((task.progress / 100) * steps.length)
          task.currentStep = steps[stepIndex] || steps[steps.length - 1]
          task.completedSteps = Math.floor((task.progress / 100) * task.totalSteps)
        }
      }, 2000)

      try {
        const result = await analyzePricedMaterials(projectId, {
          force_reanalyze: true,
          include_summary: true,
          __skipLoading: true,
          ...options
        })

        clearInterval(progressInterval)
        
        if (this.activeTasks[projectId]) {
            this.activeTasks[projectId].status = 'completed'
            this.activeTasks[projectId].progress = 100
            this.activeTasks[projectId].currentStep = '市场信息价分析完成！'
            this.activeTasks[projectId].completedSteps = this.activeTasks[projectId].totalSteps
            this.activeTasks[projectId].result = result
        }

        ElNotification({
          title: '市场信息价分析完成',
          message: `成功分析了${result.result?.analyzed_count || '若干'}个材料的价格差异`,
          type: 'success',
          duration: 5000
        })

      } catch (error) {
        clearInterval(progressInterval)
        
        if (this.activeTasks[projectId]) {
            this.activeTasks[projectId].status = 'failed'
            this.activeTasks[projectId].error = error
            this.activeTasks[projectId].currentStep = '分析失败'
        }

        ElNotification({
          title: '分析失败',
          message: error.message || '未知错误',
          type: 'error',
          duration: 0
        })
      }
    },
    
    clearTask(projectId) {
        if (this.activeTasks[projectId] && this.activeTasks[projectId].status !== 'running') {
            delete this.activeTasks[projectId]
        }
    }
  }
})
