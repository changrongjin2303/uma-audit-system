<template>
  <div class="profile">
    <el-card>
      <template #header>
        <span>个人资料</span>
      </template>
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="userForm.realName" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const userForm = ref({
  username: 'admin',
  email: 'admin@example.com',
  realName: '系统管理员',
  phone: '13800138000'
})
</script>

<style scoped>
.profile {
  padding: 20px;
  max-width: 600px;
}
</style>