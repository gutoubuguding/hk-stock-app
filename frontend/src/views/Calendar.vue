<template>
  <div class="calendar-page">
    <section class="page-heading">
      <div>
        <div class="eyebrow">CORPORATE EVENTS</div>
        <h2>财报/分红日历</h2>
        <p>跟踪港股即将公布的业绩、分红除净和派息安排。</p>
      </div>
      <div class="actions">
        <el-select v-model="days" style="width: 132px" @change="loadAll">
          <el-option label="未来30天" :value="30" />
          <el-option label="未来60天" :value="60" />
          <el-option label="未来90天" :value="90" />
          <el-option label="未来180天" :value="180" />
        </el-select>
        <el-button type="primary" :loading="loading" @click="loadAll">刷新</el-button>
      </div>
    </section>

    <el-row :gutter="16" class="summary-row">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="即将发布财报" :value="financialList.length" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="即将除净/派息" :value="dividendList.length" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="时间范围" :value="days" suffix="天" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="content-card" shadow="never">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="即将发布财报" name="financial">
          <el-table
            :data="financialList"
            stripe
            v-loading="loading"
            empty-text="暂无未来财报数据，点击刷新重新同步"
            @row-click="(row) => goToStock(row.stockCode)"
          >
            <el-table-column prop="eventDate" label="发布日期" width="130" sortable />
            <el-table-column prop="stockCode" label="代码" width="110">
              <template #default="{ row }">
                <span class="clickable-code">{{ row.stockCode }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="stockName" label="名称" min-width="260" show-overflow-tooltip />
            <el-table-column prop="financialReportType" label="报告类型" min-width="220" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag type="primary" effect="light">{{ row.financialReportType || '--' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="即将除净/派息" name="dividend">
          <el-table
            :data="dividendList"
            stripe
            v-loading="loading"
            empty-text="暂无未来分红数据，点击刷新重新同步"
            @row-click="(row) => goToStock(row.stockCode)"
          >
            <el-table-column prop="eventDate" label="除净/事件日" width="130" sortable />
            <el-table-column prop="stockCode" label="代码" width="110">
              <template #default="{ row }">
                <span class="clickable-code">{{ row.stockCode }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="stockName" label="名称" min-width="240" show-overflow-tooltip />
            <el-table-column prop="dividendPerShare" label="每股派息" width="130">
              <template #default="{ row }">
                <span class="amount">{{ row.dividendPerShare != null ? row.dividendPerShare : '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="exDividendDate" label="除净日" width="120" />
            <el-table-column prop="paymentDate" label="派息日" width="120" />
            <el-table-column prop="financialReportType" label="说明" min-width="220" show-overflow-tooltip />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const activeTab = ref('financial')
const days = ref(60)
const financialList = ref([])
const dividendList = ref([])
const loading = ref(false)

async function loadAll() {
  loading.value = true
  try {
    const [financialRes, dividendRes] = await Promise.all([
      axios.get('/api/calendar/financial', { params: { days: days.value } }),
      axios.get('/api/calendar/dividend', { params: { days: days.value } })
    ])
    financialList.value = financialRes.data || []
    dividendList.value = dividendRes.data || []
  } catch (e) {
    console.error(e)
    ElMessage.error('日历数据加载失败，请检查后端服务或同步任务')
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)

const goToStock = (stockCode) => {
  if (stockCode) router.push(`/stock/${stockCode}`)
}
</script>

<style scoped>
.calendar-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-heading {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 24px 26px;
  border: 1px solid rgba(36, 107, 254, 0.12);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(234,241,255,0.9));
  box-shadow: var(--shadow);
}

.eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: var(--primary);
}

.calendar-page h2 {
  margin-bottom: 8px;
}

.page-heading p {
  color: var(--text-muted);
  line-height: 1.7;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.summary-row {
  row-gap: 16px;
}

.summary-card :deep(.el-card__body) {
  padding: 18px 20px !important;
}

.content-card :deep(.el-card__body) {
  padding-top: 14px !important;
}

.clickable-code {
  color: var(--primary);
  cursor: pointer;
  font-weight: 800;
}

.clickable-code:hover {
  text-decoration: underline;
}

.amount {
  font-weight: 800;
  color: var(--text-main);
}

:deep(.el-table tbody tr) {
  cursor: pointer;
}

@media (max-width: 768px) {
  .page-heading {
    flex-direction: column;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
