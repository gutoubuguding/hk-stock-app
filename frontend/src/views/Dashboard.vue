<template>
  <div class="dashboard">
    <section class="hero-card">
      <div>
        <div class="eyebrow">HK MARKET DASHBOARD</div>
        <h2>大盘概览</h2>
        <p>聚合恒指、科技指数、国企指数与市场广度，快速判断当日港股情绪。</p>
      </div>
      <div class="hero-badge" :class="sentimentTone">
        <span>市场情绪</span>
        <strong>{{ sentimentLabel }}</strong>
      </div>
    </section>

    <el-row :gutter="20" class="index-grid">
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card shadow="hover" class="metric-card index-card">
          <template #header>
            <span>恒生指数</span>
          </template>
          <div class="index-data">
            <div class="index-value">{{ marketData.hsi?.value || '--' }}</div>
            <div :class="['index-change', marketData.hsi?.change > 0 ? 'up' : 'down']">
              {{ marketData.hsi?.change || '--' }} ({{ marketData.hsi?.changePercent || '--' }}%)
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card shadow="hover" class="metric-card index-card tech">
          <template #header>
            <span>恒生科技指数</span>
          </template>
          <div class="index-data">
            <div class="index-value">{{ marketData.hstech?.value || '--' }}</div>
            <div :class="['index-change', marketData.hstech?.change > 0 ? 'up' : 'down']">
              {{ marketData.hstech?.change || '--' }} ({{ marketData.hstech?.changePercent || '--' }}%)
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8">
        <el-card shadow="hover" class="metric-card index-card hscei">
          <template #header>
            <span>国企指数</span>
          </template>
          <div class="index-data">
            <div class="index-value">{{ marketData.hscei?.value || '--' }}</div>
            <div :class="['index-change', marketData.hscei?.change > 0 ? 'up' : 'down']">
              {{ marketData.hscei?.change || '--' }} ({{ marketData.hscei?.changePercent || '--' }}%)
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="bottom-grid">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="metric-card">
          <template #header>
            <span>涨跌家数</span>
          </template>
          <div class="advance-decline">
            <div class="breadth-item advance">
              <span class="label">上涨</span>
              <span class="count up">{{ marketData.advance || '--' }}</span>
            </div>
            <div class="breadth-item decline">
              <span class="label">下跌</span>
              <span class="count down">{{ marketData.decline || '--' }}</span>
            </div>
            <div class="breadth-item flat">
              <span class="label">平盘</span>
              <span class="count">{{ marketData.flat || '--' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="metric-card">
          <template #header>
            <span>市场情绪</span>
          </template>
          <div class="market-sentiment">
            <el-progress
              :percentage="marketData.sentiment || 50"
              :stroke-width="14"
              :color="sentimentColor"
              :format="() => sentimentLabel"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const marketData = ref({
  hsi: null,
  hstech: null,
  hscei: null,
  advance: null,
  decline: null,
  flat: null,
  sentiment: 50
})

const sentimentColor = computed(() => {
  const val = marketData.value.sentiment
  if (val > 70) return '#f04438'
  if (val > 30) return '#f59f0b'
  return '#12a150'
})

const sentimentLabel = computed(() => {
  const val = marketData.value.sentiment
  if (val > 70) return '偏乐观'
  if (val > 30) return '中性'
  return '偏悲观'
})

const sentimentTone = computed(() => {
  const val = marketData.value.sentiment
  if (val > 70) return 'hot'
  if (val > 30) return 'neutral'
  return 'cool'
})

onMounted(async () => {
  try {
    const res = await axios.get('/api/calendar/market-overview')
    if (res.data) {
      marketData.value = { ...marketData.value, ...res.data }
    }
  } catch (e) {
    console.log('大盘数据加载中...')
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-card {
  position: relative;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  border: 1px solid rgba(36, 107, 254, 0.14);
  border-radius: 24px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(15, 35, 71, 0.98), rgba(36, 107, 254, 0.88)),
    radial-gradient(circle at 90% 10%, rgba(255, 255, 255, 0.26), transparent 30%);
  box-shadow: 0 22px 60px rgba(15, 35, 71, 0.22);
  overflow: hidden;
}

.hero-card::after {
  content: '';
  position: absolute;
  right: -80px;
  bottom: -110px;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
}

.eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: rgba(255, 255, 255, 0.62);
}

.hero-card h2 {
  margin-bottom: 8px;
  color: #fff;
}

.hero-card p {
  max-width: 560px;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
}

.hero-badge {
  position: relative;
  z-index: 1;
  align-self: flex-start;
  min-width: 126px;
  padding: 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
}

.hero-badge span {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.68);
}

.hero-badge strong {
  font-size: 22px;
}

.index-grid,
.bottom-grid {
  row-gap: 20px;
}

.metric-card {
  height: 100%;
}

.index-card :deep(.el-card__body) {
  min-height: 138px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.index-data {
  text-align: center;
}

.index-value {
  font-size: clamp(30px, 4vw, 42px);
  font-weight: 850;
  color: var(--text-main);
  letter-spacing: -0.05em;
}

.index-change {
  display: inline-flex;
  align-items: center;
  margin-top: 10px;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 800;
  background: #f7f9fd;
}

.advance-decline {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  text-align: center;
}

.breadth-item {
  padding: 18px 12px;
  border-radius: 16px;
  background: #f7f9fd;
}

.breadth-item .label {
  display: block;
  color: var(--text-muted);
  font-size: 14px;
}

.breadth-item .count {
  display: block;
  margin-top: 8px;
  font-size: 30px;
  font-weight: 850;
}

.market-sentiment {
  padding: 24px 4px;
}

@media (max-width: 768px) {
  .hero-card {
    flex-direction: column;
    padding: 22px;
  }

  .advance-decline {
    grid-template-columns: 1fr;
  }
}
</style>
