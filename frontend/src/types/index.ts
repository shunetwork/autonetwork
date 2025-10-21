// 设备类型定义
export interface Device {
  id: number
  alias: string
  ip_address: string
  port: number
  protocol: 'ssh' | 'telnet'
  username: string
  device_type: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 备份任务类型定义
export interface BackupTask {
  id: number
  device_id: number
  device_alias: string
  device_ip: string
  user_id: number
  username: string
  task_type: 'manual' | 'scheduled'
  status: 'pending' | 'running' | 'success' | 'failed'
  backup_command: string
  file_path: string
  file_size: number
  file_hash: string
  started_at: string
  completed_at: string
  created_at: string
  error_message: string
  retry_count: number
  max_retries: number
}

// 对比结果类型定义
export interface CompareResult {
  task1: BackupTask
  task2: BackupTask
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

// API响应类型定义
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// 设备列表响应
export interface DeviceListResponse {
  success: boolean
  devices: Device[]
  error?: string
}

// 备份任务列表响应
export interface TaskListResponse {
  success: boolean
  tasks: BackupTask[]
  error?: string
}

// 对比响应
export interface CompareResponse {
  success: boolean
  task1: BackupTask
  task2: BackupTask
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
  error?: string
}
