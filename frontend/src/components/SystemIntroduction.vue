<template>
  <div class="system-introduction">
    <el-card class="introduction-card" v-for="(item, index) in introductionItems" :key="index">
      <div slot="header" class="clearfix">
        <span>{{ item.title }}</span>
      </div>
      <div class="content">
        {{ item.content }}
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  data() {
    return {
      introductionItems: [
        {
          title: '01 创建背景',
          content: '材料费用在工程造价中占较高，直接影响投资决策。随着建设项目中无信息价材料的使用日益广泛，其价格认定将成为审定工程结算价的要点之一。',
        },
        {
          title: '02 主要功能',
          content: '运用人工智能、大数据等新兴技术，实现智能识别工程结算书中的无信息价材料和市场信息价材料，自动分析价格合理性，并生成分析报告，有效辅助工程结算定价。',
        },
        {
          title: '03 适用范围',
          content: '本系统适用于各类建筑工程和土木工程（部分）的工程结算审核或施工图预算复核，尤其适用于新技术、新材料、新工艺、新服务等辅助定价。',
        },
        {
          title: '04 核心优势',
          content: '新兴技术融合传统业务，辅助建设项目精细化投资管控，有效提升审核工作时效和定案成果质量，并具备系统识别数据溯源功能，为避免争议提供基础保障。',
        },
      ],
    };
  },
};
</script>

<style scoped>
.system-introduction {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.introduction-card {
  width: calc(50% - 16px);
  margin-bottom: 20px;
  background-color: #e6f7ff; /* 背景颜色 */
  border: 1px solid #d9ecff; /* 边框颜色 */
  border-radius: 4px; /* 圆角 */
}

@media (max-width: 768px) {
  .introduction-card {
    width: 100%;
  }
}

.content {
  white-space: pre-line;
  padding: 16px;
}

.title {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #666;
}
</style>