<template>
  <div class="stock-detail">
    <el-page-header @back="router.back()" :content="stockInfo?.stockName || '加载中...'" />

    <!-- 当日关键信息 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <span>当日关键信息</span>
      </template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="开盘价">{{ dailyInfo?.openPrice || '--' }}</el-descriptions-item>
        <el-descriptions-item label="收盘价">{{ dailyInfo?.closePrice || '--' }}</el-descriptions-item>
        <el-descriptions-item label="最高价">{{ dailyInfo?.highPrice || '--' }}</el-descriptions-item>
        <el-descriptions-item label="最低价">{{ dailyInfo?.lowPrice || '--' }}</el-descriptions-item>
        <el-descriptions-item label="成交量">{{ formatVolume(dailyInfo?.volume) }}</el-descriptions-item>
        <el-descriptions-item label="成交额">{{ formatTurnover(dailyInfo?.turnover) }}</el-descriptions-item>
        <el-descriptions-item label="涨跌幅">
          <span :class="dailyInfo?.changePercent > 0 ? 'up' : 'down'">
            {{ dailyInfo?.changePercent || '--' }}%
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="换手率">{{ dailyInfo?.turnoverRate || '--' }}%</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- K线图 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="kline-header">
          <span>K线图</span>
          <div class="kline-tools">
            <el-checkbox-group v-model="indicatorOptions" size="small" @change="renderChart">
              <el-checkbox-button value="MA5">MA5</el-checkbox-button>
              <el-checkbox-button value="MA20">MA20</el-checkbox-button>
              <el-checkbox-button value="MACD">MACD</el-checkbox-button>
              <el-checkbox-button value="RSI">RSI</el-checkbox-button>
              <el-checkbox-button value="BOLL">布林带</el-checkbox-button>
            </el-checkbox-group>
            <el-radio-group v-model="periodType" size="small" @change="loadKline">
              <el-radio-button value="D">日K</el-radio-button>
              <el-radio-button value="5D">5日</el-radio-button>
              <el-radio-button value="M">月K</el-radio-button>
              <el-radio-button value="Y">年K</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div ref="klineChart" style="height: 400px;"></div>
    </el-card>

    <!-- 估值指标 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <span>估值指标</span>
      </template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="PE（市盈率）">{{ valuation?.pe || '--' }}</el-descriptions-item>
        <el-descriptions-item label="PB（市净率）">{{ valuation?.pb || '--' }}</el-descriptions-item>
        <el-descriptions-item label="股息率">{{ valuation?.dividendYield || '--' }}%</el-descriptions-item>
        <el-descriptions-item label="总市值">{{ formatMarketCap(valuation?.marketCap) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 新闻AI分析 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="news-header">
          <span>新闻AI分析</span>
          <el-button type="primary" size="small" @click="analyzeNews" :loading="analyzing" :disabled="!stockInfoLoaded">
            开始分析
          </el-button>
        </div>
      </template>
      <div v-if="newsList.length > 0" class="news-list">
        <div v-for="(item, index) in newsList" :key="index" class="news-item">
          <div class="news-item-title">
            <a v-if="item.link" :href="item.link" target="_blank">{{ item.title }}</a>
            <span v-else>{{ item.title }}</span>
          </div>
          <div class="news-item-meta">
            <span v-if="item.source">{{ item.source }}</span>
            <span v-if="item.date"> · {{ item.date }}</span>
          </div>
          <div class="news-item-content">{{ item.content }}</div>
        </div>
      </div>
      <div v-if="newsAnalysis" class="news-analysis">
        <el-divider v-if="newsList.length > 0" content-position="left">AI 分析结果</el-divider>
        <pre>{{ newsAnalysis }}</pre>
      </div>
      <div v-if="!newsAnalysis && newsList.length === 0" class="empty-text">点击"开始分析"获取AI新闻分析</div>
    </el-card>

    <!-- AI对话 -->
    <el-card v-if="newsAnalysis" shadow="hover" style="margin-top: 20px;">
      <template #header>
        <span>💬 与AI分析师对话</span>
      </template>
      <div class="chat-container">
        <div ref="chatBox" class="chat-messages">
          <div v-if="chatMessages.length === 0" class="chat-hint">
            针对上面的新闻分析，你可以向AI提问，比如："回购对股价有什么影响？"、"SU7销量预期如何？"
          </div>
          <div v-for="(msg, i) in chatMessages" :key="i" :class="['chat-msg', msg.role]">
            <div class="chat-avatar">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
            <div class="chat-bubble"><pre>{{ msg.content }}</pre></div>
          </div>
          <div v-if="chatLoading" class="chat-msg assistant">
            <div class="chat-avatar">AI</div>
            <div class="chat-bubble typing">思考中...</div>
          </div>
        </div>
        <div class="chat-input-bar">
          <el-input
            v-model="chatInput"
            placeholder="输入你的问题..."
            @keyup.enter="sendChat"
            :disabled="chatLoading"
            clearable
          />
          <el-button type="primary" @click="sendChat" :loading="chatLoading" :disabled="!chatInput.trim()">
            发送
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 股票对比 -->
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <span>股票对比</span>
      </template>
      <el-input v-model="compareCodes" placeholder="输入股票代码，逗号分隔（如：09988,03690）" style="margin-bottom: 10px;" />
      <el-button type="primary" @click="compareStocks">对比</el-button>
      <el-table v-if="compareRows.length" :data="compareRows" stripe style="margin-top: 14px;">
        <el-table-column prop="stockCode" label="代码" width="100" />
        <el-table-column prop="stockName" label="名称" min-width="160" />
        <el-table-column prop="closePrice" label="最新收盘" width="110" />
        <el-table-column prop="changePercent" label="涨跌幅" width="110">
          <template #default="{ row }">
            <span :class="row.changePercent > 0 ? 'up' : row.changePercent < 0 ? 'down' : ''">
              {{ row.changePercent != null ? row.changePercent + '%' : '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="120" />
        <el-table-column prop="marketCap" label="市值" width="130" />
        <el-table-column prop="pe" label="PE" width="90" />
        <el-table-column prop="pb" label="PB" width="90" />
        <el-table-column prop="dividendYield" label="股息率" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const stockCode = route.params.code

const stockInfo = ref(null)
const isIpoDetail = computed(() => route.query.source === 'ipo' || stockInfo.value?.isIpo)
const stockInfoLoaded = ref(false)
const dailyInfo = ref(null)
const valuation = ref(null)
const periodType = ref('D')
const indicatorOptions = ref(['MA5', 'MA20'])
const klineChart = ref(null)
const klineData = ref([])
const newsAnalysis = ref(null)
const newsList = ref([])
const analyzing = ref(false)
const compareCodes = ref('')
const compareResult = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatBox = ref(null)

let chartInstance = null

onMounted(async () => {
  await loadStockInfo()
  await loadDailyInfo()
  await loadValuation()
  await loadKline()
})

const loadStockInfo = async () => {
  try {
    const res = await axios.get('/api/stock/search', { params: { keyword: stockCode } })
    if (res.data.length > 0) {
      stockInfo.value = res.data[0]
    } else {
      await loadIpoFallbackInfo()
    }
  } catch (e) {
    console.error(e)
    await loadIpoFallbackInfo()
  } finally {
    // 即使普通股票表查不到，也允许 IPO 详情继续使用“开始分析”
    stockInfoLoaded.value = true
  }
}

const loadIpoFallbackInfo = async () => {
  const queryName = route.query.name ? String(route.query.name) : ''
  if (queryName) {
    stockInfo.value = { stockCode, stockName: queryName, isIpo: true }
    return
  }
  try {
    const res = await axios.get('/api/ipo/comparison', { params: { sortBy: 'listingDate', sortOrder: 'desc' } })
    const ipo = (res.data.data || []).find(item => item.stockCode === stockCode)
    if (ipo) stockInfo.value = { stockCode: ipo.stockCode, stockName: ipo.stockName, isIpo: true }
  } catch (e) {
    console.error(e)
  }
  if (!stockInfo.value) stockInfo.value = { stockCode, stockName: stockCode }
}

const loadDailyInfo = async () => {
  try {
    const res = await axios.get('/api/stock/daily-info', { params: { stockCode } })
    dailyInfo.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const loadValuation = async () => {
  try {
    const res = await axios.get('/api/stock/valuation', { params: { stockCode } })
    valuation.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const loadKline = async () => {
  try {
    const daysMap = { 'D': 120, '5D': 5, 'M': 36, 'Y': 10 }
    const res = await axios.get('/api/stock/kline', {
      params: { stockCode, periodType: periodType.value, days: daysMap[periodType.value] || 120 }
    })
    klineData.value = res.data
    renderChart()
  } catch (e) {
    console.error(e)
  }
}

const renderChart = () => {
  if (!klineChart.value) return
  if (chartInstance) chartInstance.dispose()

  chartInstance = echarts.init(klineChart.value)
  const dates = klineData.value.map(d => d.tradeDate)
  const closes = klineData.value.map(d => Number(d.closePrice))
  const values = klineData.value.map(d => [d.openPrice, d.closePrice, d.lowPrice, d.highPrice])
  const volumes = klineData.value.map(d => d.volume)
  const selected = indicatorOptions.value
  const series = [
    { name: 'K线', type: 'candlestick', data: values, xAxisIndex: 0, yAxisIndex: 0 },
    { name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1, itemStyle: { color: '#91cc75' } }
  ]

  if (selected.includes('MA5')) series.push({ name: 'MA5', type: 'line', data: calcMA(5, closes), smooth: true, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0 })
  if (selected.includes('MA20')) series.push({ name: 'MA20', type: 'line', data: calcMA(20, closes), smooth: true, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0 })
  if (selected.includes('BOLL')) {
    const boll = calcBOLL(20, closes)
    series.push({ name: 'BOLL上轨', type: 'line', data: boll.upper, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { type: 'dashed' } })
    series.push({ name: 'BOLL中轨', type: 'line', data: boll.mid, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { type: 'dashed' } })
    series.push({ name: 'BOLL下轨', type: 'line', data: boll.lower, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0, lineStyle: { type: 'dashed' } })
  }
  if (selected.includes('MACD')) {
    const macd = calcMACD(closes)
    series.push({ name: 'MACD', type: 'bar', data: macd.macd, xAxisIndex: 2, yAxisIndex: 2, itemStyle: { color: p => p.value >= 0 ? '#f56c6c' : '#67c23a' } })
    series.push({ name: 'DIF', type: 'line', data: macd.dif, showSymbol: false, xAxisIndex: 2, yAxisIndex: 2 })
    series.push({ name: 'DEA', type: 'line', data: macd.dea, showSymbol: false, xAxisIndex: 2, yAxisIndex: 2 })
  }
  if (selected.includes('RSI')) {
    series.push({ name: 'RSI6', type: 'line', data: calcRSI(6, closes), showSymbol: false, xAxisIndex: 2, yAxisIndex: 2 })
  }

  chartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { top: 0 },
    grid: [
      { left: '8%', right: '8%', top: '10%', height: selected.includes('MACD') || selected.includes('RSI') ? '42%' : '52%' },
      { left: '8%', right: '8%', top: selected.includes('MACD') || selected.includes('RSI') ? '58%' : '70%', height: '16%' },
      { left: '8%', right: '8%', top: '78%', height: '16%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0 },
      { type: 'category', data: dates, gridIndex: 1 },
      { type: 'category', data: dates, gridIndex: 2 }
    ],
    yAxis: [{ scale: true, gridIndex: 0 }, { scale: true, gridIndex: 1 }, { scale: true, gridIndex: 2 }],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1, 2] }],
    series
  })
}

const calcMA = (day, data) => data.map((_, i) => i < day - 1 ? null : +(data.slice(i - day + 1, i + 1).reduce((a, b) => a + b, 0) / day).toFixed(2))
const ema = (data, n) => data.reduce((arr, val, i) => { arr.push(i === 0 ? val : (val * 2 + arr[i - 1] * (n - 1)) / (n + 1)); return arr }, [])
const calcMACD = (data) => {
  const dif = ema(data, 12).map((v, i) => v - ema(data, 26)[i])
  const dea = ema(dif, 9)
  return { dif: dif.map(v => +v.toFixed(3)), dea: dea.map(v => +v.toFixed(3)), macd: dif.map((v, i) => +((v - dea[i]) * 2).toFixed(3)) }
}
const calcRSI = (day, data) => data.map((_, i) => {
  if (i < day) return null
  let up = 0, down = 0
  for (let j = i - day + 1; j <= i; j++) { const diff = data[j] - data[j - 1]; diff >= 0 ? up += diff : down -= diff }
  return down === 0 ? 100 : +(100 - 100 / (1 + up / down)).toFixed(2)
})
const calcBOLL = (day, data) => {
  const mid = calcMA(day, data)
  const upper = [], lower = []
  data.forEach((_, i) => {
    if (i < day - 1) { upper.push(null); lower.push(null); return }
    const slice = data.slice(i - day + 1, i + 1)
    const avg = mid[i]
    const sd = Math.sqrt(slice.reduce((s, v) => s + Math.pow(v - avg, 2), 0) / day)
    upper.push(+(avg + 2 * sd).toFixed(2)); lower.push(+(avg - 2 * sd).toFixed(2))
  })
  return { mid, upper, lower }
}

const analyzeNews = async () => {
  if (!stockInfoLoaded.value) return
  analyzing.value = true
  try {
    // 从后端获取当前配置的API Key
    const configRes = await axios.get('/api/config/current')
    const config = configRes.data
    
    // 等待stockInfo加载完成（双重保护）
    if (!stockInfo.value) {
      await loadStockInfo()
    }
    
    const currentStockName = stockInfo.value?.stockName || ''
    const currentStockCode = stockInfo.value?.stockCode || stockCode
    
    let res
    if (isIpoDetail.value) {
      // 从 IPO 列表进入的详情页，使用新股专用分析接口。
      // 普通新闻接口对刚上市/未进入 stock_info 的新股容易查不到名称或走错分析逻辑。
      res = await axios.get(`/api/ipo/ai-analysis/${currentStockCode}`)
    } else {
      // 调用AI服务分析新闻 - 使用公司名称+股票代码双重搜索确保相关性
      res = await axios.get('/api/analyze/stock-news', {
        params: {
          stock_code: currentStockCode,
          stock_name: currentStockName,
          days: 7,
          api_key: config.ai_api_key || '',
          base_url: config.ai_base_url || '',
          model: config.ai_model || ''
        }
      })
    }

    newsAnalysis.value = res.data.analysis || '分析完成'
    newsList.value = res.data.news || []
  } catch (e) {
    newsAnalysis.value = '分析失败: ' + (e.response?.data?.detail || e.message)
  }
  analyzing.value = false
}

const sendChat = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return
  
  const userMsg = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  chatLoading.value = true
  
  // 滚动到底部
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
  
  try {
    const configRes = await axios.get('/api/config/current')
    const config = configRes.data
    
    const res = await axios.post('/api/analyze/stock-chat', {
      stock_code: stockCode,
      stock_name: stockInfo.value?.stockName || '',
      news_context: newsList.value,
      chat_history: chatMessages.value,
      message: userMsg,
      api_key: config.ai_api_key || '',
      base_url: config.ai_base_url || '',
      model: config.ai_model || ''
    })
    
    chatMessages.value.push({ role: 'assistant', content: res.data.reply || '无法获取回复' })
  } catch (e) {
    chatMessages.value.push({ role: 'assistant', content: 'AI调用失败: ' + (e.response?.data?.detail || e.message) })
  }
  
  chatLoading.value = false
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

const compareRows = computed(() => {
  if (!compareResult.value) return []
  return Object.entries(compareResult.value).map(([code, data]) => ({
    stockCode: code,
    stockName: data.info?.stockName || '--',
    closePrice: data.latest?.closePrice ?? '--',
    changePercent: data.latest?.changePercent ?? null,
    volume: formatVolume(data.latest?.volume),
    marketCap: formatMarketCap(data.valuation?.marketCap),
    pe: data.valuation?.pe ?? '--',
    pb: data.valuation?.pb ?? '--',
    dividendYield: data.valuation?.dividendYield != null ? data.valuation.dividendYield + '%' : '--'
  }))
})

const compareStocks = async () => {
  if (!compareCodes.value.trim()) return
  try {
    const res = await axios.get('/api/compare', {
      params: { stockCodes: stockCode + ',' + compareCodes.value }
    })
    compareResult.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const formatVolume = (v) => v ? (v / 10000).toFixed(2) + '万' : '--'
const formatTurnover = (v) => v ? (v / 1e8).toFixed(2) + '亿' : '--'
const formatMarketCap = (v) => v ? (v / 1e8).toFixed(2) + '亿' : '--'
</script>

<style scoped>
.stock-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.kline-header, .news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.kline-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.up { color: #f56c6c; }
.down { color: #67c23a; }

.news-analysis pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  line-height: 1.8;
}

.news-list {
  margin-bottom: 10px;
}

.news-item {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.news-item:last-child {
  border-bottom: none;
}

.news-item-title a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
}

.news-item-title a:hover {
  text-decoration: underline;
}

.news-item-title span {
  font-weight: 500;
  font-size: 15px;
}

.news-item-meta {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.news-item-content {
  color: #606266;
  font-size: 13px;
  margin-top: 6px;
  line-height: 1.6;
}

.empty-text {
  color: #909399;
  text-align: center;
  padding: 20px;
}

.chat-container {
  display: flex;
  flex-direction: column;
}

.chat-messages {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
}

.chat-hint {
  color: #909399;
  font-size: 13px;
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.chat-msg {
  display: flex;
  margin-bottom: 12px;
  gap: 10px;
}

.chat-msg.user {
  flex-direction: row-reverse;
}

.chat-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.chat-msg.user .chat-avatar {
  background: #409eff;
  color: #fff;
}

.chat-msg.assistant .chat-avatar {
  background: #67c23a;
  color: #fff;
}

.chat-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.chat-bubble pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
}

.chat-msg.user .chat-bubble {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-msg.assistant .chat-bubble {
  background: #f0f2f5;
  color: #303133;
  border-bottom-left-radius: 4px;
}

.chat-bubble.typing {
  color: #909399;
  font-style: italic;
}

.chat-input-bar {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.chat-input-bar .el-input {
  flex: 1;
}
</style>
