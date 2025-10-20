<template>
  <div class="user-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary">添加用户</el-button>
        </div>
      </template>
      
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="realName" label="真实姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag :type="getRoleType(scope.row.role)">
              {{ getRoleLabel(scope.row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-switch v-model="scope.row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const users = ref([
  {
    id: 1,
    username: 'admin',
    realName: '系统管理员',
    email: 'admin@example.com',
    role: 'admin',
    status: true,
    createTime: '2025-01-01'
  },
  {
    id: 2,
    username: 'auditor1',
    realName: '张三',
    email: 'zhang@example.com',
    role: 'auditor',
    status: true,
    createTime: '2025-01-10'
  },
  {
    id: 3,
    username: 'engineer1',
    realName: '李四',
    email: 'li@example.com',
    role: 'engineer',
    status: false,
    createTime: '2025-01-15'
  }
])

const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    auditor: 'warning',
    engineer: 'success'
  }
  return types[role] || 'info'
}

const getRoleLabel = (role) => {
  const labels = {
    admin: '管理员',
    auditor: '审计员',
    engineer: '造价工程师'
  }
  return labels[role] || '未知'
}
</script>

<style scoped>
.user-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>