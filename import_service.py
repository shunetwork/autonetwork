#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入服务
处理CSV/Excel文件导入和设备批量添加
"""

import pandas as pd
import io
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path
import hashlib
import base64
from cryptography.fernet import Fernet
import os

from models import db, Device

logger = logging.getLogger(__name__)

class ImportService:
    """导入服务类"""
    
    def __init__(self):
        self.required_fields = ['ip_address', 'username', 'password']
        self.optional_fields = ['alias', 'port', 'protocol', 'device_type', 'enable_password']
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    def import_devices_from_file(self, file_path: str, user_id: int, 
                               backup_command: str = None, 
                               test_connections: bool = False) -> Dict[str, Any]:
        """从文件导入设备"""
        try:
            # 检查文件格式
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'不支持的文件格式: {file_ext}'
                }
            
            # 读取文件
            if file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
            
            # 验证必填字段
            missing_fields = []
            for field in self.required_fields:
                if field not in df.columns:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'缺少必填字段: {", ".join(missing_fields)}'
                }
            
            # 处理导入
            results = {
                'success_count': 0,
                'error_count': 0,
                'skipped_count': 0,
                'errors': [],
                'devices': []
            }
            
            for index, row in df.iterrows():
                try:
                    # 检查IP是否已存在
                    existing_device = Device.query.filter_by(ip_address=row['ip_address']).first()
                    if existing_device:
                        results['skipped_count'] += 1
                        results['errors'].append(f"第{index+1}行: IP {row['ip_address']} 已存在")
                        continue
                    
                    # 创建设备
                    device = Device(
                        alias=row.get('alias', ''),
                        hostname=row.get('hostname', row['ip_address']),
                        ip_address=row['ip_address'],
                        port=int(row.get('port', 22)),
                        protocol=row.get('protocol', 'ssh'),
                        username=row['username'],
                        device_type=row.get('device_type', 'cisco_ios'),
                        backup_command=backup_command or row.get('backup_command', 'show running-config'),
                        is_active=True
                    )
                    
                    # 加密存储密码
                    device.password_encrypted = self._encrypt_password(row['password'])
                    if pd.notna(row.get('enable_password')):
                        device.enable_password_encrypted = self._encrypt_password(row['enable_password'])
                    
                    # 如果选择测试连接，先测试
                    if test_connections:
                        test_result = self._test_device_connection(device)
                        if not test_result['success']:
                            results['error_count'] += 1
                            results['errors'].append(f"第{index+1}行: {test_result['error']}")
                            continue
                    
                    db.session.add(device)
                    results['success_count'] += 1
                    results['devices'].append(device.to_dict())
                    
                except Exception as e:
                    results['error_count'] += 1
                    results['errors'].append(f"第{index+1}行: {str(e)}")
            
            # 提交数据库更改
            if results['success_count'] > 0:
                db.session.commit()
            
            return {
                'success': True,
                'message': f'导入完成: 成功 {results["success_count"]} 个, 失败 {results["error_count"]} 个, 跳过 {results["skipped_count"]} 个',
                **results
            }
            
        except Exception as e:
            logger.error(f"导入设备失败: {str(e)}")
            return {
                'success': False,
                'error': f'导入失败: {str(e)}'
            }
    
    def create_template_file(self, format: str = 'csv') -> bytes:
        """创建模板文件"""
        try:
            # 创建示例数据
            sample_data = {
                'ip_address': ['192.168.1.1', '192.168.1.2'],
                'username': ['admin', 'admin'],
                'password': ['password123', 'password456'],
                'alias': ['Router-01', 'Switch-01'],
                'port': [22, 22],
                'protocol': ['ssh', 'ssh'],
                'device_type': ['cisco_ios', 'cisco_ios'],
                'enable_password': ['enable123', '']
            }
            
            df = pd.DataFrame(sample_data)
            
            if format.lower() == 'csv':
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8')
                return output.getvalue().encode('utf-8')
            else:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Devices')
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"创建模板文件失败: {str(e)}")
            return None
    
    def _encrypt_password(self, password: str) -> str:
        """加密密码"""
        try:
            # 从环境变量获取加密密钥
            key = os.environ.get('ENCRYPTION_KEY')
            if not key:
                key = 'default-key-change-in-production'
            
            # 将密钥转换为Fernet密钥
            key_bytes = key.encode()[:32].ljust(32, b'0')
            fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
            
            # 加密密码
            encrypted = fernet.encrypt(password.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"密码加密失败: {str(e)}")
            return password  # 如果加密失败，返回原密码
    
    def _test_device_connection(self, device: Device) -> Dict[str, Any]:
        """测试设备连接"""
        try:
            from device_manager import DeviceManager
            device_manager = DeviceManager()
            
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
            
            result = device_manager.test_connection(device_info)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_import_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证导入数据"""
        errors = []
        warnings = []
        
        for i, row in enumerate(data):
            # 检查必填字段
            for field in self.required_fields:
                if not row.get(field):
                    errors.append(f"第{i+1}行: 缺少必填字段 {field}")
            
            # 检查IP地址格式
            ip = row.get('ip_address', '')
            if ip and not self._is_valid_ip(ip):
                errors.append(f"第{i+1}行: 无效的IP地址 {ip}")
            
            # 检查端口号
            port = row.get('port', 22)
            if not isinstance(port, int) or port < 1 or port > 65535:
                warnings.append(f"第{i+1}行: 端口号 {port} 可能无效")
            
            # 检查协议
            protocol = row.get('protocol', 'ssh')
            if protocol not in ['ssh', 'telnet']:
                warnings.append(f"第{i+1}行: 不支持的协议 {protocol}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        import socket
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                return True
            except socket.error:
                return False


