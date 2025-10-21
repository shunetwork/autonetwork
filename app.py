#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cisco设备配置备份系统
主应用程序入口
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import hashlib
import gzip
import shutil
from pathlib import Path

# 导入自定义模块
from models import db, User, Device, BackupTask, BackupLog
from device_manager import DeviceManager
from backup_service import BackupService
from scheduler import BackupScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 基础配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///backup_system.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 文件上传配置
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['BACKUP_FOLDER'] = 'backups'
    
    # 并发配置
    app.config['MAX_CONCURRENT_BACKUPS'] = int(os.environ.get('MAX_CONCURRENT_BACKUPS', 10))
    app.config['BACKUP_TIMEOUT'] = int(os.environ.get('BACKUP_TIMEOUT', 300))  # 5分钟
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from auth import auth_bp
    from api import api_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    return app

# 创建应用实例
app = create_app()

# 初始化服务
device_manager = DeviceManager()
backup_service = BackupService()
scheduler = BackupScheduler()

# 任务队列和线程池
task_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=app.config['MAX_CONCURRENT_BACKUPS'])

@app.route('/')
@login_required
def index():
    """首页 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/backup/single')
@login_required
def backup_single():
    """单设备备份页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/backup/batch')
@login_required
def backup_batch():
    """批量备份页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/history')
@login_required
def history():
    """备份历史页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/devices')
@login_required
def devices():
    """设备管理页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/settings')
@login_required
def settings():
    """系统设置页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/logs')
@login_required
def logs():
    """日志查看页面 - Vue 3前端"""
    return send_from_directory('static', 'index.html')

@app.route('/compare')
@login_required
def compare():
    """配置对比页面 - Vue 3 CDN版本"""
    return send_from_directory('static', 'compare_vue.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建默认管理员用户
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("创建默认管理员用户: admin/admin123")
    
    # 启动调度器
    scheduler.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
