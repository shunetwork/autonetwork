#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关联关系
    backup_tasks = db.relationship('BackupTask', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Device(db.Model):
    """设备模型"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(100), nullable=True)  # 设备别名
    hostname = db.Column(db.String(255), nullable=False)  # 主机名或IP
    ip_address = db.Column(db.String(45), nullable=False)  # 支持IPv4/IPv6
    port = db.Column(db.Integer, default=22)
    protocol = db.Column(db.String(10), default='ssh')  # ssh, telnet
    username = db.Column(db.String(100), nullable=False)
    password_encrypted = db.Column(db.Text, nullable=False)  # 加密存储的密码
    enable_password_encrypted = db.Column(db.Text, nullable=True)  # 加密存储的enable密码
    device_type = db.Column(db.String(50), default='cisco_ios')  # cisco_ios, cisco_xe, cisco_nxos
    backup_command = db.Column(db.String(200), default='show running-config')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_backup = db.Column(db.DateTime)
    last_backup_status = db.Column(db.String(20))  # success, failed
    
    # 关联关系
    backup_tasks = db.relationship('BackupTask', backref='device', lazy='dynamic')
    
    def _encrypt_password(self, password: str) -> str:
        """加密密码"""
        try:
            from cryptography.fernet import Fernet
            import base64
            import os
            
            # 从环境变量获取加密密钥
            key = os.environ.get('ENCRYPTION_KEY')
            if not key:
                key = 'default-encryption-key-change-in-production'
            
            # 将密钥转换为Fernet密钥
            key_bytes = key.encode()[:32].ljust(32, b'0')
            fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
            
            # 加密密码
            encrypted = fernet.encrypt(password.encode())
            return encrypted.decode()
        except Exception as e:
            # 如果加密失败，返回原密码
            return password
    
    def to_dict(self):
        """转换为字典（不包含敏感信息）"""
        return {
            'id': self.id,
            'alias': self.alias,
            'hostname': self.hostname,
            'ip_address': self.ip_address,
            'port': self.port,
            'protocol': self.protocol,
            'device_type': self.device_type,
            'backup_command': self.backup_command,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_backup': self.last_backup.isoformat() if self.last_backup else None,
            'last_backup_status': self.last_backup_status
        }

class BackupTask(db.Model):
    """备份任务模型"""
    __tablename__ = 'backup_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_type = db.Column(db.String(20), default='manual')  # manual, scheduled, batch
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed, cancelled
    backup_command = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.BigInteger)
    file_hash = db.Column(db.String(64))  # SHA256哈希
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    
    # 关联关系
    logs = db.relationship('BackupLog', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_alias': self.device.alias if self.device else None,
            'device_ip': self.device.ip_address if self.device else None,
            'device': self.device.alias if self.device else None,  # 添加device字段
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'task_type': self.task_type,
            'status': self.status,
            'backup_command': self.backup_command,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'duration': self.get_duration()
        }
    
    def get_duration(self):
        """获取任务执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class BackupLog(db.Model):
    """备份日志模型"""
    __tablename__ = 'backup_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('backup_tasks.id'), nullable=False)
    level = db.Column(db.String(20), default='info')  # info, warning, error, debug
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class BackupSchedule(db.Model):
    """备份计划模型"""
    __tablename__ = 'backup_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cron_expression = db.Column(db.String(100), nullable=False)  # CRON表达式
    device_ids = db.Column(db.Text)  # JSON格式存储设备ID列表
    backup_command = db.Column(db.String(200), default='show running-config')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cron_expression': self.cron_expression,
            'device_ids': json.loads(self.device_ids) if self.device_ids else [],
            'backup_command': self.backup_command,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
