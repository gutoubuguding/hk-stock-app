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
        <el-form-item label="股票搜索">
          <el-select
            v-model="selectedStock"
            filterable
            remote
            reserve-keyword
            placeholder="输入股票代码或名称搜索"
            :remote-method="searchStocks"
            :loading="searchLoading"
            @change="onStockSelect"
            style="width: 250px"
          >
            <el-option
              v-for="item in stockOptions"
              :key="item.stockCode"
              :label="`${item.stockCode} ${item.stockName}`"
              :value="item.stockCode"
            />
          </el-select>
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
import request from '@/http/request'

const alerts = ref([])
const loading = ref(false)
const checking = ref(false)
let isLoading = false
const form = reactive({
  stockCode: '',
  stockName: '',
  alertType: 'ABOVE',
  targetPrice: null
})

// 股票搜索相关
const selectedStock = ref(null)
const stockOptions = ref([])
const searchLoading = ref(false)

let searchTimer = null
const searchStocks = (keyword) => {
  if (searchTimer) clearTimeout(searchTimer)
  if (!keyword || keyword.trim().length < 1) {
    stockOptions.value = []
    return
  }
  searchLoading.value = true
  searchTimer = setTimeout(async () => {
    try {
      const res = await request({ url: '/stock/search', params: { keyword: keyword.trim() } })
      stockOptions.value = (res.data || []).slice(0, 20)
    } catch (e) {
      console.error(e)
    }
    searchLoading.value = false
  }, 300)
}

const onStockSelect = (stockCode) => {
  const stock = stockOptions.value.find(s => s.stockCode === stockCode)
  if (stock) {
    form.stockCode = stock.stockCode
    form.stockName = stock.stockName
  }
}

onMounted(async () => {
  await loadAlerts()
  await checkAlerts(false)
  setInterval(() => checkAlerts(false), 60000)
})

const loadAlerts = async () => {
  if (isLoading) return
  isLoading = true
  loading.value = true
  try {
    const res = await request({ url: '/alert' })
    alerts.value = res.data || []
  } catch (e) { console.error(e) } finally {
    loading.value = false
    isLoading = false
  }
}

const addAlert = async () => {
  if (!form.stockCode || !form.targetPrice) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await request({ url: '/alert', method: 'POST', data: { ...form } })
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
    const res = await request({ url: '/alert/check', method: 'POST' })
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
    await request({ url: `/alert/${id}`, method: 'DELETE' })
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
