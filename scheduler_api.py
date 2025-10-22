#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计划任务API模块
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json

from models import db, ScheduledTask, TaskExecution
from scheduler_utils import FrequencyConfig, CronValidator, ScheduleHelper
from task_scheduler import task_scheduler

scheduler_bp = Blueprint('scheduler', __name__)


@scheduler_bp.route('/tasks', methods=['GET'])
@login_required
def get_scheduled_tasks():
    """获取计划任务列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询计划任务
        tasks = ScheduledTask.query.order_by(ScheduledTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取计划任务失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks', methods=['POST'])
@login_required
def create_scheduled_task():
    """创建计划任务"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'task_type', 'frequency_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 验证频率配置
        frequency_config = data.get('frequency_config', {})
        is_valid, error_msg = FrequencyConfig.validate_config(frequency_config)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'频率配置错误: {error_msg}'
            }), 400
        
        # 生成CRON表达式
        cron_expr = FrequencyConfig.get_cron_from_config(frequency_config)
        if not cron_expr:
            return jsonify({
                'success': False,
                'error': '无法生成CRON表达式'
            }), 400
        
        # 验证CRON表达式
        is_valid, error_msg = CronValidator.validate_cron_expression(cron_expr)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'CRON表达式错误: {error_msg}'
            }), 400
        
        # 计算下次运行时间
        next_run = CronValidator.get_next_run_time(cron_expr)
        
        # 创建计划任务
        task = ScheduledTask(
            name=data['name'],
            description=data.get('description', ''),
            task_type=data['task_type'],
            frequency_type=data['frequency_type'],
            cron_expression=cron_expr,
            frequency_config=json.dumps(frequency_config),
            target_devices=json.dumps(data.get('target_devices', [])),
            backup_command=data.get('backup_command', 'show running-config'),
            is_active=data.get('is_active', True),
            next_run=next_run,
            created_by=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 添加到任务调度器
        if task.is_active:
            task_scheduler.add_job(task)
        
        return jsonify({
            'success': True,
            'message': '计划任务创建成功',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建计划任务失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_scheduled_task(task_id):
    """更新计划任务"""
    try:
        task = ScheduledTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '计划任务不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            task.name = data['name']
        if 'description' in data:
            task.description = data['description']
        if 'task_type' in data:
            task.task_type = data['task_type']
        if 'frequency_type' in data:
            task.frequency_type = data['frequency_type']
        if 'target_devices' in data:
            task.target_devices = json.dumps(data['target_devices'])
        if 'backup_command' in data:
            task.backup_command = data['backup_command']
        if 'is_active' in data:
            task.is_active = data['is_active']
        
        # 如果频率配置发生变化，重新计算CRON表达式
        if 'frequency_config' in data:
            frequency_config = data['frequency_config']
            is_valid, error_msg = FrequencyConfig.validate_config(frequency_config)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'频率配置错误: {error_msg}'
                }), 400
            
            cron_expr = FrequencyConfig.get_cron_from_config(frequency_config)
            if cron_expr:
                is_valid, error_msg = CronValidator.validate_cron_expression(cron_expr)
                if is_valid:
                    task.cron_expression = cron_expr
                    task.frequency_config = json.dumps(frequency_config)
                    task.next_run = CronValidator.get_next_run_time(cron_expr)
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 更新任务调度器
        task_scheduler.update_task(task)
        
        return jsonify({
            'success': True,
            'message': '计划任务更新成功',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'更新计划任务失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_scheduled_task(task_id):
    """删除计划任务"""
    try:
        task = ScheduledTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '计划任务不存在'
            }), 404
        
        # 删除关联的执行记录
        TaskExecution.query.filter_by(scheduled_task_id=task_id).delete()
        
        # 从任务调度器移除
        task_scheduler.remove_job(task_id)
        
        # 删除计划任务
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '计划任务删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'删除计划任务失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_scheduled_task(task_id):
    """启用/禁用计划任务"""
    try:
        task = ScheduledTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '计划任务不存在'
            }), 404
        
        task.is_active = not task.is_active
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 更新任务调度器
        task_scheduler.update_task(task)
        
        return jsonify({
            'success': True,
            'message': f'计划任务已{"启用" if task.is_active else "禁用"}',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'切换计划任务状态失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<int:task_id>/executions', methods=['GET'])
@login_required
def get_task_executions(task_id):
    """获取任务执行记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询执行记录
        executions = TaskExecution.query.filter_by(scheduled_task_id=task_id)\
            .order_by(TaskExecution.started_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        
        return jsonify({
            'success': True,
            'executions': [execution.to_dict() for execution in executions.items],
            'total': executions.total,
            'pages': executions.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取执行记录失败: {str(e)}'
        }), 500


@scheduler_bp.route('/options', methods=['GET'])
@login_required
def get_scheduler_options():
    """获取调度器选项"""
    try:
        return jsonify({
            'success': True,
            'frequency_options': ScheduleHelper.get_frequency_options(),
            'weekday_options': ScheduleHelper.get_weekday_options(),
            'task_type_options': ScheduleHelper.get_task_type_options()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取选项失败: {str(e)}'
        }), 500


@scheduler_bp.route('/tasks/<int:task_id>/status', methods=['GET'])
@login_required
def get_task_status(task_id):
    """获取任务调度状态"""
    try:
        task = ScheduledTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '计划任务不存在'
            }), 404
        
        # 获取调度器状态
        job_status = task_scheduler.get_job_status(task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'is_active': task.is_active,
            'scheduler_status': job_status,
            'last_run': task.last_run.isoformat() if task.last_run else None,
            'next_run': task.next_run.isoformat() if task.next_run else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取任务状态失败: {str(e)}'
        }), 500
