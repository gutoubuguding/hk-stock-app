<template>
  <div class="settings-page">
    <h2>设置</h2>

    <!-- AI模型配置 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <span>AI模型配置</span>
      </template>

      <el-form label-width="120px">
        <el-form-item label="选择模型">
          <el-select v-model="selectedModel" placeholder="选择LLM模型" @change="onModelChange">
            <el-option
              v-for="(model, key) in availableModels"
              :key="key"
              :label="model.description || key"
              :value="key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="服务商">
          <el-input v-model="provider" placeholder="openai / openrouter / minimax / deepseek / custom" />
        </el-form-item>

        <el-form-item label="模型名">
          <el-input v-model="modelName" placeholder="例如 gpt-5.5 / gpt-4o / openai/gpt-5.5" />
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="apiKey"
            type="password"
            placeholder="输入API Key；没有 API Key 的模型不能直接被项目调用"
            show-password
          />
        </el-form-item>

        <el-form-item label="API地址">
          <el-input
            v-model="baseUrl"
            placeholder="例如 https://api.openai.com/v1 或 OpenAI-compatible 地址"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveModelConfig" :loading="saving">
            保存配置
          </el-button>
          <el-button @click="testConnection" :loading="testing">
            测试连接
          </el-button>
        </el-form-item>
      </el-form>

      <el-alert
        v-if="currentConfig"
        :title="`当前模型: ${currentConfig.ai_provider || currentConfig.provider} - ${currentConfig.ai_model || currentConfig.model}`"
        type="success"
        :closable="false"
        show-icon
      />
    </el-card>

    <!-- Futu OpenD 配置 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <span>Futu OpenD 配置</span>
      </template>
      <el-form label-width="120px">
        <el-form-item label="主机地址">
          <el-input v-model="futuConfig.host" placeholder="127.0.0.1" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="futuConfig.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary">保存</el-button>
          <el-button @click="testFutuConnection" :loading="testingFutu">
            测试连接
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const availableModels = ref({})
const selectedModel = ref('')
const provider = ref('openai')
const modelName = ref('')
const apiKey = ref('')
const baseUrl = ref('')
const currentConfig = ref(null)
const saving = ref(false)
const testing = ref(false)
const testingFutu = ref(false)

const futuConfig = reactive({
  host: '127.0.0.1',
  port: 11111
})

onMounted(async () => {
  await loadModels()
  await loadCurrentConfig()
})

const loadModels = async () => {
  try {
    const res = await axios.get('/api/config/models')
    availableModels.value = res.data.models || {}
  } catch (e) {
    console.error(e)
  }
}

const loadCurrentConfig = async () => {
  try {
    const res = await axios.get('/api/config/current')
    currentConfig.value = res.data
    provider.value = res.data.ai_provider || res.data.provider || provider.value
    modelName.value = res.data.ai_model || res.data.model || modelName.value
    baseUrl.value = res.data.ai_base_url || res.data.base_url || baseUrl.value
    selectedModel.value = provider.value
  } catch (e) {
    console.error(e)
  }
}

const onModelChange = (key) => {
  const model = availableModels.value[key]
  if (model) {
    provider.value = model.provider || provider.value
    modelName.value = model.model || modelName.value
    baseUrl.value = model.base_url || ''
  }
}

const saveModelConfig = async () => {
  if (!provider.value || !modelName.value || !baseUrl.value || !apiKey.value) {
    ElMessage.warning('请填写服务商、模型名、API地址和API Key')
    return
  }
  saving.value = true
  try {
    await axios.post('/api/config/set-model', {
      provider: provider.value,
      model: modelName.value,
      api_key: apiKey.value,
      base_url: baseUrl.value
    })
    ElMessage.success('配置保存成功')
    await loadCurrentConfig()
  } catch (e) {
    ElMessage.error('保存失败')
  }
  saving.value = false
}

const testConnection = async () => {
  if (!provider.value || !modelName.value || !baseUrl.value) {
    ElMessage.warning('请先填写服务商、模型名和API地址')
    return
  }
  if (!apiKey.value) {
    ElMessage.warning('请先填写API Key')
    return
  }

  testing.value = true
  try {
    const res = await axios.post('/api/config/test-connection', {
      provider: provider.value,
      model: modelName.value,
      api_key: apiKey.value,
      base_url: baseUrl.value
    })
    if (res.data.success) {
      ElMessage.success(res.data.message || '连接成功')
    } else {
      ElMessage.error(res.data.message || '连接失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '连接测试失败')
  } finally {
    testing.value = false
  }
}

const testFutuConnection = async () => {
  testingFutu.value = true
  try {
    const res = await axios.post('/api/config/test-futu', {
      host: futuConfig.host,
      port: futuConfig.port
    })
    if (res.data.success) {
      ElMessage.success(res.data.message || 'Futu OpenD 连接成功')
    } else {
      ElMessage.error(res.data.message || 'Futu OpenD 连接失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Futu 连接测试失败')
  } finally {
    testingFutu.value = false
  }
}
</script>

<style scoped>
.settings-page h2 {
  margin-bottom: 20px;
}
</style>
