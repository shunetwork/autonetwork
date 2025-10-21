import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCompareStore = defineStore('compare', () => {
  // 状态
  const devices = ref([])
  const tasks = ref([])
  const compareResult = ref(null)
  const loading = ref(false)

  // 操作
  const setDevices = (deviceList: any[]) => {
    devices.value = deviceList
  }

  const setTasks = (taskList: any[]) => {
    tasks.value = taskList
  }

  const setCompareResult = (result: any) => {
    compareResult.value = result
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const clearCompareResult = () => {
    compareResult.value = null
  }

  return {
    devices,
    tasks,
    compareResult,
    loading,
    setDevices,
    setTasks,
    setCompareResult,
    setLoading,
    clearCompareResult
  }
})
