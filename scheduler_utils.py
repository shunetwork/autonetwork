#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计划任务工具模块
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class CronValidator:
    """CRON表达式验证器"""
    
    @staticmethod
    def validate_cron_expression(cron_expr: str) -> Tuple[bool, str]:
        """
        验证CRON表达式格式
        
        Args:
            cron_expr: CRON表达式字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not cron_expr:
            return False, "CRON表达式不能为空"
        
        # 分割CRON表达式
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return False, "CRON表达式必须包含5个字段：分 时 日 月 周"
        
        # 验证每个字段
        field_names = ['分钟', '小时', '日期', '月份', '星期']
        field_patterns = [
            r'^(\*|[0-5]?\d)(,(\*|[0-5]?\d))*$',  # 分钟: 0-59
            r'^(\*|[01]?\d|2[0-3])(,(\*|[01]?\d|2[0-3]))*$',  # 小时: 0-23
            r'^(\*|[012]?\d|3[01])(,(\*|[012]?\d|3[01]))*$',  # 日期: 1-31
            r'^(\*|[01]?\d)(,(\*|[01]?\d))*$',  # 月份: 1-12
            r'^(\*|[0-6])(,(\*|[0-6]))*$'  # 星期: 0-6 (0=周日)
        ]
        
        for i, (part, name, pattern) in enumerate(zip(parts, field_names, field_patterns)):
            if not re.match(pattern, part):
                return False, f"{name}字段格式错误: {part}"
        
        return True, "CRON表达式格式正确"
    
    @staticmethod
    def get_next_run_time(cron_expr: str, from_time: Optional[datetime] = None) -> Optional[datetime]:
        """
        计算下次运行时间
        
        Args:
            cron_expr: CRON表达式
            from_time: 起始时间，默认为当前时间
            
        Returns:
            下次运行时间
        """
        try:
            from croniter import croniter
            
            if from_time is None:
                from_time = datetime.now()
            
            cron = croniter(cron_expr, from_time)
            return cron.get_next(datetime)
        except ImportError:
            # 如果没有croniter库，使用简单计算
            return CronValidator._simple_next_run(cron_expr, from_time)
        except Exception as e:
            print(f"计算下次运行时间失败: {e}")
            return None
    
    @staticmethod
    def _simple_next_run(cron_expr: str, from_time: datetime) -> Optional[datetime]:
        """简单的下次运行时间计算（仅支持基本格式）"""
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return None
        
        minute, hour, day, month, weekday = parts
        
        # 简化处理：只处理固定时间
        if minute != '*' and hour != '*':
            try:
                target_minute = int(minute)
                target_hour = int(hour)
                
                # 计算今天的目标时间
                target_time = from_time.replace(
                    hour=target_hour, 
                    minute=target_minute, 
                    second=0, 
                    microsecond=0
                )
                
                # 如果时间已过，计算明天
                if target_time <= from_time:
                    target_time += timedelta(days=1)
                
                return target_time
            except ValueError:
                return None
        
        return None


class FrequencyConfig:
    """频率配置管理器"""
    
    @staticmethod
    def create_daily_config(hour: int = 2, minute: int = 0) -> Dict:
        """创建每日配置"""
        return {
            'type': 'daily',
            'hour': hour,
            'minute': minute,
            'cron': f"{minute} {hour} * * *"
        }
    
    @staticmethod
    def create_weekly_config(weekday: int = 1, hour: int = 2, minute: int = 0) -> Dict:
        """创建每周配置"""
        return {
            'type': 'weekly',
            'weekday': weekday,  # 0=周日, 1=周一, ..., 6=周六
            'hour': hour,
            'minute': minute,
            'cron': f"{minute} {hour} * * {weekday}"
        }
    
    @staticmethod
    def create_monthly_config(day: int = 1, hour: int = 2, minute: int = 0) -> Dict:
        """创建每月配置"""
        return {
            'type': 'monthly',
            'day': day,
            'hour': hour,
            'minute': minute,
            'cron': f"{minute} {hour} {day} * *"
        }
    
    @staticmethod
    def create_custom_config(cron_expr: str) -> Dict:
        """创建自定义配置"""
        return {
            'type': 'custom',
            'cron': cron_expr
        }
    
    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, str]:
        """验证频率配置"""
        if not isinstance(config, dict):
            return False, "配置必须是字典格式"
        
        config_type = config.get('type')
        if not config_type:
            return False, "缺少配置类型"
        
        if config_type == 'daily':
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return False, "每日配置：小时必须在0-23之间，分钟必须在0-59之间"
        
        elif config_type == 'weekly':
            weekday = config.get('weekday', 0)
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            if not (0 <= weekday <= 6 and 0 <= hour <= 23 and 0 <= minute <= 59):
                return False, "每周配置：星期必须在0-6之间，小时必须在0-23之间，分钟必须在0-59之间"
        
        elif config_type == 'monthly':
            day = config.get('day', 1)
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            if not (1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59):
                return False, "每月配置：日期必须在1-31之间，小时必须在0-23之间，分钟必须在0-59之间"
        
        elif config_type == 'custom':
            cron_expr = config.get('cron')
            if not cron_expr:
                return False, "自定义配置：缺少CRON表达式"
            return CronValidator.validate_cron_expression(cron_expr)
        
        else:
            return False, f"不支持的配置类型: {config_type}"
        
        return True, "配置验证通过"
    
    @staticmethod
    def get_cron_from_config(config: Dict) -> str:
        """从配置获取CRON表达式"""
        if config.get('type') == 'custom':
            return config.get('cron', '')
        
        # 从其他配置类型生成CRON表达式
        if config.get('type') == 'daily':
            return f"{config.get('minute', 0)} {config.get('hour', 2)} * * *"
        elif config.get('type') == 'weekly':
            return f"{config.get('minute', 0)} {config.get('hour', 2)} * * {config.get('weekday', 1)}"
        elif config.get('type') == 'monthly':
            return f"{config.get('minute', 0)} {config.get('hour', 2)} {config.get('day', 1)} * *"
        
        return ''


class ScheduleHelper:
    """调度助手类"""
    
    @staticmethod
    def get_frequency_options() -> List[Dict]:
        """获取频率选项"""
        return [
            {'value': 'daily', 'label': '每日', 'description': '每天定时执行'},
            {'value': 'weekly', 'label': '每周', 'description': '每周定时执行'},
            {'value': 'monthly', 'label': '每月', 'description': '每月定时执行'},
            {'value': 'custom', 'label': '自定义', 'description': '使用CRON表达式'}
        ]
    
    @staticmethod
    def get_weekday_options() -> List[Dict]:
        """获取星期选项"""
        return [
            {'value': 0, 'label': '周日'},
            {'value': 1, 'label': '周一'},
            {'value': 2, 'label': '周二'},
            {'value': 3, 'label': '周三'},
            {'value': 4, 'label': '周四'},
            {'value': 5, 'label': '周五'},
            {'value': 6, 'label': '周六'}
        ]
    
    @staticmethod
    def get_task_type_options() -> List[Dict]:
        """获取任务类型选项"""
        return [
            {'value': 'backup', 'label': '备份任务', 'description': '设备配置备份'},
            {'value': 'maintenance', 'label': '维护任务', 'description': '系统维护任务'}
        ]
    
    @staticmethod
    def format_next_run_time(next_run: Optional[datetime]) -> str:
        """格式化下次运行时间"""
        if not next_run:
            return '未设置'
        
        now = datetime.now()
        diff = next_run - now
        
        if diff.total_seconds() < 0:
            return '已过期'
        elif diff.total_seconds() < 3600:  # 1小时内
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes}分钟后'
        elif diff.total_seconds() < 86400:  # 1天内
            hours = int(diff.total_seconds() / 3600)
            return f'{hours}小时后'
        else:
            return next_run.strftime('%Y-%m-%d %H:%M:%S')
