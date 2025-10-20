import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import Layout from '@/layout/index.vue'
import SystemIntroduction from '@/components/SystemIntroduction.vue'

const routes = [
  // 登录页面
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    hidden: true,
    meta: { title: '登录', noAuth: true }
  },
  // 重定向到首页
  {
    path: '/',
    redirect: '/home/dashboard'
  },
  // 首页
  {
    path: '/home',
    component: Layout,
    meta: {
      title: '首页',
      icon: 'House'
    },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/system/SystemIntroduction.vue'),
        meta: {
          title: '系统简介',
          icon: 'DataBoard',
          noCache: false
        }
      },
      {
        path: 'charts',
        name: 'ChartDemo',
        component: () => import('@/views/dashboard/ChartDemo.vue'),
        meta: {
          title: '操作流程',
          icon: 'TrendCharts',
          noCache: false
        }
      }
    ]
  },
  // 项目材料价格管理
  {
    path: '/projects',
    component: Layout,
    meta: {
      title: '项目材料价格管理',
      icon: 'FolderOpened'
    },
    children: [
      {
        path: '',
        name: 'ProjectList',
        component: () => import('@/views/projects/ProjectList.vue'),
        meta: { title: '项目管理', icon: 'List' }
      },
      {
        path: 'create',
        name: 'ProjectCreate',
        component: () => import('@/views/projects/ProjectCreate.vue'),
        meta: { title: '新建项目', icon: 'Plus' },
        hidden: true
      },
      {
        path: 'type/:type',
        name: 'ProjectTypeList',
        component: () => import('@/views/projects/ProjectTypeList.vue'),
        meta: { title: '分类项目列表' },
        hidden: true
      },
      {
        path: ':id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/ProjectDetail.vue'),
        meta: { title: '项目详情' },
        hidden: true
      },
      {
        path: ':id/materials',
        name: 'ProjectMaterials',
        component: () => import('@/views/materials/MaterialManage.vue'),
        meta: { title: '材料管理' },
        hidden: true
      },
      {
        path: ':id/material-upload',
        name: 'ProjectMaterialUpload',
        component: () => import('@/views/projects/ProjectMaterialUpload.vue'),
        meta: { title: '上传项目材料' },
        hidden: true
      },
      {
        path: ':projectId/materials/:materialId',
        name: 'ProjectMaterialDetail',
        component: () => import('@/views/projects/ProjectMaterialDetail.vue'),
        meta: { title: '项目材料详情' },
        hidden: true
      }
    ]
  },
  // 市场信息价材料管理
  {
    path: '/materials',
    component: Layout,
    meta: {
      title: '市场信息价材料',
      icon: 'Box'
    },
    children: [
      {
        path: 'base',
        name: 'BaseMaterials',
        component: () => import('@/views/materials/BaseMaterials.vue'),
        meta: { title: '市场信息价材料库', icon: 'Box' }
      },
      {
        path: 'upload',
        name: 'MaterialUpload',
        component: () => import('@/views/materials/ExcelUpload.vue'),
        meta: { title: '市场信息价查询', icon: 'Search' }
      },
      {
        path: 'import',
        name: 'MaterialImport',
        component: () => import('@/views/materials/MaterialImport.vue'),
        meta: { title: '材料导入', icon: 'Upload' },
        hidden: true
      },
      {
        path: ':id',
        name: 'MaterialDetail',
        component: () => import('@/views/materials/MaterialDetail.vue'),
        meta: { title: '材料详情' },
        hidden: true
      }
    ]
  },
  // 无信息价材料管理
  {
    path: '/unmatched-materials',
    component: Layout,
    meta: {
      title: '无信息价材料',
      icon: 'Connection'
    },
    children: [
      {
        path: 'library',
        name: 'UnmatchedMaterials',
        component: () => import('@/views/materials/UnmatchedMaterials.vue'),
        meta: { title: '无信息价材料库', icon: 'Connection' }
      },
      {
        path: 'query',
        name: 'UnmatchedMaterialsQuery',
        component: () => import('@/views/materials/UnmatchedMaterialsQuery.vue'),
        meta: { title: '无信息价查询', icon: 'Search' }
      },
      {
        path: 'import',
        name: 'UnmatchedMaterialImport',
        component: () => import('@/views/materials/UnmatchedMaterialImport.vue'),
        meta: { title: '无信息价导入', icon: 'Upload' },
        hidden: true
      }
    ]
  },
  // 价格分析
  {
    path: '/analysis',
    component: Layout,
    meta: {
      title: '价格分析',
      icon: 'TrendCharts'
    },
    children: [
      {
        path: 'results',
        name: 'AnalysisResults',
        component: () => import('@/views/analysis/AnalysisResults.vue'),
        meta: { title: '分析结果', icon: 'DataAnalysis' }
      },
      {
        path: 'details',
        name: 'AnalysisDetails',
        component: () => import('@/views/analysis/AnalysisDetails.vue'),
        meta: { title: '分析详情', hidden: true }
      }
    ]
  },
  // 报告管理
  {
    path: '/reports',
    component: Layout,
    meta: {
      title: '价格报告',
      icon: 'Document'
    },
    children: [
      {
        path: '',
        name: 'ReportsList',
        component: () => import('@/views/reports/ReportsList.vue'),
        meta: { title: '分析报告', icon: 'Document' }
      },
      {
        path: 'generate',
        name: 'ReportGenerate',
        component: () => import('@/views/reports/ReportGenerate.vue'),
        meta: { title: '生成报告', icon: 'Plus' },
        hidden: true
      },
      {
        path: ':id',
        name: 'ReportDetail',
        component: () => import('@/views/reports/ReportDetail.vue'),
        meta: { title: '报告详情' },
        hidden: true
      }
    ]
  },
  // 系统管理
  {
    path: '/system',
    component: Layout,
    meta: {
      title: '系统管理',
      icon: 'Setting',
      roles: ['admin', 'manager']
    },
    children: [
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      },
      {
        path: 'settings',
        name: 'SystemSettings',
        component: () => import('@/views/system/SystemSettings.vue'),
        meta: { title: '系统设置', icon: 'Tools', roles: ['admin'] }
      },
      {
        path: 'category-test',
        name: 'CategoryTest',
        component: () => import('@/views/test/CategoryTest.vue'),
        meta: { title: '分类API测试', icon: 'Document', roles: ['admin'] }
      }
    ]
  },
  // 个人中心
  {
    path: '/profile',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', icon: 'User' }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    hidden: true,
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 路由守卫 - 开发模式简化版
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 材料价格AI分析系统`
  }

  // 开发模式：跳过所有认证检查，直接允许访问
  console.log('开发模式：跳过认证检查，允许访问所有页面')
  next()
})

export default router
