<template>
  <div class="search-page">
    <h2>股票查询</h2>

    <el-input
      v-model="searchKeyword"
      placeholder="输入股票代码、名称或板块搜索"
      size="large"
      clearable
      @input="handleSearch"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <el-table
      :data="searchResults"
      style="width: 100%; margin-top: 20px;"
      v-loading="loading"
      @row-click="goToDetail"
      stripe
    >
      <el-table-column prop="stockCode" label="股票代码" width="120" />
      <el-table-column prop="stockName" label="股票名称" width="200" />
      <el-table-column prop="sector" label="板块" width="150" />
      <el-table-column prop="marketCap" label="市值" width="150">
        <template #default="{ row }">
          {{ formatMarketCap(row.marketCap) }}
        </template>
      </el-table-column>
      <el-table-column prop="isHkStockConnect" label="港股通" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.isHkStockConnect" type="success">是</el-tag>
          <el-tag v-else type="info">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click.stop="addToWatchlist(row)">加入自选</el-button>
          <el-button size="small" type="primary" @click.stop="viewNews(row)">新闻分析</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const searchKeyword = ref('')
const searchResults = ref([])
const loading = ref(false)

let searchTimer = null

const handleSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    if (!searchKeyword.value.trim()) {
      searchResults.value = []
      return
    }
    loading.value = true
    try {
      const res = await axios.get('/api/stock/search', {
        params: { keyword: searchKeyword.value }
      })
      searchResults.value = res.data
    } catch (e) {
      console.error('搜索失败', e)
    }
    loading.value = false
  }, 300)
}

const goToDetail = (row) => {
  router.push(`/stock/${row.stockCode}`)
}

const addToWatchlist = async (row) => {
  try {
    await axios.post('/api/watchlist', {
      stockCode: row.stockCode,
      stockName: row.stockName
    })
    ElMessage.success(`已添加 ${row.stockName} 到自选股`)
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const viewNews = (row) => {
  router.push(`/stock/${row.stockCode}?tab=news`)
}

const formatMarketCap = (cap) => {
  if (!cap) return '--'
  if (cap >= 1e12) return (cap / 1e12).toFixed(2) + '万亿'
  if (cap >= 1e8) return (cap / 1e8).toFixed(2) + '亿'
  return cap.toLocaleString()
}
</script>

<style scoped>
.search-page h2 {
  margin-bottom: 20px;
  color: #303133;
}

.el-table :deep(tr) {
  cursor: pointer;
}
</style>
