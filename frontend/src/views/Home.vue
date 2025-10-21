<template>
  <div class="home-container">
    <el-card class="welcome-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><HomeFilled /></el-icon>
          <span>欢迎使用Cisco设备配置备份系统</span>
        </div>
      </template>
      
      <div class="welcome-content">
        <h2>系统功能</h2>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="feature-card" shadow="hover">
              <el-icon class="feature-icon"><Server /></el-icon>
              <h3>设备管理</h3>
              <p>管理Cisco网络设备，支持SSH和Telnet连接</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="feature-card" shadow="hover">
              <el-icon class="feature-icon"><DocumentCopy /></el-icon>
              <h3>配置备份</h3>
              <p>单设备和批量备份，支持定时任务</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="feature-card" shadow="hover">
              <el-icon class="feature-icon"><DataAnalysis /></el-icon>
              <h3>配置对比</h3>
              <p>智能对比配置文件差异，生成详细报告</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled, Server, DocumentCopy, DataAnalysis } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.welcome-content h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.feature-card {
  text-align: center;
  padding: 20px;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.feature-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 15px;
}

.feature-card h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.feature-card p {
  color: #6c757d;
  line-height: 1.5;
}
</style>
