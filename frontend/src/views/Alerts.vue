<template>
  <div class="alerts-page">
    <div class="page-title">
      <h2>价格预警</h2>
      <el-button type="primary" :loading="checking" @click="checkAlerts">检查触发</el-button>
    </div>

    <!-- 添加预警表单 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <span>添加预警</span>
      </template>
      <el-form :model="form" inline>
        <el-form-item label="股票代码">
          <el-input v-model="form.stockCode" placeholder="如：00700" />
        </el-form-item>
        <el-form-item label="股票名称">
          <el-input v-model="form.stockName" placeholder="如：腾讯控股" />
        </el-form-item>
        <el-form-item label="预警类型">
          <el-select v-model="form.alertType">
            <el-option label="涨到" value="ABOVE" />
            <el-option label="跌到" value="BELOW" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标价格">
          <el-input-number v-model="form.targetPrice" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addAlert">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预警列表 -->
    <el-table :data="alerts" stripe v-loading="loading">
      <el-table-column prop="stockCode" label="代码" width="120" />
      <el-table-column prop="stockName" label="名称" width="200" />
      <el-table-column prop="alertType" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.alertType === 'ABOVE' ? 'danger' : 'success'">
            {{ row.alertType === 'ABOVE' ? '涨到' : '跌到' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="targetPrice" label="目标价格" width="120" />
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="deleteAlert(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import axios from 'axios'

const alerts = ref([])
const loading = ref(false)
const checking = ref(false)
const form = reactive({
  stockCode: '',
  stockName: '',
  alertType: 'ABOVE',
  targetPrice: null
})

onMounted(async () => {
  await loadAlerts()
  await checkAlerts(false)
  setInterval(() => checkAlerts(false), 60000)
})

const loadAlerts = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/alert')
    alerts.value = res.data
  } catch (e) { console.error(e) }
  loading.value = false
}

const addAlert = async () => {
  if (!form.stockCode || !form.targetPrice) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await axios.post('/api/alert', { ...form })
    ElMessage.success('预警添加成功')
    form.stockCode = ''
    form.stockName = ''
    form.targetPrice = null
    await loadAlerts()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const checkAlerts = async (showEmpty = true) => {
  checking.value = true
  try {
    const res = await axios.post('/api/alert/check')
    const triggered = res.data || []
    if (triggered.length > 0) {
      triggered.forEach(item => {
        ElNotification({
          title: '价格预警触发',
          message: `${item.stockName || item.stockCode} 已${item.alertType === 'ABOVE' ? '涨到' : '跌到'} ${item.targetPrice}`,
          type: item.alertType === 'ABOVE' ? 'success' : 'warning',
          duration: 8000
        })
      })
      await loadAlerts()
    } else if (showEmpty) {
      ElMessage.info('暂无触发的预警')
    }
  } catch (e) {
    console.error(e)
    if (showEmpty) ElMessage.error('检查失败')
  } finally {
    checking.value = false
  }
}

const deleteAlert = async (id) => {
  try {
    await axios.delete(`/api/alert/${id}`)
    ElMessage.success('已删除')
    await loadAlerts()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.alerts-page h2 {
  margin-bottom: 0;
}
</style>
