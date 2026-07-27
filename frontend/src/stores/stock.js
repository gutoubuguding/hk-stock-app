import { ref } from 'vue'
import { defineStore } from 'pinia'
import request from '@/http/request'

export const useStockStore = defineStore('stock', () => {
  const currentStock = ref(null)
  const searchResults = ref([])
  const loading = ref(false)

  async function searchStocks(keyword) {
    loading.value = true
    try {
      const res = await request({ url: '/stock/search', params: { keyword } })
      searchResults.value = res.data || []
      return res.data
    } finally {
      loading.value = false
    }
  }

  async function getStockDetail(stockCode) {
    loading.value = true
    try {
      const res = await request({ url: '/stock/daily-info', params: { stockCode } })
      currentStock.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  return {
    currentStock,
    searchResults,
    loading,
    searchStocks,
    getStockDetail,
  }
})
