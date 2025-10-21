#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份调度器
支持CRON式调度和计划任务
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import atexit

from models import db, BackupSchedule, Device, BackupTask
from backup_service import BackupService

logger = logging.getLogger(__name__)

class BackupScheduler:
    """备份调度器类"""
    
    def __init__(self):
        # 配置作业存储
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///scheduler.db')
        }
        
        # 配置执行器
        executors = {
            'default': ThreadPoolExecutor(max_workers=10)
        }
        
        # 作业默认配置
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5分钟
        }
        
        # 创建调度器
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'
        )
        
        self.backup_service = BackupService()
        self.is_running = False
    
    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            
            # 加载所有计划任务
            self.load_schedules()
            
            # 注册退出处理
            atexit.register(self.shutdown)
            
            logger.info("备份调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("备份调度器已关闭")
    
    def load_schedules(self):
        """加载所有计划任务"""
        try:
            schedules = BackupSchedule.query.filter_by(is_active=True).all()
            
            for schedule in schedules:
                self.add_schedule_job(schedule)
            
            logger.info(f"已加载 {len(schedules)} 个计划任务")
            
        except Exception as e:
            logger.error(f"加载计划任务失败: {str(e)}")
    
    def add_schedule_job(self, schedule: BackupSchedule):
        """添加计划任务"""
        try:
            job_id = f"schedule_{schedule.id}"
            
            # 解析CRON表达式
            cron_parts = schedule.cron_expression.split()
            if len(cron_parts) != 5:
                logger.error(f"无效的CRON表达式: {schedule.cron_expression}")
                return
            
            # 创建CRON触发器
            trigger = CronTrigger(
                second=0,  # 默认在整分钟执行
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4]
            )
            
            # 添加作业
            self.scheduler.add_job(
                func=self.execute_scheduled_backup,
                trigger=trigger,
                args=[schedule.id],
                id=job_id,
                name=f"计划备份: {schedule.name}",
                replace_existing=True
            )
            
            # 更新下次运行时间
            next_run = self.scheduler.get_job(job_id).next_run_time
            schedule.next_run = next_run
            db.session.commit()
            
            logger.info(f"已添加计划任务: {schedule.name} (ID: {schedule.id})")
            
        except Exception as e:
            logger.error(f"添加计划任务失败: {str(e)}")
    
    def remove_schedule_job(self, schedule_id: int):
        """移除计划任务"""
        try:
            job_id = f"schedule_{schedule_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除计划任务: {job_id}")
        except Exception as e:
            logger.error(f"移除计划任务失败: {str(e)}")
    
    def execute_scheduled_backup(self, schedule_id: int):
        """执行计划备份"""
        try:
            schedule = BackupSchedule.query.get(schedule_id)
            if not schedule or not schedule.is_active:
                return
            
            logger.info(f"开始执行计划备份: {schedule.name}")
            
            # 更新最后运行时间
            schedule.last_run = datetime.utcnow()
            db.session.commit()
            
            # 获取设备ID列表
            device_ids = schedule.device_ids if isinstance(schedule.device_ids, list) else []
            if not device_ids:
                logger.warning(f"计划任务 {schedule.name} 没有配置设备")
                return
            
            # 执行批量备份
            result = self.backup_service.backup_multiple_devices(
                device_ids=device_ids,
                user_id=schedule.created_by,
                backup_command=schedule.backup_command,
                task_type='scheduled'
            )
            
            if result['success']:
                logger.info(f"计划备份完成: {schedule.name}, 任务数: {result['task_count']}")
            else:
                logger.error(f"计划备份失败: {schedule.name}, 错误: {result['error']}")
            
        except Exception as e:
            logger.error(f"执行计划备份失败: {str(e)}")
    
    def create_schedule(self, name: str, cron_expression: str, device_ids: list,
                      backup_command: str, created_by: int, description: str = None) -> dict:
        """创建计划任务"""
        try:
            # 验证CRON表达式
            if not self._validate_cron_expression(cron_expression):
                return {
                    'success': False,
                    'error': '无效的CRON表达式'
                }
            
            # 创建计划任务
            schedule = BackupSchedule(
                name=name,
                description=description,
                cron_expression=cron_expression,
                device_ids=device_ids,
                backup_command=backup_command,
                created_by=created_by,
                is_active=True
            )
            
            db.session.add(schedule)
            db.session.commit()
            
            # 添加到调度器
            self.add_schedule_job(schedule)
            
            return {
                'success': True,
                'message': '计划任务创建成功',
                'schedule_id': schedule.id
            }
            
        except Exception as e:
            logger.error(f"创建计划任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_schedule(self, schedule_id: int, **kwargs) -> dict:
        """更新计划任务"""
        try:
            schedule = BackupSchedule.query.get(schedule_id)
            if not schedule:
                return {
                    'success': False,
                    'error': '计划任务不存在'
                }
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            
            schedule.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 重新添加到调度器
            self.remove_schedule_job(schedule_id)
            if schedule.is_active:
                self.add_schedule_job(schedule)
            
            return {
                'success': True,
                'message': '计划任务更新成功'
            }
            
        except Exception as e:
            logger.error(f"更新计划任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_schedule(self, schedule_id: int) -> dict:
        """删除计划任务"""
        try:
            schedule = BackupSchedule.query.get(schedule_id)
            if not schedule:
                return {
                    'success': False,
                    'error': '计划任务不存在'
                }
            
            # 从调度器移除
            self.remove_schedule_job(schedule_id)
            
            # 删除记录
            db.session.delete(schedule)
            db.session.commit()
            
            return {
                'success': True,
                'message': '计划任务删除成功'
            }
            
        except Exception as e:
            logger.error(f"删除计划任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_schedule_status(self) -> dict:
        """获取调度器状态"""
        try:
            jobs = self.scheduler.get_jobs()
            schedules = BackupSchedule.query.filter_by(is_active=True).all()
            
            return {
                'success': True,
                'scheduler_running': self.is_running,
                'total_jobs': len(jobs),
                'active_schedules': len(schedules),
                'jobs': [
                    {
                        'id': job.id,
                        'name': job.name,
                        'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                        'trigger': str(job.trigger)
                    }
                    for job in jobs
                ]
            }
            
        except Exception as e:
            logger.error(f"获取调度器状态失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_cron_expression(self, cron_expression: str) -> bool:
        """验证CRON表达式"""
        try:
            parts = cron_expression.split()
            if len(parts) != 5:
                return False
            
            # 简单验证每个部分
            for part in parts:
                if part == '*':
                    continue
                if ',' in part:
                    for subpart in part.split(','):
                        if not subpart.isdigit():
                            return False
                elif '-' in part:
                    range_parts = part.split('-')
                    if len(range_parts) != 2:
                        return False
                    for subpart in range_parts:
                        if not subpart.isdigit():
                            return False
                elif not part.isdigit():
                    return False
            
            return True
            
        except Exception:
            return False
    
    def run_immediate_backup(self, device_ids: list, user_id: int, 
                           backup_command: str = None) -> dict:
        """立即执行备份（不通过调度器）"""
        try:
            result = self.backup_service.backup_multiple_devices(
                device_ids=device_ids,
                user_id=user_id,
                backup_command=backup_command,
                task_type='immediate'
            )
            
            return result
            
        except Exception as e:
            logger.error(f"立即备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


