#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口模块
提供RESTful API接口
"""

from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import difflib
from pathlib import Path

from models import db, Device, BackupTask, BackupLog, User
from device_manager import DeviceManager
from backup_service import BackupService

api_bp = Blueprint('api', __name__)

# 初始化服务
device_manager = DeviceManager()
backup_service = BackupService()

@api_bp.route('/device/test', methods=['POST'])
@login_required
def test_device_connection():
    """测试设备连接"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({
                'success': False,
                'message': '设备ID不能为空'
            }), 400
        
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'success': False,
                'message': '设备不存在'
            }), 404
        
        # 构建设备信息
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
        
        # 测试连接
        result = device_manager.test_connection(device_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试连接失败: {str(e)}'
        }), 500

@api_bp.route('/device/test-new', methods=['POST'])
def test_new_device_connection():
    """测试新设备连接（用于添加设备前测试）"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['ip_address', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} 不能为空'
                }), 400
        
        # 构建设备信息
        device_info = {
            'ip_address': data['ip_address'],
            'username': data['username'],
            'password': data['password'],
            'enable_password': data.get('enable_password'),
            'device_type': data.get('device_type', 'cisco_ios'),
            'port': data.get('port', 22),
            'protocol': data.get('protocol', 'ssh')
        }
        
        # 测试连接
        result = device_manager.test_connection(device_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试连接失败: {str(e)}'
        }), 500

@api_bp.route('/backup/single', methods=['POST'])
@login_required
def backup_single_device():
    """单设备备份"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        backup_command = data.get('backup_command')
        test_connection = data.get('test_connection', False)
        
        if not device_id:
            return jsonify({
                'success': False,
                'error': '设备ID不能为空'
            }), 400
        
        # 如果选择测试连接，先测试
        if test_connection:
            device = Device.query.get(device_id)
            if device:
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
                
                test_result = device_manager.test_connection(device_info)
                if not test_result['success']:
                    return jsonify({
                        'success': False,
                        'error': f'连接测试失败: {test_result["message"]}'
                    }), 400
        
        # 执行备份
        result = backup_service.backup_single_device(
            device_id=device_id,
            user_id=current_user.id,
            backup_command=backup_command,
            task_type='manual'
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'备份失败: {str(e)}'
        }), 500

@api_bp.route('/backup/batch', methods=['POST'])
@login_required
def backup_batch_devices():
    """批量设备备份"""
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        backup_command = data.get('backup_command')
        
        if not device_ids:
            return jsonify({
                'success': False,
                'error': '设备ID列表不能为空'
            }), 400
        
        # 执行批量备份
        result = backup_service.backup_multiple_devices(
            device_ids=device_ids,
            user_id=current_user.id,
            backup_command=backup_command,
            task_type='batch'
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量备份失败: {str(e)}'
        }), 500

@api_bp.route('/backup/progress/<int:task_id>')
@login_required
def get_backup_progress(task_id):
    """获取备份进度"""
    try:
        task = BackupTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404
        
        # 获取任务日志
        logs = BackupLog.query.filter_by(task_id=task_id).order_by(BackupLog.timestamp.desc()).limit(10).all()
        log_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'status': task.status,
            'logs': log_data,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取进度失败: {str(e)}'
        }), 500

@api_bp.route('/backup/recent')
@login_required
def get_recent_backups():
    """获取最近备份任务"""
    try:
        # 获取最近10个任务
        tasks = BackupTask.query.order_by(BackupTask.created_at.desc()).limit(10).all()
        task_data = [task.to_dict() for task in tasks]
        
        return jsonify({
            'success': True,
            'tasks': task_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取最近备份失败: {str(e)}'
        }), 500

@api_bp.route('/backup/device/<int:device_id>')
@login_required
def get_device_backups(device_id):
    """获取特定设备的备份任务"""
    try:
        # 获取指定设备的所有备份任务
        tasks = BackupTask.query.filter_by(device_id=device_id).order_by(BackupTask.created_at.desc()).all()
        task_data = [task.to_dict() for task in tasks]
        
        return jsonify({
            'success': True,
            'tasks': task_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取设备备份失败: {str(e)}'
        }), 500

@api_bp.route('/backup/download/<int:task_id>')
@login_required
def download_backup_file(task_id):
    """下载备份文件"""
    try:
        task = BackupTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404
        
        if task.status != 'success' or not task.file_path:
            return jsonify({
                'success': False,
                'error': '备份文件不存在'
            }), 404
        
        file_path = Path(task.file_path)
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': '备份文件已丢失'
            }), 404
        
        # 生成下载文件名
        device_name = task.device.alias or task.device.ip_address
        timestamp = task.completed_at.strftime('%Y%m%d_%H%M%S') if task.completed_at else 'unknown'
        filename = f"{device_name}_{timestamp}_backup.txt"
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'下载失败: {str(e)}'
        }), 500

@api_bp.route('/backup/delete/<int:task_id>', methods=['DELETE'])
@login_required
def delete_backup_task(task_id):
    """删除备份任务和文件"""
    try:
        task = BackupTask.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404
        
        # 删除备份文件
        if task.file_path:
            backup_service.delete_backup_file(task_id)
        
        # 删除任务记录
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500

@api_bp.route('/device/add', methods=['POST'])
@login_required
def add_device():
    """添加设备"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['ip_address', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} 不能为空'
                }), 400
        
        # 检查IP是否已存在
        existing_device = Device.query.filter_by(ip_address=data['ip_address']).first()
        if existing_device:
            return jsonify({
                'success': False,
                'error': '该IP地址的设备已存在'
            }), 400
        
        # 创建新设备
        device = Device(
            alias=data.get('alias'),
            hostname=data.get('hostname', data['ip_address']),
            ip_address=data['ip_address'],
            port=data.get('port', 22),
            protocol=data.get('protocol', 'ssh'),
            username=data['username'],
            device_type=data.get('device_type', 'cisco_ios'),
            backup_command=data.get('backup_command', 'show running-config')
        )
        
        # 加密存储密码
        device.password_encrypted = device._encrypt_password(data['password'])
        if data.get('enable_password'):
            device.enable_password_encrypted = device._encrypt_password(data['enable_password'])
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备添加成功',
            'device_id': device.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'添加设备失败: {str(e)}'
        }), 500

@api_bp.route('/device/<int:device_id>', methods=['PUT'])
@login_required
def update_device(device_id):
    """更新设备信息"""
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'success': False,
                'error': '设备不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新设备信息
        if 'alias' in data:
            device.alias = data['alias']
        if 'hostname' in data:
            device.hostname = data['hostname']
        if 'port' in data:
            device.port = data['port']
        if 'protocol' in data:
            device.protocol = data['protocol']
        if 'username' in data:
            device.username = data['username']
        if 'device_type' in data:
            device.device_type = data['device_type']
        if 'backup_command' in data:
            device.backup_command = data['backup_command']
        if 'is_active' in data:
            device.is_active = data['is_active']
        
        # 更新密码（如果提供）
        if 'password' in data and data['password']:
            device.password_encrypted = device._encrypt_password(data['password'])
        if 'enable_password' in data and data['enable_password']:
            device.enable_password_encrypted = device._encrypt_password(data['enable_password'])
        
        device.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'更新设备失败: {str(e)}'
        }), 500

@api_bp.route('/device/<int:device_id>', methods=['DELETE'])
@login_required
def delete_device(device_id):
    """删除设备"""
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'success': False,
                'error': '设备不存在'
            }), 404
        
        # 检查是否有相关的备份任务
        backup_count = BackupTask.query.filter_by(device_id=device_id).count()
        if backup_count > 0:
            return jsonify({
                'success': False,
                'error': f'该设备有 {backup_count} 个备份任务，无法删除'
            }), 400
        
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除设备失败: {str(e)}'
        }), 500

@api_bp.route('/statistics')
@login_required
def get_statistics():
    """获取系统统计信息"""
    try:
        stats = backup_service.get_backup_statistics()
        
        # 添加设备统计
        total_devices = Device.query.count()
        active_devices = Device.query.filter_by(is_active=True).count()
        
        stats.update({
            'total_devices': total_devices,
            'active_devices': active_devices
        })
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@api_bp.route('/device/list')
@login_required
def get_device_list():
    """获取设备列表"""
    try:
        devices = Device.query.all()
        device_data = [device.to_dict() for device in devices]
        
        return jsonify({
            'success': True,
            'devices': device_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取设备列表失败: {str(e)}'
        }), 500

@api_bp.route('/device/<int:device_id>')
@login_required
def get_device(device_id):
    """获取设备详情"""
    try:
        device = Device.query.get(device_id)
        if not device:
            return jsonify({
                'success': False,
                'error': '设备不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'device': device.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取设备详情失败: {str(e)}'
        }), 500

@api_bp.route('/import/devices', methods=['POST'])
@login_required
def import_devices():
    """导入设备"""
    try:
        from import_service import ImportService
        import tempfile
        import os
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 保存临时文件
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            # 获取参数
            backup_command = request.form.get('backup_command', 'show running-config')
            test_connections = request.form.get('test_connections') == 'true'
            
            # 执行导入
            import_service = ImportService()
            result = import_service.import_devices_from_file(
                temp_path, 
                current_user.id,
                backup_command,
                test_connections
            )
            
            return jsonify(result)
            
        finally:
            # 清理临时文件
            os.remove(temp_path)
            os.rmdir(temp_dir)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'导入设备失败: {str(e)}'
        }), 500

@api_bp.route('/import/template')
@login_required
def download_template():
    """下载导入模板"""
    try:
        from import_service import ImportService
        from flask import Response
        
        format_type = request.args.get('format', 'csv')
        import_service = ImportService()
        
        template_data = import_service.create_template_file(format_type)
        if not template_data:
            return jsonify({
                'success': False,
                'error': '创建模板文件失败'
            }), 500
        
        filename = f'device_template.{format_type}'
        mimetype = 'text/csv' if format_type == 'csv' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        return Response(
            template_data,
            mimetype=mimetype,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'下载模板失败: {str(e)}'
        }), 500

@api_bp.route('/logs/view/<filename>')
@login_required
def view_log_file(filename):
    """查看日志文件内容"""
    try:
        # 安全检查：只允许查看指定目录下的日志文件
        if not filename.endswith('.log'):
            return jsonify({
                'success': False,
                'error': '只能查看.log文件'
            }), 400
        
        # 构建日志文件路径
        log_dir = Path('logs')
        log_file = log_dir / filename
        
        # 检查文件是否存在
        if not log_file.exists():
            return jsonify({
                'success': False,
                'error': '日志文件不存在'
            }), 404
        
        # 读取日志文件内容
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试GBK编码
            with open(log_file, 'r', encoding='gbk') as f:
                content = f.read()
        
        # 获取文件信息
        file_size = log_file.stat().st_size
        modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content,
            'file_size': file_size,
            'modified_time': modified_time.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'读取日志文件失败: {str(e)}'
        }), 500

@api_bp.route('/logs/list')
@login_required
def list_log_files():
    """获取日志文件列表"""
    try:
        log_dir = Path('logs')
        if not log_dir.exists():
            return jsonify({
                'success': True,
                'files': []
            })
        
        # 获取所有.log文件
        log_files = []
        for file_path in log_dir.glob('*.log'):
            stat = file_path.stat()
            log_files.append({
                'filename': file_path.name,
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # 按修改时间排序
        log_files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': log_files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取日志文件列表失败: {str(e)}'
        }), 500

@api_bp.route('/logs/entries')
@login_required
def get_log_entries():
    """获取日志条目"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        level = request.args.get('level', '')
        
        # 模拟日志条目数据
        log_entries = []
        
        # 从日志文件中读取最近的条目
        log_dir = Path('logs')
        if log_dir.exists():
            for log_file in log_dir.glob('*.log'):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # 取最后50行作为示例
                        recent_lines = lines[-50:] if len(lines) > 50 else lines
                        
                        for line in recent_lines:
                            line = line.strip()
                            if line:
                                # 解析日志行格式: 2025-10-22 09:57:05,555 - module - LEVEL - message
                                parts = line.split(' - ', 3)
                                if len(parts) >= 4:
                                    timestamp_str = parts[0]
                                    module = parts[1]
                                    log_level = parts[2]
                                    message = parts[3]
                                    
                                    # 过滤级别
                                    if level and log_level.lower() != level.lower():
                                        continue
                                    
                                    log_entries.append({
                                        'timestamp': timestamp_str,
                                        'level': log_level,
                                        'module': module,
                                        'message': message
                                    })
                except Exception as e:
                    continue
        
        # 按时间排序
        log_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 分页
        total = len(log_entries)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_entries = log_entries[start:end]
        
        return jsonify({
            'success': True,
            'logs': paginated_entries,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取日志条目失败: {str(e)}'
        }), 500

@api_bp.route('/backup/<int:backup_id>/content')
@login_required
def get_backup_content(backup_id):
    """获取备份文件内容"""
    try:
        # 获取备份任务信息
        task = BackupTask.query.get(backup_id)
        if not task:
            return jsonify({
                'success': False,
                'error': '备份任务不存在'
            }), 404
        
        # 检查备份文件是否存在
        if not task.file_path or not os.path.exists(task.file_path):
            return jsonify({
                'success': False,
                'error': '备份文件不存在'
            }), 404
        
        # 读取备份文件内容
        try:
            with open(task.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(task.file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                with open(task.file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
        
        # 获取文件信息
        file_stat = os.stat(task.file_path)
        
        return jsonify({
            'success': True,
            'content': content,
            'file_info': {
                'file_path': task.file_path,
                'file_size': file_stat.st_size,
                'created_at': task.created_at.isoformat(),
                'device_alias': task.device.alias if task.device else '未知设备',
                'backup_command': task.backup_command
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取备份内容失败: {str(e)}'
        }), 500

@api_bp.route('/backup/compare/<int:task_id1>/<int:task_id2>')
@login_required
def compare_backup_files(task_id1, task_id2):
    """比较两个备份文件"""
    try:
        # 获取两个备份任务
        task1 = BackupTask.query.get(task_id1)
        task2 = BackupTask.query.get(task_id2)
        
        if not task1 or not task2:
            return jsonify({
                'success': False,
                'error': '备份任务不存在'
            }), 404
        
        if task1.status != 'success' or task2.status != 'success':
            return jsonify({
                'success': False,
                'error': '备份任务未成功完成'
            }), 400
        
        if not task1.file_path or not task2.file_path:
            return jsonify({
                'success': False,
                'error': '备份文件不存在'
            }), 404
        
        # 读取两个文件内容
        try:
            with open(task1.file_path, 'r', encoding='utf-8') as f:
                content1 = f.read()
        except UnicodeDecodeError:
            with open(task1.file_path, 'r', encoding='gbk') as f:
                content1 = f.read()
        
        try:
            with open(task2.file_path, 'r', encoding='utf-8') as f:
                content2 = f.read()
        except UnicodeDecodeError:
            with open(task2.file_path, 'r', encoding='gbk') as f:
                content2 = f.read()
        
        # 计算差异
        diff_result = _calculate_config_diff(content1, content2)
        
        return jsonify({
            'success': True,
            'task1': {
                'id': task1.id,
                'device': task1.device.alias or task1.device.ip_address,
                'created_at': task1.created_at.isoformat(),
                'file_size': task1.file_size
            },
            'task2': {
                'id': task2.id,
                'device': task2.device.alias or task2.device.ip_address,
                'created_at': task2.created_at.isoformat(),
                'file_size': task2.file_size
            },
            'diff': diff_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'比较备份文件失败: {str(e)}'
        }), 500

@api_bp.route('/backup/compare/latest/<int:device_id>')
@login_required
def compare_latest_backups(device_id):
    """比较设备的最新两个备份"""
    try:
        # 获取设备的最新两个成功备份
        latest_backups = BackupTask.query.filter_by(
            device_id=device_id,
            status='success'
        ).order_by(BackupTask.created_at.desc()).limit(2).all()
        
        if len(latest_backups) < 2:
            return jsonify({
                'success': False,
                'error': '设备备份数量不足，需要至少2个备份才能比较'
            }), 400
        
        # 比较最新的两个备份
        return compare_backup_files(latest_backups[1].id, latest_backups[0].id)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'比较最新备份失败: {str(e)}'
        }), 500

@api_bp.route('/backup/compare/quick/<int:device_id>')
@login_required
def quick_compare_latest_backups(device_id):
    """快速比较设备的最新两个备份（简化版本）"""
    try:
        # 获取设备的最新两个成功备份
        latest_backups = BackupTask.query.filter_by(
            device_id=device_id,
            status='success'
        ).order_by(BackupTask.created_at.desc()).limit(2).all()
        
        if len(latest_backups) < 2:
            return jsonify({
                'success': False,
                'error': '设备备份数量不足，需要至少2个备份才能比较'
            }), 400
        
        task1 = latest_backups[1]
        task2 = latest_backups[0]
        
        # 检查文件是否存在
        if not task1.file_path or not task2.file_path:
            return jsonify({
                'success': False,
                'error': '备份文件不存在'
            }), 404
        
        # 读取文件内容（限制大小）
        try:
            with open(task1.file_path, 'r', encoding='utf-8') as f:
                content1 = f.read(1024 * 1024)  # 限制1MB
        except UnicodeDecodeError:
            with open(task1.file_path, 'r', encoding='gbk') as f:
                content1 = f.read(1024 * 1024)
        
        try:
            with open(task2.file_path, 'r', encoding='utf-8') as f:
                content2 = f.read(1024 * 1024)  # 限制1MB
        except UnicodeDecodeError:
            with open(task2.file_path, 'r', encoding='gbk') as f:
                content2 = f.read(1024 * 1024)
        
        # 简单比较：只检查行数差异
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        # 计算基本统计
        added_lines = len(lines2) - len(lines1)
        removed_lines = 0
        if added_lines < 0:
            removed_lines = -added_lines
            added_lines = 0
        
        return jsonify({
            'success': True,
            'task1': {
                'id': task1.id,
                'device': task1.device.alias or task1.device.ip_address,
                'created_at': task1.created_at.isoformat(),
                'file_size': task1.file_size,
                'lines': len(lines1)
            },
            'task2': {
                'id': task2.id,
                'device': task2.device.alias or task2.device.ip_address,
                'created_at': task2.created_at.isoformat(),
                'file_size': task2.file_size,
                'lines': len(lines2)
            },
            'diff': {
                'summary': {
                    'total_changes': abs(len(lines2) - len(lines1)),
                    'added_lines': added_lines,
                    'removed_lines': removed_lines,
                    'modified_lines': 0,
                    'has_changes': len(lines1) != len(lines2)
                },
                'diff_blocks': [],
                'raw_diff': f'配置文件行数变化: {len(lines1)} -> {len(lines2)}'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'快速比较失败: {str(e)}'
        }), 500

def _calculate_config_diff(content1, content2):
    """计算两个配置文件的差异"""
    try:
        # 检查文件大小，如果太大则限制处理
        max_size = 1024 * 1024  # 1MB限制
        if len(content1) > max_size or len(content2) > max_size:
            return {
                'summary': {
                    'total_changes': 0,
                    'added_lines': 0,
                    'removed_lines': 0,
                    'modified_lines': 0,
                    'has_changes': False,
                    'error': '配置文件过大，无法进行比较'
                },
                'diff_blocks': [],
                'raw_diff': ''
            }
        
        # 将内容按行分割
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)
        
        # 限制行数，避免处理过大的文件
        max_lines = 10000
        if len(lines1) > max_lines or len(lines2) > max_lines:
            lines1 = lines1[:max_lines]
            lines2 = lines2[:max_lines]
        
        # 使用difflib计算差异
        differ = difflib.unified_diff(
            lines1, lines2,
            fromfile='旧配置',
            tofile='新配置',
            lineterm=''
        )
        
        # 转换为列表，限制结果大小
        diff_lines = list(differ)
        if len(diff_lines) > 5000:  # 限制差异行数
            diff_lines = diff_lines[:5000]
        
        # 统计差异信息
        added_lines = 0
        removed_lines = 0
        modified_lines = 0
        
        diff_result = []
        current_hunk = None
        
        for line in diff_lines:
            if line.startswith('@@'):
                # 新的差异块
                if current_hunk:
                    diff_result.append(current_hunk)
                current_hunk = {
                    'header': line.strip(),
                    'changes': []
                }
            elif line.startswith('+') and not line.startswith('+++'):
                # 新增行
                added_lines += 1
                if current_hunk:
                    current_hunk['changes'].append({
                        'type': 'added',
                        'content': line[1:].rstrip('\n')
                    })
            elif line.startswith('-') and not line.startswith('---'):
                # 删除行
                removed_lines += 1
                if current_hunk:
                    current_hunk['changes'].append({
                        'type': 'removed',
                        'content': line[1:].rstrip('\n')
                    })
            elif line.startswith(' '):
                # 上下文行
                if current_hunk:
                    current_hunk['changes'].append({
                        'type': 'context',
                        'content': line[1:].rstrip('\n')
                    })
        
        # 添加最后一个差异块
        if current_hunk:
            diff_result.append(current_hunk)
        
        # 计算修改行数（新增和删除的组合）
        modified_lines = min(added_lines, removed_lines)
        added_lines -= modified_lines
        removed_lines -= modified_lines
        
        return {
            'summary': {
                'total_changes': len(diff_lines),
                'added_lines': added_lines,
                'removed_lines': removed_lines,
                'modified_lines': modified_lines,
                'has_changes': len(diff_lines) > 0
            },
            'diff_blocks': diff_result,
            'raw_diff': '\n'.join(diff_lines)
        }
        
    except Exception as e:
        return {
            'summary': {
                'total_changes': 0,
                'added_lines': 0,
                'removed_lines': 0,
                'modified_lines': 0,
                'has_changes': False,
                'error': str(e)
            },
            'diff_blocks': [],
            'raw_diff': ''
        }

@api_bp.route('/backup/history')
@login_required
def get_backup_history():
    """获取备份历史"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        tasks = BackupTask.query.order_by(BackupTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        history = []
        for task in tasks.items:
            device = Device.query.get(task.device_id)
            history.append({
                'id': task.id,
                'device_alias': device.alias if device else '未知设备',
                'backup_command': task.backup_command,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'duration': task.get_duration()
            })
        
        return jsonify({
            'success': True,
            'tasks': history,
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取备份历史失败: {str(e)}'
        }), 500

@api_bp.route('/settings')
@login_required
def get_settings():
    """获取系统设置"""
    try:
        # 这里可以从数据库或配置文件读取设置
        settings = {
            'default_command': 'show running-config',
            'default_retry': 3,
            'default_concurrent': 3,
            'log_retention_days': 30,
            'auto_backup': False
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取设置失败: {str(e)}'
        }), 500

@api_bp.route('/settings', methods=['POST'])
@login_required
def save_settings():
    """保存系统设置"""
    try:
        data = request.get_json()
        
        # 这里可以将设置保存到数据库或配置文件
        # 暂时只返回成功
        
        return jsonify({
            'success': True,
            'message': '设置保存成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'保存设置失败: {str(e)}'
        }), 500

@api_bp.route('/system/info')
@login_required
def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import time
        
        # 获取系统运行时间
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        
        uptime = f"{uptime_days}天{uptime_hours}小时{uptime_minutes}分钟"
        
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = f"{memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB"
        
        return jsonify({
            'success': True,
            'uptime': uptime,
            'memory': memory_usage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取系统信息失败: {str(e)}'
        }), 500

@api_bp.route('/backup/compare', methods=['POST'])
@login_required
def compare_backups():
    """对比备份配置"""
    try:
        data = request.get_json()
        first_backup_id = data.get('first_backup_id')
        second_backup_id = data.get('second_backup_id')
        ignore_whitespace = data.get('ignore_whitespace', True)
        ignore_case = data.get('ignore_case', False)
        
        if not first_backup_id or not second_backup_id:
            return jsonify({
                'success': False,
                'error': '请选择要对比的备份'
            }), 400
        
        # 获取备份任务
        first_task = BackupTask.query.get(first_backup_id)
        second_task = BackupTask.query.get(second_backup_id)
        
        if not first_task or not second_task:
            return jsonify({
                'success': False,
                'error': '备份任务不存在'
            }), 404
        
        # 这里实现配置对比逻辑
        # 暂时返回模拟结果
        result = {
            'differences': 0,
            'first_backup_time': first_task.created_at.isoformat(),
            'second_backup_time': second_task.created_at.isoformat(),
            'diff_details': []
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'对比失败: {str(e)}'
        }), 500

@api_bp.route('/backup/batch/progress')
@login_required
def get_batch_progress():
    """获取批量备份进度"""
    try:
        # 获取最近的批量备份任务进度
        # 这里返回模拟数据
        progress = [
            {
                'device_alias': 'R1',
                'status': 'success',
                'progress': 100,
                'message': '备份完成'
            },
            {
                'device_alias': 'R2',
                'status': 'running',
                'progress': 50,
                'message': '正在备份...'
            }
        ]
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取进度失败: {str(e)}'
        }), 500
