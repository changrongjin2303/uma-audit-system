<template>
  <div class="project-create-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">新建项目</h1>
        <p class="page-subtitle">创建新的无信息价材料识别项目，开始材料识别分析</p>
      </div>
      <div class="header-actions">
        <el-button @click="$router.back()">
          返回
        </el-button>
      </div>
    </div>

    <!-- 创建表单 -->
    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        size="large"
        @submit.prevent="handleSubmit"
      >
        <el-row :gutter="24">
          <!-- 基本信息 -->
          <el-col :span="24">
            <div class="form-section">
              <h3 class="section-title">基本信息</h3>
              <el-row :gutter="24">
                <el-col :lg="12" :span="24">
                  <el-form-item label="项目名称" prop="name">
                    <el-input
                      v-model="form.name"
                      placeholder="请输入项目名称"
                      maxlength="100"
                      show-word-limit
                    />
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="项目地点" prop="location">
                    <el-input
                      v-model="form.location"
                      placeholder="请输入项目地点"
                      maxlength="100"
                      show-word-limit
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :lg="12" :span="24">
                  <el-form-item label="项目类型" prop="project_type">
                    <el-select
                      v-model="form.project_type"
                      placeholder="请选择项目类型"
                      style="width: 100%"
                    >
                      <el-option label="建筑工程" value="building" />
                      <el-option label="装修工程" value="decoration" />
                      <el-option label="市政工程" value="municipal" />
                      <el-option label="园林工程" value="landscape" />
                      <el-option label="公路工程" value="highway" />
                      <el-option label="其他工程" value="other" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="工程造价" prop="budget_amount">
                    <el-input
                      v-model="form.budget_amount"
                      placeholder="请输入工程造价（万元）"
                      type="number"
                      step="0.01"
                      min="0"
                    >
                      <template #append>万元</template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="项目描述" prop="description">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入项目描述信息，包括工程概况、主要内容等"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </div>
          </el-col>

          <!-- 分析设置 -->
          <el-col :span="24">
            <div class="form-section">
              <h3 class="section-title">分析设置</h3>
              <el-row :gutter="24">
                <el-col :lg="12" :span="24">
                  <el-form-item label="基期信息价日期" prop="base_price_date">
                    <el-date-picker
                      v-model="form.base_price_date"
                      type="month"
                      placeholder="选择基期信息价日期"
                      format="YYYY-MM"
                      value-format="YYYY-MM"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="基期信息价地区" prop="base_price_region">
                    <div class="region-selector">
                      <el-select
                        v-model="form.base_price_province"
                        placeholder="选择省份"
                        style="width: 32%; margin-right: 2%"
                        @change="handleProvinceChange"
                      >
                        <el-option
                          v-for="province in provinces"
                          :key="province.code"
                          :label="province.name"
                          :value="province.code"
                        />
                      </el-select>
                      <el-select
                        v-model="form.base_price_city"
                        placeholder="选择城市"
                        style="width: 32%; margin-right: 2%"
                        :disabled="!form.base_price_province"
                        @change="handleCityChange"
                      >
                        <el-option
                          v-for="city in cities"
                          :key="city.code"
                          :label="city.name"
                          :value="city.code"
                        />
                      </el-select>
                      <el-select
                        v-model="form.base_price_district"
                        placeholder="选择区"
                        style="width: 32%"
                        :disabled="!form.base_price_city"
                      >
                        <el-option
                          v-for="district in districts"
                          :key="district.code"
                          :label="district.name"
                          :value="district.code"
                        />
                      </el-select>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="合同开始月份">
                    <el-date-picker
                      v-model="form.contract_start_date"
                      type="month"
                      placeholder="选择合同开始月份"
                      format="YYYY-MM"
                      value-format="YYYY-MM"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="合同结束月份">
                    <el-date-picker
                      v-model="form.contract_end_date"
                      type="month"
                      placeholder="选择合同结束月份"
                      format="YYYY-MM"
                      value-format="YYYY-MM"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :lg="12" :span="24">
                  <el-form-item label="是否支持调价" prop="support_price_adjustment">
                    <el-select
                      v-model="form.support_price_adjustment"
                      placeholder="请选择是否支持调价"
                      style="width: 100%"
                      @change="handlePriceAdjustmentChange"
                    >
                      <el-option label="是" :value="true" />
                      <el-option label="否" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :lg="12" :span="24">
                  <el-form-item label="调价范围" prop="price_adjustment_range">
                    <el-input
                      v-model="form.price_adjustment_range"
                      placeholder="请输入调价范围"
                      type="number"
                      step="0.1"
                      min="0"
                      max="100"
                      :disabled="!form.support_price_adjustment"
                    >
                      <template #append>%</template>
                    </el-input>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="24">
                  <el-form-item label="分析范围" prop="audit_scope">
                    <el-checkbox-group v-model="form.audit_scope">
                      <el-checkbox label="price_analysis">价格合理性分析</el-checkbox>
                      <el-checkbox label="material_matching">材料匹配度检查</el-checkbox>
                      <el-checkbox label="market_comparison">市场价格对比</el-checkbox>
                      <el-checkbox label="risk_assessment">风险评估</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-col>

          <!-- 材料导入 -->
          <el-col :span="24">
            <div class="form-section">
              <h3 class="section-title">材料导入</h3>
              <el-form-item label="初始材料清单">
                <div class="upload-section">
                  <el-upload
                    ref="uploadRef"
                    :file-list="fileList"
                    :auto-upload="false"
                    accept=".xlsx,.xls,.csv"
                    :on-change="handleFileChange"
                    :on-remove="handleFileRemove"
                    :before-upload="beforeUpload"
                    drag
                    multiple
                  >
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">
                      将文件拖到此处，或<em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 Excel (.xlsx, .xls) 和 CSV 格式文件，单个文件不超过 50MB
                      </div>
                    </template>
                  </el-upload>
                  
                  <!-- 文件预览 -->
                  <div v-if="fileList.length > 0" class="file-preview">
                    <h4>待导入文件:</h4>
                    <ul class="file-list">
                      <li v-for="file in fileList" :key="file.uid" class="file-item">
                        <el-icon><Document /></el-icon>
                        <span class="file-name">{{ file.name }}</span>
                        <span class="file-size">{{ formatFileSize(file.size) }}</span>
                        <el-button
                          type="danger"
                          link
                          :icon="Delete"
                          @click="handleFileRemove(file)"
                        />
                      </li>
                    </ul>
                  </div>
                </div>
              </el-form-item>
            </div>
          </el-col>
        </el-row>

        <!-- 表单操作 -->
        <div class="form-actions">
          <el-button
            size="large"
            @click="$router.back()"
          >
            取消
          </el-button>
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            @click="handleSubmit"
          >
            {{ fileList.length > 0 ? '创建项目并导入材料' : '创建项目' }}
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Document, Delete } from '@element-plus/icons-vue'
import { createProject, uploadExcel } from '@/api/projects'

const router = useRouter()

// 响应式数据
const formRef = ref()
const uploadRef = ref()
const submitting = ref(false)
const fileList = ref([])
const cities = ref([])
const districts = ref([])

// 省份和城市数据
const provinces = ref([
  { code: '110000', name: '北京市' },
  { code: '120000', name: '天津市' },
  { code: '130000', name: '河北省' },
  { code: '140000', name: '山西省' },
  { code: '150000', name: '内蒙古自治区' },
  { code: '210000', name: '辽宁省' },
  { code: '220000', name: '吉林省' },
  { code: '230000', name: '黑龙江省' },
  { code: '310000', name: '上海市' },
  { code: '320000', name: '江苏省' },
  { code: '330000', name: '浙江省' },
  { code: '340000', name: '安徽省' },
  { code: '350000', name: '福建省' },
  { code: '360000', name: '江西省' },
  { code: '370000', name: '山东省' },
  { code: '410000', name: '河南省' },
  { code: '420000', name: '湖北省' },
  { code: '430000', name: '湖南省' },
  { code: '440000', name: '广东省' },
  { code: '450000', name: '广西壮族自治区' },
  { code: '460000', name: '海南省' },
  { code: '500000', name: '重庆市' },
  { code: '510000', name: '四川省' },
  { code: '520000', name: '贵州省' },
  { code: '530000', name: '云南省' },
  { code: '540000', name: '西藏自治区' },
  { code: '610000', name: '陕西省' },
  { code: '620000', name: '甘肃省' },
  { code: '630000', name: '青海省' },
  { code: '640000', name: '宁夏回族自治区' },
  { code: '650000', name: '新疆维吾尔自治区' }
])

// 城市数据映射
const provinceCitiesMap = {
  '110000': [{ code: '110100', name: '北京市' }],
  '120000': [{ code: '120100', name: '天津市' }],
  '130000': [
    { code: '130100', name: '石家庄市' },
    { code: '130200', name: '唐山市' },
    { code: '130300', name: '秦皇岛市' },
    { code: '130400', name: '邯郸市' },
    { code: '130500', name: '邢台市' },
    { code: '130600', name: '保定市' },
    { code: '130700', name: '张家口市' },
    { code: '130800', name: '承德市' },
    { code: '130900', name: '沧州市' },
    { code: '131000', name: '廊坊市' },
    { code: '131100', name: '衡水市' }
  ],
  '140000': [
    { code: '140100', name: '太原市' },
    { code: '140200', name: '大同市' },
    { code: '140300', name: '阳泉市' },
    { code: '140400', name: '长治市' },
    { code: '140500', name: '晋城市' },
    { code: '140600', name: '朔州市' },
    { code: '140700', name: '晋中市' },
    { code: '140800', name: '运城市' },
    { code: '140900', name: '忻州市' },
    { code: '141000', name: '临汾市' },
    { code: '141100', name: '吕梁市' }
  ],
  '150000': [
    { code: '150100', name: '呼和浩特市' },
    { code: '150200', name: '包头市' },
    { code: '150300', name: '乌海市' },
    { code: '150400', name: '赤峰市' },
    { code: '150500', name: '通辽市' },
    { code: '150600', name: '鄂尔多斯市' },
    { code: '150700', name: '呼伦贝尔市' },
    { code: '150800', name: '巴彦淖尔市' },
    { code: '150900', name: '乌兰察布市' }
  ],
  '210000': [
    { code: '210100', name: '沈阳市' },
    { code: '210200', name: '大连市' },
    { code: '210300', name: '鞍山市' },
    { code: '210400', name: '抚顺市' },
    { code: '210500', name: '本溪市' },
    { code: '210600', name: '丹东市' },
    { code: '210700', name: '锦州市' },
    { code: '210800', name: '营口市' },
    { code: '210900', name: '阜新市' },
    { code: '211000', name: '辽阳市' },
    { code: '211100', name: '盘锦市' },
    { code: '211200', name: '铁岭市' },
    { code: '211300', name: '朝阳市' },
    { code: '211400', name: '葫芦岛市' }
  ],
  '220000': [
    { code: '220100', name: '长春市' },
    { code: '220200', name: '吉林市' },
    { code: '220300', name: '四平市' },
    { code: '220400', name: '辽源市' },
    { code: '220500', name: '通化市' },
    { code: '220600', name: '白山市' },
    { code: '220700', name: '松原市' },
    { code: '220800', name: '白城市' },
    { code: '222400', name: '延边朝鲜族自治州' }
  ],
  '230000': [
    { code: '230100', name: '哈尔滨市' },
    { code: '230200', name: '齐齐哈尔市' },
    { code: '230300', name: '鸡西市' },
    { code: '230400', name: '鹤岗市' },
    { code: '230500', name: '双鸭山市' },
    { code: '230600', name: '大庆市' },
    { code: '230700', name: '伊春市' },
    { code: '230800', name: '佳木斯市' },
    { code: '230900', name: '七台河市' },
    { code: '231000', name: '牡丹江市' },
    { code: '231100', name: '黑河市' },
    { code: '231200', name: '绥化市' }
  ],
  '310000': [{ code: '310100', name: '上海市' }],
  '320000': [
    { code: '320100', name: '南京市' },
    { code: '320200', name: '无锡市' },
    { code: '320300', name: '徐州市' },
    { code: '320400', name: '常州市' },
    { code: '320500', name: '苏州市' },
    { code: '320600', name: '南通市' },
    { code: '320700', name: '连云港市' },
    { code: '320800', name: '淮安市' },
    { code: '320900', name: '盐城市' },
    { code: '321000', name: '扬州市' },
    { code: '321100', name: '镇江市' },
    { code: '321200', name: '泰州市' },
    { code: '321300', name: '宿迁市' }
  ],
  '330000': [
    { code: '330100', name: '杭州市' },
    { code: '330200', name: '宁波市' },
    { code: '330300', name: '温州市' },
    { code: '330400', name: '嘉兴市' },
    { code: '330500', name: '湖州市' },
    { code: '330600', name: '绍兴市' },
    { code: '330700', name: '金华市' },
    { code: '330800', name: '衢州市' },
    { code: '330900', name: '舟山市' },
    { code: '331000', name: '台州市' },
    { code: '331100', name: '丽水市' }
  ],
  '340000': [
    { code: '340100', name: '合肥市' },
    { code: '340200', name: '芜湖市' },
    { code: '340300', name: '蚌埠市' },
    { code: '340400', name: '淮南市' },
    { code: '340500', name: '马鞍山市' },
    { code: '340600', name: '淮北市' },
    { code: '340700', name: '铜陵市' },
    { code: '340800', name: '安庆市' },
    { code: '341000', name: '黄山市' },
    { code: '341100', name: '滁州市' },
    { code: '341200', name: '阜阳市' },
    { code: '341300', name: '宿州市' },
    { code: '341500', name: '六安市' },
    { code: '341600', name: '亳州市' },
    { code: '341700', name: '池州市' },
    { code: '341800', name: '宣城市' }
  ],
  '350000': [
    { code: '350100', name: '福州市' },
    { code: '350200', name: '厦门市' },
    { code: '350300', name: '莆田市' },
    { code: '350400', name: '三明市' },
    { code: '350500', name: '泉州市' },
    { code: '350600', name: '漳州市' },
    { code: '350700', name: '南平市' },
    { code: '350800', name: '龙岩市' },
    { code: '350900', name: '宁德市' }
  ],
  '360000': [
    { code: '360100', name: '南昌市' },
    { code: '360200', name: '景德镇市' },
    { code: '360300', name: '萍乡市' },
    { code: '360400', name: '九江市' },
    { code: '360500', name: '新余市' },
    { code: '360600', name: '鹰潭市' },
    { code: '360700', name: '赣州市' },
    { code: '360800', name: '吉安市' },
    { code: '360900', name: '宜春市' },
    { code: '361000', name: '抚州市' },
    { code: '361100', name: '上饶市' }
  ],
  '370000': [
    { code: '370100', name: '济南市' },
    { code: '370200', name: '青岛市' },
    { code: '370300', name: '淄博市' },
    { code: '370400', name: '枣庄市' },
    { code: '370500', name: '东营市' },
    { code: '370600', name: '烟台市' },
    { code: '370700', name: '潍坊市' },
    { code: '370800', name: '济宁市' },
    { code: '370900', name: '泰安市' },
    { code: '371000', name: '威海市' },
    { code: '371100', name: '日照市' },
    { code: '371200', name: '莱芜市' },
    { code: '371300', name: '临沂市' },
    { code: '371400', name: '德州市' },
    { code: '371500', name: '聊城市' },
    { code: '371600', name: '滨州市' },
    { code: '371700', name: '菏泽市' }
  ],
  '410000': [
    { code: '410100', name: '郑州市' },
    { code: '410200', name: '开封市' },
    { code: '410300', name: '洛阳市' },
    { code: '410400', name: '平顶山市' },
    { code: '410500', name: '安阳市' },
    { code: '410600', name: '鹤壁市' },
    { code: '410700', name: '新乡市' },
    { code: '410800', name: '焦作市' },
    { code: '410900', name: '濮阳市' },
    { code: '411000', name: '许昌市' },
    { code: '411100', name: '漯河市' },
    { code: '411200', name: '三门峡市' },
    { code: '411300', name: '南阳市' },
    { code: '411400', name: '商丘市' },
    { code: '411500', name: '信阳市' },
    { code: '411600', name: '周口市' },
    { code: '411700', name: '驻马店市' }
  ],
  '420000': [
    { code: '420100', name: '武汉市' },
    { code: '420200', name: '黄石市' },
    { code: '420300', name: '十堰市' },
    { code: '420500', name: '宜昌市' },
    { code: '420600', name: '襄阳市' },
    { code: '420700', name: '鄂州市' },
    { code: '420800', name: '荆门市' },
    { code: '420900', name: '孝感市' },
    { code: '421000', name: '荆州市' },
    { code: '421100', name: '黄冈市' },
    { code: '421200', name: '咸宁市' },
    { code: '421300', name: '随州市' }
  ],
  '430000': [
    { code: '430100', name: '长沙市' },
    { code: '430200', name: '株洲市' },
    { code: '430300', name: '湘潭市' },
    { code: '430400', name: '衡阳市' },
    { code: '430500', name: '邵阳市' },
    { code: '430600', name: '岳阳市' },
    { code: '430700', name: '常德市' },
    { code: '430800', name: '张家界市' },
    { code: '430900', name: '益阳市' },
    { code: '431000', name: '郴州市' },
    { code: '431100', name: '永州市' },
    { code: '431200', name: '怀化市' },
    { code: '431300', name: '娄底市' }
  ],
  '440000': [
    { code: '440100', name: '广州市' },
    { code: '440200', name: '韶关市' },
    { code: '440300', name: '深圳市' },
    { code: '440400', name: '珠海市' },
    { code: '440500', name: '汕头市' },
    { code: '440600', name: '佛山市' },
    { code: '440700', name: '江门市' },
    { code: '440800', name: '湛江市' },
    { code: '440900', name: '茂名市' },
    { code: '441200', name: '肇庆市' },
    { code: '441300', name: '惠州市' },
    { code: '441400', name: '梅州市' },
    { code: '441500', name: '汕尾市' },
    { code: '441600', name: '河源市' },
    { code: '441700', name: '阳江市' },
    { code: '441800', name: '清远市' },
    { code: '441900', name: '东莞市' },
    { code: '442000', name: '中山市' },
    { code: '445100', name: '潮州市' },
    { code: '445200', name: '揭阳市' },
    { code: '445300', name: '云浮市' }
  ],
  '450000': [
    { code: '450100', name: '南宁市' },
    { code: '450200', name: '柳州市' },
    { code: '450300', name: '桂林市' },
    { code: '450400', name: '梧州市' },
    { code: '450500', name: '北海市' },
    { code: '450600', name: '防城港市' },
    { code: '450700', name: '钦州市' },
    { code: '450800', name: '贵港市' },
    { code: '450900', name: '玉林市' },
    { code: '451000', name: '百色市' },
    { code: '451100', name: '贺州市' },
    { code: '451200', name: '河池市' },
    { code: '451300', name: '来宾市' },
    { code: '451400', name: '崇左市' }
  ],
  '460000': [
    { code: '460100', name: '海口市' },
    { code: '460200', name: '三亚市' },
    { code: '460300', name: '三沙市' },
    { code: '460400', name: '儋州市' }
  ],
  '500000': [{ code: '500100', name: '重庆市' }],
  '510000': [
    { code: '510100', name: '成都市' },
    { code: '510300', name: '自贡市' },
    { code: '510400', name: '攀枝花市' },
    { code: '510500', name: '泸州市' },
    { code: '510600', name: '德阳市' },
    { code: '510700', name: '绵阳市' },
    { code: '510800', name: '广元市' },
    { code: '510900', name: '遂宁市' },
    { code: '511000', name: '内江市' },
    { code: '511100', name: '乐山市' },
    { code: '511300', name: '南充市' },
    { code: '511400', name: '眉山市' },
    { code: '511500', name: '宜宾市' },
    { code: '511600', name: '广安市' },
    { code: '511700', name: '达州市' },
    { code: '511800', name: '雅安市' },
    { code: '511900', name: '巴中市' },
    { code: '512000', name: '资阳市' }
  ],
  '520000': [
    { code: '520100', name: '贵阳市' },
    { code: '520200', name: '六盘水市' },
    { code: '520300', name: '遵义市' },
    { code: '520400', name: '安顺市' },
    { code: '520500', name: '毕节市' },
    { code: '520600', name: '铜仁市' }
  ],
  '530000': [
    { code: '530100', name: '昆明市' },
    { code: '530300', name: '曲靖市' },
    { code: '530400', name: '玉溪市' },
    { code: '530500', name: '保山市' },
    { code: '530600', name: '昭通市' },
    { code: '530700', name: '丽江市' },
    { code: '530800', name: '普洱市' },
    { code: '530900', name: '临沧市' }
  ],
  '540000': [
    { code: '540100', name: '拉萨市' },
    { code: '540200', name: '日喀则市' },
    { code: '540300', name: '昌都市' },
    { code: '540400', name: '林芝市' },
    { code: '540500', name: '山南市' },
    { code: '540600', name: '那曲市' }
  ],
  '610000': [
    { code: '610100', name: '西安市' },
    { code: '610200', name: '铜川市' },
    { code: '610300', name: '宝鸡市' },
    { code: '610400', name: '咸阳市' },
    { code: '610500', name: '渭南市' },
    { code: '610600', name: '延安市' },
    { code: '610700', name: '汉中市' },
    { code: '610800', name: '榆林市' },
    { code: '610900', name: '安康市' },
    { code: '611000', name: '商洛市' }
  ],
  '620000': [
    { code: '620100', name: '兰州市' },
    { code: '620200', name: '嘉峪关市' },
    { code: '620300', name: '金昌市' },
    { code: '620400', name: '白银市' },
    { code: '620500', name: '天水市' },
    { code: '620600', name: '武威市' },
    { code: '620700', name: '张掖市' },
    { code: '620800', name: '平凉市' },
    { code: '620900', name: '酒泉市' },
    { code: '621000', name: '庆阳市' },
    { code: '621100', name: '定西市' },
    { code: '621200', name: '陇南市' }
  ],
  '630000': [
    { code: '630100', name: '西宁市' },
    { code: '630200', name: '海东市' }
  ],
  '640000': [
    { code: '640100', name: '银川市' },
    { code: '640200', name: '石嘴山市' },
    { code: '640300', name: '吴忠市' },
    { code: '640400', name: '固原市' },
    { code: '640500', name: '中卫市' }
  ],
  '650000': [
    { code: '650100', name: '乌鲁木齐市' },
    { code: '650200', name: '克拉玛依市' },
    { code: '650400', name: '吐鲁番市' },
    { code: '650500', name: '哈密市' }
  ]
}

// 表单数据
const form = reactive({
  name: '',
  location: '',
  project_type: '',
  budget_amount: '',
  description: '',
  base_price_date: '',
  base_price_province: '',
  base_price_city: '',
  base_price_district: '',
  support_price_adjustment: true,
  price_adjustment_range: 5,
  audit_scope: ['price_analysis', 'material_matching'],
  contract_start_date: '',
  contract_end_date: ''
})

// 验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 100, message: '项目名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  project_type: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  location: [
    { max: 100, message: '项目地点不能超过100个字符', trigger: 'blur' }
  ],
  budget_amount: [
    { 
      validator: (rule, value, callback) => {
        if (!value || value === '') {
          callback() // 允许为空
        } else if (!/^\d+(\.\d{1,2})?$/.test(value)) {
          callback(new Error('请输入有效的金额'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  base_price_date: [
    { required: true, message: '请选择基期信息价日期', trigger: 'change' }
  ],
  base_price_province: [
    { required: true, message: '请选择省份', trigger: 'change' }
  ],
  base_price_city: [
    { required: true, message: '请选择城市', trigger: 'change' }
  ],
  base_price_district: [
    { required: true, message: '请选择区', trigger: 'change' }
  ],
  support_price_adjustment: [
    { required: true, message: '请选择是否支持调价', trigger: 'change' }
  ],
  price_adjustment_range: [
    { required: true, message: '请输入调价范围', trigger: 'blur' },
    { pattern: /^(0|[1-9]\d*)(\.\d+)?$/, message: '请输入有效的百分比', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        if (value < 0 || value > 100) {
          callback(new Error('调价范围必须在0-100%之间'))
        } else {
          callback()
        }
      }, trigger: 'blur' }
  ],
  audit_scope: [
    { type: 'array', min: 1, message: '请至少选择一项分析范围', trigger: 'change' }
  ]
}

// 文件处理
const handleFileChange = (file, fileList) => {
  // 文件大小检查
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  // 文件格式检查
  const allowedTypes = ['.xlsx', '.xls', '.csv']
  const fileExtension = file.name.toLowerCase().substr(file.name.lastIndexOf('.'))
  if (!allowedTypes.includes(fileExtension)) {
    ElMessage.error('只支持 Excel 和 CSV 格式文件')
    return false
  }
}

const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const beforeUpload = (file) => {
  return false // 阻止自动上传
}

// 杭州市区数据（2021年行政区划调整后）
const hangzhouDistricts = [
  { code: '330102', name: '上城区' },
  { code: '330104', name: '拱墅区' },
  { code: '330105', name: '西湖区' },
  { code: '330106', name: '滨江区' },
  { code: '330107', name: '萧山区' },
  { code: '330110', name: '余杭区' },
  { code: '330111', name: '富阳区' },
  { code: '330112', name: '临安区' },
  { code: '330113', name: '临平区' },
  { code: '330114', name: '钱塘区' },
  { code: '330122', name: '桐庐县' },
  { code: '330127', name: '淳安县' },
  { code: '330182', name: '建德市' }
]

// 省份选择处理
const handleProvinceChange = (provinceCode) => {
  form.base_price_city = '' // 清空城市选择
  form.base_price_district = '' // 清空区选择
  cities.value = provinceCitiesMap[provinceCode] || []
  districts.value = [] // 清空区列表
}

// 城市选择处理
const handleCityChange = (cityCode) => {
  form.base_price_district = '' // 清空区选择
  
  // 只有杭州市才显示区选项
  if (cityCode === '330100') {
    districts.value = hangzhouDistricts
  } else {
    districts.value = []
  }
}

// 监听调价支持状态变化
const handlePriceAdjustmentChange = () => {
  if (!form.support_price_adjustment) {
    form.price_adjustment_range = 0
  } else {
    form.price_adjustment_range = 5 // 恢复默认值
  }
}

// 工具函数
const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

// 表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 表单验证
    await formRef.value.validate()
    
    submitting.value = true
    
    // 创建项目
    const projectData = { ...form }
    // 处理 budget_amount：空字符串转为 null，有值转为数字
    if (projectData.budget_amount === '' || projectData.budget_amount === null || projectData.budget_amount === undefined) {
      projectData.budget_amount = null
    } else {
      const budgetValue = parseFloat(projectData.budget_amount)
      projectData.budget_amount = isNaN(budgetValue) ? null : budgetValue
    }
    
    // 将合同工期以规范格式写入描述，确保后端未支持字段时也能保存
    const fmt = (m) => {
      if (!m) return null
      const [y, mm] = String(m).split('-')
      return y && mm ? `${y}年${mm.padStart(2, '0')}月` : null
    }
    const cpStart = fmt(projectData.contract_start_date)
    const cpEnd = fmt(projectData.contract_end_date)
    if (cpStart && cpEnd) {
      const periodText = `合同工期：${cpStart}至${cpEnd}`
      projectData.contract_period = `${cpStart}至${cpEnd}`
      projectData.description = projectData.description ? `${projectData.description}\n${periodText}` : periodText
    }

    const response = await createProject(projectData)
    const projectId = response.id
    
    ElMessage.success('项目创建成功')
    
    // 如果有文件需要上传
    if (fileList.value.length > 0) {
      try {
        ElMessage.info('开始上传材料文件...')
        
        // 上传文件
        for (const file of fileList.value) {
          await uploadExcel(projectId, file.raw, (progressEvent) => {
            // 可以在这里更新上传进度
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            console.log(`文件 ${file.name} 上传进度: ${progress}%`)
          })
        }
        
        ElMessage.success('材料文件上传成功')
      } catch (error) {
        ElMessage.warning('项目创建成功，但文件上传失败，请在项目详情页重新上传')
        console.error('文件上传失败:', error)
      }
    }
    
    // 跳转到项目详情页
    router.push(`/projects/${projectId}`)
    
  } catch (error) {
    if (error.errors) {
      // 表单验证错误
      ElMessage.error('请检查表单信息')
    } else {
      ElMessage.error('创建项目失败')
      console.error('创建项目失败:', error)
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss" scoped>
.project-create-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;

  .header-content {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
    }
  }
}

.form-card {
  .form-section {
    margin-bottom: 32px;

    &:last-child {
      margin-bottom: 0;
    }

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 20px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid $border-color-lighter;
    }
  }

  .upload-section {
    .file-preview {
      margin-top: 16px;
      padding: 16px;
      background-color: $bg-color-base;
      border-radius: 8px;

      h4 {
        font-size: 14px;
        font-weight: 500;
        margin: 0 0 12px 0;
        color: $text-primary;
      }

      .file-list {
        list-style: none;
        margin: 0;
        padding: 0;

        .file-item {
          display: flex;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid $border-color-lighter;

          &:last-child {
            border-bottom: none;
          }

          .el-icon {
            margin-right: 8px;
            color: $primary-color;
          }

          .file-name {
            flex: 1;
            font-size: 14px;
            color: $text-primary;
          }

          .file-size {
            margin-right: 12px;
            font-size: 12px;
            color: $text-secondary;
          }
        }
      }
    }
  }

  .form-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding-top: 24px;
    border-top: 1px solid $border-color-lighter;
    margin-top: 32px;
  }

  .region-selector {
    display: flex;
    width: 100%;
    align-items: center;
  }
}

// 复选框组优化
:deep(.el-checkbox-group) {
  .el-checkbox {
    margin-right: 20px;
    margin-bottom: 12px;
    
    .el-checkbox__label {
      font-weight: normal;
    }
  }
}

// 选择器选项优化
:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 12px 20px;
  line-height: 1.4;
}

// 上传组件优化
:deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .project-create-container {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .form-card {
    :deep(.el-form-item__label) {
      text-align: left;
    }

    .region-selector {
      flex-direction: column;
      gap: 12px;
      
      .el-select {
        width: 100% !important;
        margin-right: 0 !important;
      }
    }

    .form-actions {
      flex-direction: column;
      
      .el-button {
        width: 100%;
      }
    }
  }
}
</style>
