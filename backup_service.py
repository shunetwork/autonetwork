#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份服务
负责执行设备配置备份、文件存储、差异比较等功能
"""

import os
import hashlib
import gzip
import shutil
import difflib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import db, Device, BackupTask, BackupLog
from device_manager import DeviceManager

logger = logging.getLogger(__name__)

class BackupService:
    """备份服务类"""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.backup_base_path = Path('backups')
        self.backup_base_path.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def backup_single_device(self, device_id: int, user_id: int, 
                           backup_command: str = None, 
                           task_type: str = 'manual') -> Dict[str, Any]:
        """备份单个设备"""
        try:
            # 获取设备信息
            device = Device.query.get(device_id)
            if not device:
                return {
                    'success': False,
                    'error': '设备不存在',
                    'task_id': None
                }
            
            # 创建备份任务
            task = BackupTask(
                device_id=device_id,
                user_id=user_id,
                task_type=task_type,
                status='pending',
                backup_command=backup_command or device.backup_command,
                max_retries=3
            )
            db.session.add(task)
            db.session.commit()
            
            # 异步执行备份
            future = self.executor.submit(self._execute_backup, task.id)
            
            return {
                'success': True,
                'task_id': task.id,
                'message': '备份任务已提交'
            }
            
        except Exception as e:
            logger.error(f"创建备份任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'task_id': None
            }
    
    def backup_multiple_devices(self, device_ids: List[int], user_id: int,
                               backup_command: str = None,
                               task_type: str = 'batch') -> Dict[str, Any]:
        """批量备份设备"""
        try:
            tasks = []
            
            # 为每个设备创建备份任务
            for device_id in device_ids:
                device = Device.query.get(device_id)
                if device and device.is_active:
                    task = BackupTask(
                        device_id=device_id,
                        user_id=user_id,
                        task_type=task_type,
                        status='pending',
                        backup_command=backup_command or device.backup_command,
                        max_retries=3
                    )
                    db.session.add(task)
                    tasks.append(task)
            
            db.session.commit()
            
            # 异步执行所有备份任务
            futures = []
            for task in tasks:
                future = self.executor.submit(self._execute_backup, task.id)
                futures.append(future)
            
            return {
                'success': True,
                'task_count': len(tasks),
                'task_ids': [task.id for task in tasks],
                'message': f'已提交 {len(tasks)} 个备份任务'
            }
            
        except Exception as e:
            logger.error(f"批量备份失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'task_count': 0
            }
    
    def _execute_backup(self, task_id: int):
        """执行备份任务"""
        from app import app
        
        with app.app_context():
            logger.info(f"开始执行备份任务 {task_id}")
            try:
                task = BackupTask.query.get(task_id)
                if not task:
                    logger.error(f"任务 {task_id} 不存在")
                    return
                
                device = task.device
                if not device:
                    logger.error(f"任务 {task_id} 的设备不存在")
                    self._update_task_status(task, 'failed', '设备不存在')
                    return
                    
                logger.info(f"任务 {task_id} 开始备份设备 {device.ip_address}")
                
                # 更新任务状态
                self._update_task_status(task, 'running')
                self._log_task(task, 'info', f'开始备份设备 {device.ip_address}')
                
                # 获取设备连接
                device_info = {
                    'id': device.id,
                    'ip_address': device.ip_address,
                    'username': device.username,
                    'password_encrypted': device.password_encrypted,
                    'enable_password_encrypted': device.enable_password_encrypted,
                    'device_type': device.device_type,
                    'port': device.port,
                    'protocol': device.protocol
                }
                
                connection = self.device_manager.get_connection(device_info)
                if not connection:
                    self._update_task_status(task, 'failed', '无法建立设备连接')
                    return
                
                # 执行备份命令
                result = connection.execute_command(task.backup_command)
                if not result['success']:
                    self._update_task_status(task, 'failed', f"命令执行失败: {result['error']}")
                    return
                
                # 生成备份文件路径
                file_path = self._generate_backup_path(device, task)
                
                # 保存备份文件
                backup_content = result['output']
                if not self._save_backup_file(file_path, backup_content):
                    self._update_task_status(task, 'failed', '保存备份文件失败')
                    return
                
                # 计算文件哈希
                file_hash = self._calculate_file_hash(file_path)
                file_size = os.path.getsize(file_path)
                
                # 更新任务状态
                task.status = 'success'
                task.file_path = str(file_path)
                task.file_size = file_size
                task.file_hash = file_hash
                task.completed_at = datetime.utcnow()
                
                # 更新设备最后备份信息
                device.last_backup = datetime.utcnow()
                device.last_backup_status = 'success'
                
                db.session.commit()
                
                self._log_task(task, 'info', f'备份完成，文件大小: {file_size} 字节')
                
                # 执行差异比较
                self._compare_with_previous_backup(device, file_path)
                
            except Exception as e:
                logger.error(f"执行备份任务 {task_id} 失败: {str(e)}")
                self._update_task_status(task, 'failed', str(e))
            finally:
                # 释放设备连接
                if 'device' in locals() and device:
                    self.device_manager.release_connection(device.id)
    
    def _update_task_status(self, task: BackupTask, status: str, error_message: str = None):
        """更新任务状态"""
        try:
            task.status = status
            if error_message:
                task.error_message = error_message
            if status == 'running':
                task.started_at = datetime.utcnow()
            elif status in ['success', 'failed']:
                task.completed_at = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            logger.error(f"更新任务状态失败: {str(e)}")
    
    def _log_task(self, task: BackupTask, level: str, message: str):
        """记录任务日志"""
        try:
            log = BackupLog(
                task_id=task.id,
                level=level,
                message=message
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.error(f"记录任务日志失败: {str(e)}")
    
    def _generate_backup_path(self, device: Device, task: BackupTask) -> Path:
        """生成备份文件路径"""
        # 使用设备别名或IP作为目录名
        device_name = device.alias or device.ip_address.replace(':', '_')
        device_dir = self.backup_base_path / device_name
        device_dir.mkdir(exist_ok=True)
        
        # 生成文件名：YYYYMMDD_HHMMSS_sh_run.txt
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        command_name = task.backup_command.replace(' ', '_').replace('-', '_')
        filename = f"{timestamp}_{command_name}.txt"
        
        return device_dir / filename
    
    def _save_backup_file(self, file_path: Path, content: str) -> bool:
        """保存备份文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 可选：压缩文件
            if os.environ.get('COMPRESS_BACKUPS', 'false').lower() == 'true':
                compressed_path = file_path.with_suffix('.txt.gz')
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(file_path)
                file_path = compressed_path
            
            return True
        except Exception as e:
            logger.error(f"保存备份文件失败: {str(e)}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件SHA256哈希"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败: {str(e)}")
            return ""
    
    def _compare_with_previous_backup(self, device: Device, current_file_path: Path):
        """与上次备份进行比较"""
        try:
            # 查找设备的上次成功备份
            previous_task = BackupTask.query.filter(
                BackupTask.device_id == device.id,
                BackupTask.status == 'success',
                BackupTask.id != current_file_path.stem.split('_')[0]  # 排除当前任务
            ).order_by(BackupTask.completed_at.desc()).first()
            
            if not previous_task or not previous_task.file_path:
                return
            
            previous_file_path = Path(previous_task.file_path)
            if not previous_file_path.exists():
                return
            
            # 读取文件内容进行比较
            with open(current_file_path, 'r', encoding='utf-8') as f:
                current_content = f.readlines()
            
            with open(previous_file_path, 'r', encoding='utf-8') as f:
                previous_content = f.readlines()
            
            # 生成差异报告
            diff = list(difflib.unified_diff(
                previous_content,
                current_content,
                fromfile=f'previous_{previous_file_path.name}',
                tofile=f'current_{current_file_path.name}',
                lineterm=''
            ))
            
            if diff:
                # 保存差异报告
                diff_file_path = current_file_path.with_suffix('.diff')
                with open(diff_file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(diff))
                
                logger.info(f"生成差异报告: {diff_file_path}")
            
        except Exception as e:
            logger.error(f"比较备份文件失败: {str(e)}")
    
    def get_backup_file(self, task_id: int) -> Optional[Path]:
        """获取备份文件路径"""
        task = BackupTask.query.get(task_id)
        if task and task.file_path:
            file_path = Path(task.file_path)
            if file_path.exists():
                return file_path
        return None
    
    def delete_backup_file(self, task_id: int) -> bool:
        """删除备份文件"""
        try:
            task = BackupTask.query.get(task_id)
            if task and task.file_path:
                file_path = Path(task.file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"已删除备份文件: {file_path}")
                    return True
        except Exception as e:
            logger.error(f"删除备份文件失败: {str(e)}")
        return False
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        try:
            total_tasks = BackupTask.query.count()
            success_tasks = BackupTask.query.filter_by(status='success').count()
            failed_tasks = BackupTask.query.filter_by(status='failed').count()
            running_tasks = BackupTask.query.filter_by(status='running').count()
            
            # 计算总备份大小
            total_size = db.session.query(db.func.sum(BackupTask.file_size)).filter(
                BackupTask.status == 'success'
            ).scalar() or 0
            
            return {
                'total_tasks': total_tasks,
                'success_tasks': success_tasks,
                'failed_tasks': failed_tasks,
                'running_tasks': running_tasks,
                'total_size': total_size,
                'success_rate': (success_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取备份统计失败: {str(e)}")
            return {}
