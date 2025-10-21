#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备连接管理器
负责与Cisco设备的SSH/Telnet连接和命令执行
"""

import logging
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
try:
    from netmiko.ssh_exception import SSHException
except ImportError:
    from paramiko.ssh_exception import SSHException
import paramiko
from cryptography.fernet import Fernet
import base64
import os

logger = logging.getLogger(__name__)

class DeviceConnection:
    """设备连接类"""
    
    def __init__(self, device_info: Dict[str, Any]):
        self.device_info = device_info
        self.connection = None
        self.is_connected = False
        self.lock = threading.Lock()
    
    def connect(self) -> bool:
        """建立设备连接"""
        try:
            with self.lock:
                if self.is_connected:
                    return True
                
                # 解密密码
                password = self._decrypt_password(self.device_info.get('password_encrypted'))
                enable_password = None
                if self.device_info.get('enable_password_encrypted'):
                    enable_password = self._decrypt_password(self.device_info.get('enable_password_encrypted'))
                
                # 构建连接参数
                connection_params = {
                    'device_type': self.device_info.get('device_type', 'cisco_ios'),
                    'host': self.device_info.get('ip_address'),
                    'username': self.device_info.get('username'),
                    'password': password,
                    'port': self.device_info.get('port', 22),
                    'timeout': 60,  # 增加连接超时时间
                    'session_timeout': 120,  # 增加会话超时时间
                    'banner_timeout': 30,  # 增加banner超时时间
                    'auth_timeout': 60,  # 增加认证超时时间
                }
                
                # 添加enable密码
                if enable_password:
                    connection_params['secret'] = enable_password
                
                # 根据协议选择连接方式
                if self.device_info.get('protocol', 'ssh').lower() == 'telnet':
                    connection_params['device_type'] = 'cisco_ios_telnet'
                
                # 建立连接
                self.connection = ConnectHandler(**connection_params)
                self.is_connected = True
                
                logger.info(f"成功连接到设备 {self.device_info.get('ip_address')}")
                return True
                
        except NetMikoAuthenticationException as e:
            logger.error(f"设备 {self.device_info.get('ip_address')} 认证失败: {str(e)}")
            return False
        except NetMikoTimeoutException as e:
            logger.error(f"设备 {self.device_info.get('ip_address')} 连接超时: {str(e)}")
            return False
        except SSHException as e:
            logger.error(f"设备 {self.device_info.get('ip_address')} SSH错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"设备 {self.device_info.get('ip_address')} 连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开设备连接"""
        try:
            with self.lock:
                if self.connection and self.is_connected:
                    self.connection.disconnect()
                    self.is_connected = False
                    logger.info(f"已断开设备 {self.device_info.get('ip_address')} 的连接")
        except Exception as e:
            logger.error(f"断开设备连接时出错: {str(e)}")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """执行设备命令"""
        if not self.is_connected:
            if not self.connect():
                return {
                    'success': False,
                    'error': '设备连接失败',
                    'output': ''
                }
        
        try:
            with self.lock:
                # 进入特权模式（如果需要）
                if command.startswith('show') and self.device_info.get('enable_password_encrypted'):
                    self.connection.enable()
                
                # 执行命令，增加超时时间和延迟
                if command.lower().startswith('show running-config'):
                    # 对于show running-config命令，使用更长的超时时间
                    output = self.connection.send_command(command, delay_factor=4, max_loops=2000)
                else:
                    output = self.connection.send_command(command, delay_factor=2)
                
                return {
                    'success': True,
                    'output': output,
                    'error': None
                }
                
        except Exception as e:
            logger.error(f"执行命令失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'output': ''
            }
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """解密密码"""
        try:
            # 从环境变量获取加密密钥
            key = os.environ.get('ENCRYPTION_KEY')
            if not key:
                # 如果没有设置密钥，使用默认密钥（生产环境应该设置自己的密钥）
                key = 'default-encryption-key-change-in-production'
            
            # 将密钥转换为Fernet密钥
            key_bytes = key.encode()[:32].ljust(32, b'0')
            fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
            
            # 解密密码
            decrypted = fernet.decrypt(encrypted_password.encode())
            result = decrypted.decode()
            logger.info(f"密码解密成功，长度: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"密码解密失败: {str(e)}")
            logger.error(f"加密密码长度: {len(encrypted_password)}")
            return encrypted_password  # 如果解密失败，返回原密码

class DeviceManager:
    """设备管理器"""
    
    def __init__(self):
        self.connections = {}  # 存储活跃连接
        self.connection_locks = {}  # 连接锁
        self.max_connections = 10  # 最大并发连接数
    
    def get_connection(self, device_info: Dict[str, Any]) -> DeviceConnection:
        """获取设备连接"""
        device_id = device_info.get('id')
        device_ip = device_info.get('ip_address')
        
        # 检查是否已有连接
        if device_id in self.connections:
            connection = self.connections[device_id]
            if connection.is_connected:
                return connection
        
        # 创建新连接
        connection = DeviceConnection(device_info)
        if connection.connect():
            self.connections[device_id] = connection
            return connection
        else:
            return None
    
    def release_connection(self, device_id: int):
        """释放设备连接"""
        if device_id in self.connections:
            connection = self.connections[device_id]
            connection.disconnect()
            del self.connections[device_id]
    
    def test_connection(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """测试设备连接"""
        try:
            # 处理密码加密
            if 'password' in device_info and not device_info.get('password_encrypted'):
                # 如果是明文密码，需要加密
                from cryptography.fernet import Fernet
                import base64
                import os
                
                key = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')
                key_bytes = key.encode()[:32].ljust(32, b'0')
                fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
                device_info['password_encrypted'] = fernet.encrypt(device_info['password'].encode()).decode()
            
            if 'enable_password' in device_info and not device_info.get('enable_password_encrypted'):
                # 如果是明文enable密码，需要加密
                from cryptography.fernet import Fernet
                import base64
                import os
                
                key = os.environ.get('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')
                key_bytes = key.encode()[:32].ljust(32, b'0')
                fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
                device_info['enable_password_encrypted'] = fernet.encrypt(device_info['enable_password'].encode()).decode()
            
            connection = DeviceConnection(device_info)
            if connection.connect():
                # 执行简单命令测试
                result = connection.execute_command('show version')
                connection.disconnect()
                
                return {
                    'success': result['success'],
                    'message': '连接测试成功' if result['success'] else '连接测试失败',
                    'output': result['output'] if result['success'] else result['error']
                }
            else:
                return {
                    'success': False,
                    'message': '无法建立连接',
                    'output': ''
                }
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return {
                'success': False,
                'message': f'连接测试异常: {str(e)}',
                'output': ''
            }
    
    def cleanup_connections(self):
        """清理所有连接"""
        for device_id, connection in list(self.connections.items()):
            try:
                connection.disconnect()
            except Exception as e:
                logger.error(f"清理连接 {device_id} 时出错: {str(e)}")
        
        self.connections.clear()
        logger.info("已清理所有设备连接")
