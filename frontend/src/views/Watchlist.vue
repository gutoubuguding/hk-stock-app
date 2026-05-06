<template>
  <div class="watchlist-page">
    <section class="page-heading">
      <div>
        <div class="eyebrow">WATCHLIST</div>
        <h2>自选股</h2>
        <p>集中查看关注股票的最新价格、涨跌幅和估值。</p>
      </div>
      <el-button type="primary" :loading="loading" @click="loadWatchlist">刷新行情</el-button>
    </section>

    <el-card shadow="never" class="content-card">
      <el-table :data="watchlist" stripe v-loading="loading" empty-text="暂无自选股，去搜索添加吧！">
        <el-table-column prop="stockCode" label="代码" width="110" />
        <el-table-column prop="stockName" label="名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="closePrice" label="最新收盘" width="110" />
        <el-table-column prop="changePercent" label="涨跌幅" width="110">
          <template #default="{ row }">
            <span :class="row.changePercent > 0 ? 'up' : row.changePercent < 0 ? 'down' : ''">
              {{ row.changePercent != null ? row.changePercent + '%' : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volumeText" label="成交量" width="120" />
        <el-table-column prop="turnoverText" label="成交额" width="120" />
        <el-table-column prop="pe" label="PE" width="90" />
        <el-table-column prop="pb" label="PB" width="90" />
        <el-table-column prop="marketCapText" label="市值" width="130" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToDetail(row.stockCode)">详情</el-button>
            <el-button size="small" type="danger" @click="removeStock(row.stockCode)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="watchlist.length === 0 && !loading" class="empty">
        <el-empty description="暂无自选股，去搜索添加吧！">
          <el-button type="primary" @click="router.push('/search')">去搜索</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const watchlist = ref([])
const loading = ref(true)

onMounted(loadWatchlist)

async function loadWatchlist() {
  loading.value = true
  try {
    const res = await axios.get('/api/watchlist')
    const rows = res.data || []
    watchlist.value = await Promise.all(rows.map(async row => {
      const [daily, valuation] = await Promise.all([
        axios.get('/api/stock/daily-info', { params: { stockCode: row.stockCode } }).then(r => r.data).catch(() => null),
        axios.get('/api/stock/valuation', { params: { stockCode: row.stockCode } }).then(r => r.data).catch(() => null)
      ])
      return {
        ...row,
        closePrice: daily?.closePrice ?? '--',
        changePercent: daily?.changePercent ?? null,
        volumeText: formatVolume(daily?.volume),
        turnoverText: formatTurnover(daily?.turnover),
        pe: valuation?.pe ?? '--',
        pb: valuation?.pb ?? '--',
        marketCapText: formatMarketCap(valuation?.marketCap)
      }
    }))
  } catch (e) {
    console.error(e)
    ElMessage.error('自选股加载失败')
  } finally {
    loading.value = false
  }
}

const goToDetail = (code) => {
  router.push(`/stock/${code}`)
}

const removeStock = async (code) => {
  try {
    await axios.delete(`/api/watchlist/${code}`)
    ElMessage.success('已删除')
    await loadWatchlist()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const formatVolume = (v) => v ? (v / 10000).toFixed(2) + '万' : '--'
const formatTurnover = (v) => v ? (v / 1e8).toFixed(2) + '亿' : '--'
const formatMarketCap = (v) => v ? (v / 1e8).toFixed(2) + '亿' : '--'
</script>

<style scoped>
.watchlist-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
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

.watchlist-page h2 {
  margin-bottom: 8px;
}

.page-heading p {
  color: var(--text-muted);
  line-height: 1.7;
}

.empty {
  margin-top: 40px;
}
</style>
