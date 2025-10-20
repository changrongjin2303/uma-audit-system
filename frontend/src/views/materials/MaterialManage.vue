<template>
  <div class="material-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>材料管理</span>
          <el-button type="primary">添加材料</el-button>
        </div>
      </template>
      <el-table :data="materials" style="width: 100%">
        <el-table-column prop="name" label="材料名称" />
        <el-table-column prop="specification" label="规格型号" />
        <el-table-column prop="unit" label="单位" />
        <el-table-column prop="price" label="价格" />
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

const materials = ref([
  { id: 1, name: '钢筋', specification: 'HRB400 Φ12', unit: 't', price: 4200 },
  { id: 2, name: '水泥', specification: 'P.O 42.5', unit: 't', price: 450 },
  { id: 3, name: '砂子', specification: '中砂', unit: 'm³', price: 120 }
])
</script>

<style scoped>
.material-manage {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>