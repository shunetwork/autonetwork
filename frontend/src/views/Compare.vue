<template>
  <div class="compare-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><DocumentCopy /></el-icon>
        配置对比
      </h1>
      <div class="page-actions">
        <el-button type="primary" @click="performCompare" :disabled="!canCompare">
          <el-icon><Switch /></el-icon>
          开始对比
        </el-button>
        <el-button @click="clearSelection">
          <el-icon><Delete /></el-icon>
          清除选择
        </el-button>
      </div>
    </div>

    <!-- 选择区域 -->
    <el-card class="selection-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>选择要对比的备份任务</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px">
        <!-- 设备选择 -->
        <el-form-item label="选择设备" required>
          <el-select
            v-model="form.deviceId"
            placeholder="请选择设备"
            style="width: 100%"
            @change="handleDeviceChange"
            :loading="deviceLoading"
          >
            <el-option
              v-for="device in devices"
              :key="device.id"
              :label="`${device.alias || device.ip_address} (${device.ip_address})`"
              :value="device.id"
            />
          </el-select>
          <div class="form-tip">选择设备后，将显示该设备的所有备份任务</div>
        </el-form-item>

        <!-- 备份任务选择 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="第一个备份（基准）" required>
              <el-select
                v-model="form.task1Id"
                placeholder="请选择备份任务"
                style="width: 100%"
                :disabled="!form.deviceId"
                :loading="taskLoading"
                @change="handleTaskChange"
              >
                <el-option
                  v-for="task in tasks"
                  :key="task.id"
                  :label="formatTaskTime(task.created_at)"
                  :value="task.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="第二个备份（对比）" required>
              <el-select
                v-model="form.task2Id"
                placeholder="请选择备份任务"
                style="width: 100%"
                :disabled="!form.deviceId"
                :loading="taskLoading"
                @change="handleTaskChange"
              >
                <el-option
                  v-for="task in tasks"
                  :key="task.id"
                  :label="formatTaskTime(task.created_at)"
                  :value="task.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-button
              type="info"
              @click="compareLatest"
              :disabled="!form.deviceId"
              :loading="compareLoading"
            >
              <el-icon><Clock /></el-icon>
              对比最新两个备份
            </el-button>
          </el-col>
          <el-col :span="12">
            <el-checkbox v-model="form.ignoreWhitespace">
              忽略空白字符差异
            </el-checkbox>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 对比结果 -->
    <el-card v-if="compareResult" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>对比结果</span>
        </div>
      </template>

      <div class="compare-result">
        <!-- 任务信息 -->
        <el-row :gutter="20" class="task-info">
          <el-col :span="12">
            <div class="task-card">
              <h4>第一个备份</h4>
              <p><strong>设备:</p>
              <p><strong>时间:</strong> {{ formatTaskTime(compareResult.task1.created_at) }}</p>
              <p><strong>文件大小:</strong> {{ formatFileSize(compareResult.task1.file_size) }}</p>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="task-card">
              <h4>第二个备份</h4>
              <p><strong>设备:</strong> {{ compareResult.task2.device }}</p>
              <p><strong>时间:</strong> {{ formatTaskTime(compareResult.task2.created_at) }}</p>
              <p><strong>文件大小:</strong> {{ formatFileSize(compareResult.task2.file_size) }}</p>
            </div>
          </el-col>
        </el-row>

        <!-- 差异统计 -->
        <el-divider />
        <div class="diff-stats">
          <h4>差异统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总变化" :value="compareResult.diff.summary.total_changes" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="新增行" :value="compareResult.diff.summary.added_lines" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="删除行" :value="compareResult.diff.summary.removed_lines" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="修改行" :value="compareResult.diff.summary.modified_lines" />
            </el-col>
          </el-row>
        </div>

        <!-- 详细差异 -->
        <el-divider />
        <div class="diff-details">
          <h4>详细差异</h4>
          <div v-if="compareResult.diff.summary.has_changes" class="diff-content">
            <pre class="diff-text">{{ compareResult.diff.raw_diff }}</pre>
          </div>
          <el-empty v-else description="配置文件完全相同，无差异" />
        </div>
      </div>
    </el-card>

    <!-- 加载对话框 -->
    <el-dialog
      v-model="loadingVisible"
      title="正在分析"
      width="300px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="loading-content">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在分析配置差异，请稍候...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy, Switch, Delete, Setting, Clock, DataAnalysis, Loading } from '@element-plus/icons-vue'
import { useCompareStore } from '@/stores/compare'
import dayjs from 'dayjs'

// 类型定义
interface Device {
  id: number
  alias: string
  ip_address: string
  is_active: boolean
}

interface Task {
  id: number
  device_id: number
  device_alias: string
  device_ip: string
  created_at: string
  file_size: number
  status: string
}

interface CompareResult {
  task1: Task
  task2: Task
  diff: {
    summary: {
      total_changes: number
      added_lines: number
      removed_lines: number
      modified_lines: number
      has_changes: boolean
    }
    raw_diff: string
  }
}

// 响应式数据
const devices = ref<Device[]>([])
const tasks = ref<Task[]>([])
const compareResult = ref<CompareResult | null>(null)
const loadingVisible = ref(false)
const deviceLoading = ref(false)
const taskLoading = ref(false)
const compareLoading = ref(false)

const form = reactive({
  deviceId: '',
  task1Id: '',
  task2Id: '',
  ignoreWhitespace: true
})

// 计算属性
const canCompare = computed(() => {
  return form.deviceId && form.task1Id && form.task2Id && form.task1Id !== form.task2Id
})

// 方法
const formatTaskTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const formatFileSize = (size: number) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const handleDeviceChange = async () => {
  if (!form.deviceId) {
    tasks.value = []
    form.task1Id = ''
    form.task2Id = ''
    return
  }

  taskLoading.value = true
  try {
    const response = await fetch(`/api/backup/device/${form.deviceId}`)
    const data = await response.json()
    
    if (data.success) {
      tasks.value = data.tasks.filter((task: Task) => task.status === 'success')
      form.task1Id = ''
      form.task2Id = ''
    } else {
      ElMessage.error('加载备份任务失败: ' + data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    taskLoading.value = false
  }
}

const handleTaskChange = () => {
  // 任务选择变化时的处理
}

const compareLatest = async () => {
  if (!form.deviceId) {
    ElMessage.warning('请先选择设备')
    return
  }

  compareLoading.value = true
  loadingVisible.value = true

  try {
    const response = await fetch(`/api/backup/compare/quick/${form.deviceId}`)
    const data = await response.json()
    
    if (data.success) {
      compareResult.value = data
      ElMessage.success('对比完成')
    } else {
      ElMessage.error('对比失败: ' + data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    compareLoading.value = false
    loadingVisible.value = false
  }
}

const performCompare = async () => {
  if (!canCompare.value) {
    ElMessage.warning('请选择两个不同的备份任务')
    return
  }

  loadingVisible.value = true

  try {
    const response = await fetch(`/api/backup/compare/${form.task1Id}/${form.task2Id}`)
    const data = await response.json()
    
    if (data.success) {
      compareResult.value = data
      ElMessage.success('对比完成')
    } else {
      ElMessage.error('对比失败: ' + data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loadingVisible.value = false
  }
}

const clearSelection = () => {
  form.deviceId = ''
  form.task1Id = ''
  form.task2Id = ''
  tasks.value = []
  compareResult.value = null
}

// 加载设备列表
const loadDevices = async () => {
  deviceLoading.value = true
  try {
    const response = await fetch('/api/device/list')
    const data = await response.json()
    
    if (data.success) {
      devices.value = data.devices.filter((device: Device) => device.is_active)
    } else {
      ElMessage.error('加载设备列表失败: ' + data.error)
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    deviceLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.compare-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.selection-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.result-card {
  margin-top: 20px;
}

.task-info {
  margin-bottom: 20px;
}

.task-card {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.task-card h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.task-card p {
  margin: 5px 0;
  color: #6c757d;
}

.diff-stats {
  margin: 20px 0;
}

.diff-stats h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.diff-details h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.diff-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.diff-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.loading-content {
  text-align: center;
  padding: 20px;
}

.loading-content .el-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.loading-content p {
  margin: 0;
  color: #6c757d;
}
</style>
