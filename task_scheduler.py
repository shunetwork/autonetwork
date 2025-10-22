#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器模块
集成APScheduler实现计划任务执行
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import atexit

from models import db, ScheduledTask, TaskExecution, Device
from backup_service import BackupService
from scheduler_utils import CronValidator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """任务调度器类"""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = None
        self.backup_service = None
        
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        
        # 配置调度器
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'
        )
        
        # 添加事件监听器
        self.scheduler.add_listener(self.job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self.job_error_listener, EVENT_JOB_ERROR)
        
        # 初始化备份服务
        self.backup_service = BackupService()
        
        # 注册关闭处理
        atexit.register(self.shutdown)
        
    def start(self):
        """启动调度器"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            logger.info("任务调度器已启动")
            
            # 加载现有任务
            self.load_scheduled_tasks()
            
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("任务调度器已关闭")
            
    def load_scheduled_tasks(self):
        """加载所有启用的计划任务"""
        with self.app.app_context():
            try:
                tasks = ScheduledTask.query.filter_by(is_active=True).all()
                for task in tasks:
                    self.add_job(task)
                logger.info(f"已加载 {len(tasks)} 个计划任务")
            except Exception as e:
                logger.error(f"加载计划任务失败: {e}")
                
    def add_job(self, task):
        """添加任务到调度器"""
        try:
            # 验证CRON表达式
            is_valid, error_msg = CronValidator.validate_cron_expression(task.cron_expression)
            if not is_valid:
                logger.error(f"任务 {task.name} CRON表达式无效: {error_msg}")
                return False
                
            # 创建触发器
            trigger = CronTrigger.from_crontab(task.cron_expression)
            
            # 添加任务
            self.scheduler.add_job(
                func=self.execute_task,
                trigger=trigger,
                args=[task.id],
                id=f"task_{task.id}",
                name=task.name,
                replace_existing=True
            )
            
            logger.info(f"已添加任务: {task.name} (ID: {task.id})")
            return True
            
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return False
            
    def remove_job(self, task_id):
        """从调度器移除任务"""
        try:
            job_id = f"task_{task_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"已移除任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"移除任务失败: {e}")
            return False
            
    def execute_task(self, task_id):
        """执行计划任务"""
        with self.app.app_context():
            try:
                # 获取任务信息
                task = ScheduledTask.query.get(task_id)
                if not task:
                    logger.error(f"任务不存在: {task_id}")
                    return
                    
                if not task.is_active:
                    logger.info(f"任务已禁用，跳过执行: {task.name}")
                    return
                    
                logger.info(f"开始执行计划任务: {task.name}")
                
                # 创建执行记录
                execution = TaskExecution(
                    scheduled_task_id=task_id,
                    status='running',
                    started_at=datetime.utcnow()
                )
                db.session.add(execution)
                db.session.commit()
                
                # 执行任务
                if task.task_type == 'backup':
                    result = self.execute_backup_task(task, execution)
                else:
                    result = self.execute_maintenance_task(task, execution)
                
                # 更新执行记录
                execution.status = 'completed' if result['success'] else 'failed'
                execution.completed_at = datetime.utcnow()
                execution.result_summary = result.get('summary', '')
                execution.error_message = result.get('error', '')
                execution.execution_log = result.get('log', '')
                
                # 更新任务最后运行时间
                task.last_run = datetime.utcnow()
                
                db.session.commit()
                
                logger.info(f"计划任务执行完成: {task.name}, 状态: {execution.status}")
                
            except Exception as e:
                logger.error(f"执行计划任务失败: {e}")
                if 'execution' in locals():
                    execution.status = 'failed'
                    execution.completed_at = datetime.utcnow()
                    execution.error_message = str(e)
                    db.session.commit()
                    
    def execute_backup_task(self, task, execution):
        """执行备份任务"""
        try:
            target_devices = task.target_devices if isinstance(task.target_devices, list) else []
            if not target_devices:
                return {
                    'success': False,
                    'error': '没有指定目标设备',
                    'summary': '备份失败：没有指定目标设备'
                }
            
            # 获取设备信息
            devices = Device.query.filter(Device.id.in_(target_devices)).all()
            if not devices:
                return {
                    'success': False,
                    'error': '指定的设备不存在',
                    'summary': '备份失败：指定的设备不存在'
                }
            
            success_count = 0
            failed_count = 0
            log_entries = []
            
            for device in devices:
                try:
                    log_entries.append(f"开始备份设备: {device.alias} ({device.ip_address})")
                    
                    # 执行备份
                    result = self.backup_service.backup_device(
                        device_id=device.id,
                        command=task.backup_command,
                        task_type='scheduled'
                    )
                    
                    if result['success']:
                        success_count += 1
                        log_entries.append(f"设备 {device.alias} 备份成功")
                    else:
                        failed_count += 1
                        log_entries.append(f"设备 {device.alias} 备份失败: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    failed_count += 1
                    log_entries.append(f"设备 {device.alias} 备份异常: {str(e)}")
            
            summary = f"备份完成: 成功 {success_count} 个, 失败 {failed_count} 个"
            log_entries.append(summary)
            
            return {
                'success': failed_count == 0,
                'summary': summary,
                'log': '\n'.join(log_entries)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f'备份任务执行失败: {str(e)}'
            }
            
    def execute_maintenance_task(self, task, execution):
        """执行维护任务"""
        # 这里可以实现其他类型的维护任务
        return {
            'success': True,
            'summary': '维护任务执行完成',
            'log': f'维护任务: {task.name} 执行完成'
        }
        
    def job_executed_listener(self, event):
        """任务执行完成监听器"""
        logger.info(f"任务执行完成: {event.job_id}")
        
    def job_error_listener(self, event):
        """任务执行错误监听器"""
        logger.error(f"任务执行错误: {event.job_id}, 异常: {event.exception}")
        
    def update_task(self, task):
        """更新任务"""
        # 先移除旧任务
        self.remove_job(task.id)
        # 如果任务启用，重新添加
        if task.is_active:
            self.add_job(task)
            
    def get_job_status(self, task_id):
        """获取任务状态"""
        try:
            job_id = f"task_{task_id}"
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'exists': True,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
            else:
                return {'exists': False}
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return {'exists': False, 'error': str(e)}


# 全局调度器实例
task_scheduler = TaskScheduler()
