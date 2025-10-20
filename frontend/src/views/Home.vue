<template>
  <div>
    <!-- 其他内容 -->
    <el-link type="primary" @click="goToSystemIntroduction">系统简介</el-link>
  </div>
</template>

<script>
export default {
  methods: {
    goToSystemIntroduction() {
      this.$router.push('/system-introduction');
    }
  }
};
</script>

<style scoped>
.statistic-card {
  background-color: #f9fafc; /* 确保背景颜色设置正确 */
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .statistic-card {
    width: 100%;
  }
}
</style>