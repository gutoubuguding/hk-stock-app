<template>
  <div class="ipo-page">
    <section class="page-heading">
      <div>
        <div class="eyebrow">IPO INTELLIGENCE</div>
        <h2>新股AI分析</h2>
        <p>把招股、上市后表现、板块统计和破发率放在一个更清爽的工作台里。</p>
      </div>
    </section>

    <el-card class="content-card" shadow="never">
      <el-tabs v-model="activeTab" class="ipo-tabs">
      <!-- 即将上市新股 -->
      <el-tab-pane label="即将上市" name="upcoming">
        <el-table :data="upcomingList" stripe v-loading="loadingUpcoming" @row-click="goToStock">
          <el-table-column prop="stockCode" label="代码" width="100">
            <template #default="{ row }">
              <span class="clickable-code">{{ row.stockCode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stockName" label="名称" width="150">
            <template #default="{ row }">
              <span class="clickable-name">{{ row.stockName }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="listingDate" label="上市日" width="120" />
          <el-table-column prop="subscriptionStart" label="招股开始" width="120" />
          <el-table-column prop="subscriptionEnd" label="招股结束" width="120" />
          <el-table-column prop="issuePrice" label="发行价" width="100" />
          <el-table-column prop="entryFee" label="入场费" width="120" />
          <el-table-column label="AI分析" width="120">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click.stop="analyzeIpo(row)">分析</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 新股对比表格 -->
      <el-tab-pane label="近一年新股对比" name="comparison">
        <div class="table-toolbar">
          <el-select v-model="sortBy" placeholder="排序字段" @change="loadComparison">
            <el-option label="上市时间" value="listingDate" />
            <el-option label="首日涨幅" value="firstDayChange" />
            <el-option label="7天涨幅" value="sevenDayChange" />
            <el-option label="30天涨幅" value="thirtyDayChange" />
            <el-option label="中签率" value="allotmentRate" />
          </el-select>
          <el-select v-model="sortOrder" placeholder="排序方式" @change="loadComparison">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </div>

        <el-table :data="comparisonData" stripe v-loading="loadingComparison" max-height="600" @row-click="goToStock">
          <el-table-column prop="stockCode" label="代码" width="100" fixed>
            <template #default="{ row }">
              <span class="clickable-code">{{ row.stockCode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stockName" label="名称" width="120" fixed>
            <template #default="{ row }">
              <span class="clickable-name">{{ row.stockName }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="listingDate" label="上市日" width="110" sortable />
          <el-table-column prop="issuePrice" label="发行价" width="90">
            <template #default="{ row }">
              <span>{{ row.issuePrice != null ? row.issuePrice : '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="currentChange" label="现价涨跌%" width="100" sortable>
            <template #default="{ row }">
              <span :class="row.currentChange > 0 ? 'up' : row.currentChange < 0 ? 'down' : ''">{{ row.currentChange != null ? row.currentChange + '%' : '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="firstDayChange" label="首日%" width="90" sortable>
            <template #default="{ row }">
              <span v-if="!row.issuePrice && row.firstDayChange == 100" class="empty-cell">--</span>
              <span v-else-if="row.firstDayChange != null" :class="row.firstDayChange > 0 ? 'up' : row.firstDayChange < 0 ? 'down' : ''">{{ row.firstDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="sevenDayChange" label="7天%" width="80" sortable>
            <template #default="{ row }">
              <span v-if="row.sevenDayChange != null" :class="row.sevenDayChange > 0 ? 'up' : row.sevenDayChange < 0 ? 'down' : ''">{{ row.sevenDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="thirtyDayChange" label="30天%" width="85" sortable>
            <template #default="{ row }">
              <span v-if="row.thirtyDayChange != null" :class="row.thirtyDayChange > 0 ? 'up' : row.thirtyDayChange < 0 ? 'down' : ''">{{ row.thirtyDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="allotmentRate" label="中签率%" width="95" sortable>
            <template #default="{ row }">{{ formatNullable(row.allotmentRate, '%') }}</template>
          </el-table-column>
          <el-table-column prop="oversubscriptionRatio" label="超购倍数" width="100" sortable>
            <template #default="{ row }">{{ formatNullable(row.oversubscriptionRatio, 'x') }}</template>
          </el-table-column>
          <el-table-column prop="publicOfferingRatio" label="公开发售%" width="110">
            <template #default="{ row }">{{ formatNullable(row.publicOfferingRatio, '%') }}</template>
          </el-table-column>
          <el-table-column prop="internationalPlacementRatio" label="国际配售%" width="110">
            <template #default="{ row }">{{ formatNullable(row.internationalPlacementRatio, '%') }}</template>
          </el-table-column>
          <el-table-column prop="entryFee" label="入场费" width="100">
            <template #default="{ row }">{{ formatNullable(row.entryFee) }}</template>
          </el-table-column>
          <el-table-column prop="fundraisingAmount" label="募资额" width="100">
            <template #default="{ row }">{{ formatNullable(row.fundraisingAmount) }}</template>
          </el-table-column>
          <el-table-column prop="sector" label="板块" width="120" />
          <el-table-column prop="sponsor" label="保荐人" width="150" />
          <el-table-column prop="cornerstoneInvestor" label="基石投资者" width="150" />
          <el-table-column prop="issuePE" label="发行PE" width="90" />
          <el-table-column prop="industryAvgPE" label="行业PE" width="90" />
          <el-table-column prop="isHkStockConnect" label="港股通" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.isHkStockConnect" type="success" size="small">是</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 板块统计 -->
      <el-tab-pane label="板块统计" name="sector">
        <div v-if="sectorStats && sectorStats.stats && sectorStats.stats.length > 0">
          <div class="sector-summary">
            <el-statistic title="有效板块数" :value="sectorStats.totalSectors" />
            <el-statistic title="新股总数" :value="sectorStats.total" />
          </div>
          <el-table :data="sectorStats.stats" stripe style="margin-top: 16px;" @row-click="onSectorClick" cursor="pointer">
            <el-table-column prop="sector" label="行业板块" min-width="180">
              <template #default="{ row }">
                <span class="clickable-sector">{{ row.sector }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="新股数量" width="100" sortable />
            <el-table-column prop="avgFirstDayChange" label="平均首日涨幅%" width="130" sortable>
              <template #default="{ row }">
                <span :class="row.avgFirstDayChange > 0 ? 'up' : 'down'">
                  {{ row.avgFirstDayChange != null ? row.avgFirstDayChange + '%' : '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="avgSevenDayChange" label="平均7天涨幅%" width="130" sortable>
              <template #default="{ row }">
                <span :class="row.avgSevenDayChange > 0 ? 'up' : 'down'">
                  {{ row.avgSevenDayChange != null ? row.avgSevenDayChange + '%' : '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="breakRate" label="破发率" width="100" sortable>
              <template #default="{ row }">
                <span :class="row.breakRate > 30 ? 'down' : row.breakRate > 15 ? 'warn' : ''">
                  {{ row.breakRate != null ? row.breakRate + '%' : '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="brokenCount" label="破发数量" width="100" />
          </el-table>
          <div class="sector-hint">
            点击板块名称查看该板块下的所有公司；已过滤样本数少于 {{ sectorStats.minSectorSampleSize || 3 }} 只的低参考性板块
            <span v-if="sectorStats.hiddenSmallSectors">（隐藏 {{ sectorStats.hiddenSmallSectors }} 个小板块 / {{ sectorStats.hiddenSmallSectorStocks }} 只股票）</span>
          </div>
        </div>
        <div v-else-if="sectorStats" class="empty-text">暂无板块统计数据</div>
        <div v-else class="empty-text">加载中...</div>
      </el-tab-pane>

      <!-- 破发率 -->
      <el-tab-pane label="破发率统计" name="breakRate">
        <div v-if="breakRateData" class="break-rate">
          <el-statistic title="近一年新股总数" :value="breakRateData.total" />
          <el-statistic title="破发数量" :value="breakRateData.brokenCount" />
          <el-statistic title="破发率" :value="breakRateData.breakRate" suffix="%" />
        </div>
      </el-tab-pane>
      </el-tabs>
    </el-card>

    <!--
      AI 分析弹窗
      - analysisFullscreen 控制“放大界面 / 还原窗口”
      - analysis-layout 使用左右两栏：左侧公司信息/新闻，右侧 AI 报告
      - 两栏都在 CSS 里设置了独立滚动，避免拖动报告时整个弹窗一起滚动
    -->
    <el-dialog
      v-model="showAnalysis"
      width="min(1120px, 92vw)"
      class="analysis-dialog"
      :fullscreen="analysisFullscreen"
      :show-close="true"
      destroy-on-close
    >
      <template #header>
        <div class="analysis-dialog-title">
          <div>
            <div class="eyebrow">IPO AI REPORT</div>
            <h3>{{ selectedIpo?.stockName || '新股 AI 分析' }}</h3>
            <p>{{ selectedIpo?.stockCode || '--' }} · 基于最新新闻和上市表现生成</p>
          </div>
          <div class="analysis-title-actions">
            <el-tag v-if="ipoAnalysisResult?.llm_provider" type="success" effect="light">
              {{ ipoAnalysisResult.llm_provider }} / {{ ipoAnalysisResult.model }}
            </el-tag>
            <el-button size="small" plain @click="analysisFullscreen = !analysisFullscreen">
              {{ analysisFullscreen ? '还原窗口' : '放大界面' }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!ipoAnalysis" class="analysis-loading">
        <div class="loading-orb"></div>
        <div>
          <h4>AI 正在读取新闻并生成报告...</h4>
          <p>这一步可能需要几十秒，尤其是长报告输出时。</p>
        </div>
      </div>

      <div v-else class="analysis-layout">
        <aside class="analysis-side">
          <div class="side-card main-meta">
            <div class="meta-code">{{ selectedIpo?.stockCode }}</div>
            <div class="meta-name">{{ selectedIpo?.stockName }}</div>
            <div class="meta-row">
              <span>上市日</span>
              <strong>{{ selectedIpo?.listingDate || '--' }}</strong>
            </div>
            <div class="meta-row">
              <span>发行价</span>
              <strong>{{ selectedIpo?.issuePrice ?? '--' }}</strong>
            </div>
            <div class="meta-row">
              <span>首日涨幅</span>
              <strong :class="selectedIpo?.firstDayChange > 0 ? 'up' : selectedIpo?.firstDayChange < 0 ? 'down' : ''">
                {{ selectedIpo?.firstDayChange != null ? selectedIpo.firstDayChange + '%' : '--' }}
              </strong>
            </div>
          </div>

          <div class="side-card">
            <div class="side-title">相关新闻</div>
            <div v-if="ipoNewsList.length" class="news-cards">
              <a
                v-for="(news, index) in ipoNewsList"
                :key="index"
                class="news-card"
                :href="news.link || undefined"
                target="_blank"
              >
                <span class="news-index">{{ index + 1 }}</span>
                <div>
                  <div class="news-title">{{ news.title }}</div>
                  <div class="news-meta">{{ news.source || '新闻源' }} · {{ news.date || '未知日期' }}</div>
                </div>
              </a>
            </div>
            <div v-else class="empty-mini">暂无新闻列表</div>
          </div>
        </aside>

        <main class="analysis-main">
          <div class="report-toolbar">
            <div>
              <div class="report-kicker">AI 分析结果</div>
              <h4>上市走势研判</h4>
            </div>
            <el-button size="small" @click="copyAnalysis">复制报告</el-button>
          </div>
          <div class="report-body">
            <div v-if="ipoStructuredAnalysis" class="structured-report">
              <div class="rating-card">
                <div>
                  <div class="rating-label">AI 综合评级</div>
                  <div class="rating-value">{{ ipoStructuredAnalysis.suggestion || '--' }}</div>
                </div>
                <el-tag size="large" :type="riskTagType(ipoStructuredAnalysis.riskLevel)">
                  风险等级：{{ ipoStructuredAnalysis.riskLevel || '未知' }}
                </el-tag>
              </div>

              <div class="confidence-row">
                <span>AI 置信度</span>
                <el-progress :percentage="confidencePercent(ipoStructuredAnalysis.confidence)" :stroke-width="10" />
              </div>

              <section class="analysis-section">
                <h5>整体评价</h5>
                <p>{{ ipoStructuredAnalysis.summary || '--' }}</p>
              </section>

              <section class="analysis-section two-cols">
                <div>
                  <h5>核心优势</h5>
                  <ul>
                    <li v-for="(item, index) in ipoStructuredAnalysis.advantages || []" :key="'adv-' + index">{{ item }}</li>
                    <li v-if="!(ipoStructuredAnalysis.advantages || []).length" class="empty-mini">暂无</li>
                  </ul>
                </div>
                <div>
                  <h5>主要风险</h5>
                  <ul>
                    <li v-for="(item, index) in ipoStructuredAnalysis.risks || []" :key="'risk-' + index">{{ item }}</li>
                    <li v-if="!(ipoStructuredAnalysis.risks || []).length" class="empty-mini">暂无</li>
                  </ul>
                </div>
              </section>
            </div>
            <pre v-else>{{ ipoAnalysis }}</pre>
          </div>
        </main>
      </div>
    </el-dialog>

    <!-- 板块公司列表弹窗 -->
    <el-dialog v-model="sectorDialogVisible" :title="'板块: ' + selectedSector" width="900px">
      <div v-if="sectorIpos.length > 0">
        <el-table :data="sectorIpos" stripe>
          <el-table-column prop="stockCode" label="股票代码" width="100">
            <template #default="{ row }">
              <span class="clickable-code" @click.stop="goToStock(row)">{{ row.stockCode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stockName" label="公司名称" min-width="150">
            <template #default="{ row }">
              <span class="clickable-name" @click.stop="goToStock(row)">{{ row.stockName }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="listingDate" label="上市日期" width="110" />
          <el-table-column prop="issuePrice" label="发行价" width="90">
            <template #default="{ row }">
              <span>{{ row.issuePrice != null ? row.issuePrice : '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="firstDayChange" label="首日%" width="90">
            <template #default="{ row }">
              <span v-if="row.issuePrice && row.firstDayChange == 100" class="empty-cell">--</span>
              <span v-else-if="row.firstDayChange != null" :class="row.firstDayChange > 0 ? 'up' : row.firstDayChange < 0 ? 'down' : ''">{{ row.firstDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="sevenDayChange" label="7天%" width="80">
            <template #default="{ row }">
              <span v-if="row.sevenDayChange != null" :class="row.sevenDayChange > 0 ? 'up' : 'down'">{{ row.sevenDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="thirtyDayChange" label="30天%" width="85">
            <template #default="{ row }">
              <span v-if="row.thirtyDayChange != null" :class="row.thirtyDayChange > 0 ? 'up' : 'down'">{{ row.thirtyDayChange }}%</span>
              <span v-else class="empty-cell">--</span>
            </template>
          </el-table-column>
          <el-table-column prop="allotmentRate" label="中签率%" width="95" />
        </el-table>
      </div>
      <div v-else class="empty-text">该板块暂无新股数据</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const activeTab = ref('upcoming')
const upcomingList = ref([])
const comparisonData = ref([])
const sectorStats = ref(null)
const breakRateData = ref(null)
const sortBy = ref('listingDate')
const sortOrder = ref('desc')
const loadingUpcoming = ref(false)
const loadingComparison = ref(false)
const showAnalysis = ref(false)
const analysisFullscreen = ref(false)
const ipoAnalysis = ref(null)
const ipoStructuredAnalysis = ref(null)
const ipoAnalysisResult = ref(null)
const ipoNewsList = ref([])
const selectedIpo = ref(null)
const sectorDialogVisible = ref(false)
const selectedSector = ref('')
const sectorIpos = ref([])

onMounted(async () => {
  await loadUpcoming()
  await loadComparison()
  await loadSectorStats()
  await loadBreakRate()
})

const unwrapApiResponse = (res) => res.data?.data ?? res.data
const formatNullable = (value, suffix = '') => value == null || value === '' ? '待公布' : `${value}${suffix}`

const loadUpcoming = async () => {
  loadingUpcoming.value = true
  try {
    const res = await axios.get('/api/ipo/upcoming')
    upcomingList.value = unwrapApiResponse(res) || []
  } catch (e) { console.error(e) }
  loadingUpcoming.value = false
}

const loadComparison = async () => {
  loadingComparison.value = true
  try {
    const res = await axios.get('/api/ipo/comparison', {
      params: { sortBy: sortBy.value, sortOrder: sortOrder.value }
    })
    comparisonData.value = unwrapApiResponse(res)?.data || []
  } catch (e) { console.error(e) }
  loadingComparison.value = false
}

const loadSectorStats = async () => {
  try {
    const res = await axios.get('/api/ipo/sector-stats')
    sectorStats.value = unwrapApiResponse(res)
  } catch (e) { console.error(e) }
}

const loadBreakRate = async () => {
  try {
    const res = await axios.get('/api/ipo/break-rate')
    breakRateData.value = unwrapApiResponse(res)
  } catch (e) { console.error(e) }
}

const goToStock = (rowOrCode) => {
  const stockCode = typeof rowOrCode === 'string' ? rowOrCode : rowOrCode?.stockCode
  const stockName = typeof rowOrCode === 'string' ? '' : rowOrCode?.stockName
  if (!stockCode) return
  router.push({ path: `/stock/${stockCode}`, query: { source: 'ipo', name: stockName || '' } })
}

// 点击“分析”按钮后的主流程：
// 1. 先打开弹窗并清空旧报告，给用户看到加载状态；
// 2. 请求后端 /api/ipo/ai-analysis/{stockCode}；
// 3. 后端会继续调用 Python AI 微服务生成分析结果。
const analyzeIpo = async (row) => {
  selectedIpo.value = row
  showAnalysis.value = true
  analysisFullscreen.value = false
  ipoAnalysis.value = null
  ipoStructuredAnalysis.value = null
  ipoAnalysisResult.value = null
  ipoNewsList.value = []
  try {
    const res = await axios.get(`/api/ipo/ai-analysis/${row.stockCode}`)
    const data = unwrapApiResponse(res) || {}
    ipoAnalysisResult.value = data
    ipoNewsList.value = data.news || []
    if (data.analysis && typeof data.analysis === 'object') {
      ipoStructuredAnalysis.value = data.analysis
      ipoAnalysis.value = formatStructuredAnalysis(data.analysis)
    } else {
      ipoStructuredAnalysis.value = null
      ipoAnalysis.value = data.analysis || '分析完成'
    }
  } catch (e) {
    ipoStructuredAnalysis.value = null
    ipoAnalysis.value = '分析失败: ' + e.message
  }
}

const formatStructuredAnalysis = (analysis) => {
  if (!analysis) return ''
  const advantages = (analysis.advantages || []).map(item => `- ${item}`).join('\n') || '- 暂无'
  const risks = (analysis.risks || []).map(item => `- ${item}`).join('\n') || '- 暂无'
  return [
    `AI 综合评级：${analysis.suggestion || '--'}`,
    `风险等级：${analysis.riskLevel || '未知'}`,
    `AI 置信度：${confidencePercent(analysis.confidence)}%`,
    `整体评价：${analysis.summary || '--'}`,
    `核心优势：\n${advantages}`,
    `主要风险：\n${risks}`
  ].join('\n\n')
}

const confidencePercent = (value) => {
  const numberValue = Number(value)
  if (Number.isNaN(numberValue)) return 0
  return Math.round(Math.max(0, Math.min(numberValue, 1)) * 100)
}

const riskTagType = (riskLevel) => {
  if (['高', '中高'].includes(riskLevel)) return 'danger'
  if (['中', '中低'].includes(riskLevel)) return 'warning'
  if (riskLevel === '低') return 'success'
  return 'info'
}

// 复制报告：用浏览器 Clipboard API，把右侧完整 AI 文本复制到剪贴板。
const copyAnalysis = async () => {
  if (!ipoAnalysis.value) return
  try {
    await navigator.clipboard.writeText(ipoAnalysis.value)
    ElMessage.success('报告已复制')
  } catch (e) {
    ElMessage.warning('复制失败，请手动选择文本复制')
  }
}

const onSectorClick = async (row) => {
  selectedSector.value = row.sector
  sectorDialogVisible.value = true
  sectorIpos.value = []
  try {
    const res = await axios.get('/api/ipo/sector', { params: { sector: row.sector } })
    sectorIpos.value = unwrapApiResponse(res)?.ipos || []
  } catch (e) {
    console.error('加载板块公司失败:', e)
  }
}
</script>

<style scoped>
.ipo-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-heading {
  padding: 24px 26px;
  border: 1px solid rgba(36, 107, 254, 0.12);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(234,241,255,0.9));
  box-shadow: var(--shadow);
}

.eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: var(--primary);
}

.ipo-page h2 {
  margin-bottom: 8px;
}

.page-heading p {
  color: var(--text-muted);
  line-height: 1.7;
}

.content-card :deep(.el-card__body) {
  padding-top: 14px !important;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px;
  border-radius: 16px;
  background: #f7f9fd;
}

.up { color: #f56c6c; }
.down { color: #67c23a; }
.warn { color: #e6a23c; }
.empty-cell { color: #c0c4cc; }

.sector-summary {
  display: flex;
  gap: 40px;
  padding: 16px 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.sector-hint {
  margin-top: 10px;
  color: #909399;
  font-size: 13px;
  text-align: center;
}

.clickable-sector {
  color: #409eff;
  cursor: pointer;
}

.clickable-sector:hover {
  text-decoration: underline;
}

.break-rate {
  display: flex;
  gap: 40px;
  padding: 20px;
}

:deep(.analysis-dialog .el-dialog) {
  border-radius: 26px;
  overflow: hidden;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 28%);
  max-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
}

:deep(.analysis-dialog .el-dialog.is-fullscreen) {
  width: 100vw !important;
  height: 100vh;
  max-height: none;
  margin: 0;
  border-radius: 0;
}

:deep(.analysis-dialog .el-dialog__header) {
  margin: 0;
  padding: 24px 28px 18px;
  border-bottom: 1px solid rgba(36, 107, 254, 0.1);
  background:
    radial-gradient(circle at 10% 0%, rgba(36, 107, 254, 0.18), transparent 32%),
    linear-gradient(135deg, rgba(255,255,255,0.95), rgba(235,242,255,0.9));
}

:deep(.analysis-dialog .el-dialog__body) {
  padding: 0;
  overflow: hidden;
  flex: 1;
  min-height: 0;
}

.analysis-dialog-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding-right: 44px;
}

.analysis-title-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.analysis-dialog-title h3 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #12223f;
}

.analysis-dialog-title p {
  margin: 0;
  color: var(--text-muted);
}

.analysis-loading {
  min-height: 380px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 22px;
  color: #2f3b52;
}

.analysis-loading h4 {
  margin: 0 0 8px;
  font-size: 18px;
}

.analysis-loading p {
  margin: 0;
  color: var(--text-muted);
}

.loading-orb {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, var(--primary), #7dd3fc, #a78bfa, var(--primary));
  animation: spin 1.2s linear infinite;
  box-shadow: 0 12px 32px rgba(36, 107, 254, 0.25);
}

.loading-orb::after {
  content: '';
  display: block;
  width: 36px;
  height: 36px;
  margin: 9px;
  border-radius: 50%;
  background: #fff;
}

@keyframes spin { to { transform: rotate(360deg); } }

.analysis-layout {
  display: grid;
  grid-template-columns: 330px minmax(0, 1fr);
  height: min(680px, calc(100vh - 188px));
  min-height: 460px;
  overflow: hidden;
}

:deep(.analysis-dialog .el-dialog.is-fullscreen) .analysis-layout {
  height: calc(100vh - 112px);
  min-height: 0;
  grid-template-columns: 380px minmax(0, 1fr);
}

.analysis-side {
  min-height: 0;
  padding: 22px;
  overflow-y: auto;
  overscroll-behavior: contain;
  border-right: 1px solid #edf1f7;
  background: #f7f9fd;
}

.side-card {
  padding: 18px;
  border: 1px solid #e7edf7;
  border-radius: 20px;
  background: rgba(255,255,255,0.92);
  box-shadow: 0 10px 28px rgba(27, 46, 94, 0.06);
}

.side-card + .side-card {
  margin-top: 16px;
}

.main-meta {
  background: linear-gradient(135deg, #10233f, #244b8f);
  color: #fff;
  border: 0;
}

.meta-code {
  font-size: 13px;
  opacity: 0.74;
  letter-spacing: 0.12em;
  font-weight: 800;
}

.meta-name {
  margin: 8px 0 18px;
  font-size: 22px;
  font-weight: 800;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid rgba(255,255,255,0.16);
}

.meta-row span {
  opacity: 0.7;
}

.side-title {
  margin-bottom: 12px;
  font-weight: 800;
  color: #1f2f4d;
}

.news-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.news-card {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  color: inherit;
  text-decoration: none;
  background: #f8fafc;
  border: 1px solid transparent;
  transition: all 0.18s ease;
}

.news-card:hover {
  border-color: rgba(36, 107, 254, 0.24);
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(27, 46, 94, 0.08);
}

.news-index {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(36, 107, 254, 0.1);
  color: var(--primary);
  font-weight: 800;
}

.news-title {
  font-size: 13px;
  line-height: 1.45;
  color: #1f2f4d;
}

.news-meta,
.empty-mini {
  margin-top: 6px;
  font-size: 12px;
  color: #8a96aa;
}

.analysis-main {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.report-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 28px;
  border-bottom: 1px solid #edf1f7;
}

.report-kicker {
  margin-bottom: 6px;
  color: var(--primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.report-toolbar h4 {
  margin: 0;
  font-size: 20px;
  color: #12223f;
}

.report-body {
  flex: 1;
  min-height: 0;
  padding: 26px 32px 34px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.report-body pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 15px;
  line-height: 1.9;
  color: #21314f;
}

.structured-report {
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #21314f;
}

.rating-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(36, 107, 254, 0.1), rgba(125, 211, 252, 0.18));
  border: 1px solid rgba(36, 107, 254, 0.14);
}

.rating-label {
  margin-bottom: 6px;
  color: #60708c;
  font-size: 13px;
  font-weight: 700;
}

.rating-value {
  font-size: 28px;
  font-weight: 900;
  color: #12223f;
}

.confidence-row {
  padding: 16px 18px;
  border: 1px solid #edf1f7;
  border-radius: 16px;
  background: #fbfcff;
}

.confidence-row span {
  display: block;
  margin-bottom: 10px;
  color: #60708c;
  font-weight: 800;
}

.analysis-section {
  padding: 18px 20px;
  border: 1px solid #edf1f7;
  border-radius: 18px;
  background: #fff;
}

.analysis-section h5 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #12223f;
}

.analysis-section p {
  margin: 0;
  line-height: 1.8;
}

.analysis-section ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.8;
}

.two-cols {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

@media (max-width: 860px) {
  .analysis-layout {
    grid-template-columns: 1fr;
    height: min(720px, calc(100vh - 176px));
    min-height: 0;
  }
  .analysis-side {
    max-height: 260px;
    border-right: 0;
    border-bottom: 1px solid #edf1f7;
  }
  .rating-card,
  .two-cols {
    grid-template-columns: 1fr;
  }
  .rating-card {
    align-items: flex-start;
    flex-direction: column;
  }
}

.empty-text {
  color: #909399;
  text-align: center;
  padding: 40px;
}

.clickable-code,
.clickable-name {
  color: #409eff;
  cursor: pointer;
}

.clickable-code:hover,
.clickable-name:hover {
  text-decoration: underline;
}

.el-table tbody tr {
  cursor: pointer;
}
</style>
