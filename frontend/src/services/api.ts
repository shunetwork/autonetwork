import axios from 'axios'
import type { DeviceListResponse, TaskListResponse, CompareResponse } from '@/types'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API方法
export const deviceApi = {
  // 获取设备列表
  getDevices: (): Promise<DeviceListResponse> => {
    return api.get('/device/list').then(res => res.data)
  },

  // 获取设备详情
  getDevice: (id: number) => {
    return api.get(`/device/${id}`).then(res => res.data)
  },

  // 创建设备
  createDevice: (data: any) => {
    return api.post('/device', data).then(res => res.data)
  },

  // 更新设备
  updateDevice: (id: number, data: any) => {
    return api.put(`/device/${id}`, data).then(res => res.data)
  },

  // 删除设备
  deleteDevice: (id: number) => {
    return api.delete(`/device/${id}`).then(res => res.data)
  },

  // 测试设备连接
  testConnection: (data: any) => {
    return api.post('/device/test', data).then(res => res.data)
  }
}

export const backupApi = {
  // 获取设备备份任务
  getDeviceTasks: (deviceId: number): Promise<TaskListResponse> => {
    return api.get(`/backup/device/${deviceId}`).then(res => res.data)
  },

  // 获取最近备份
  getRecentTasks: () => {
    return api.get('/backup/recent').then(res => res.data)
  },

  // 执行备份
  executeBackup: (data: any) => {
    return api.post('/backup/execute', data).then(res => res.data)
  },

  // 对比备份
  compareBackups: (task1Id: number, task2Id: number): Promise<CompareResponse> => {
    return api.get(`/backup/compare/${task1Id}/${task2Id}`).then(res => res.data)
  },

  // 快速对比最新备份
  quickCompare: (deviceId: number): Promise<CompareResponse> => {
    return api.get(`/backup/compare/quick/${deviceId}`).then(res => res.data)
  }
}

export const logApi = {
  // 获取日志列表
  getLogs: () => {
    return api.get('/logs/list').then(res => res.data)
  },

  // 查看日志内容
  viewLog: (filename: string) => {
    return api.get(`/logs/view/${filename}`).then(res => res.data)
  }
}

export const statisticsApi = {
  // 获取统计信息
  getStatistics: () => {
    return api.get('/statistics').then(res => res.data)
  }
}

export default api
