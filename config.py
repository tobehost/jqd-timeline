"""
TimelineJS 配置文件
文件名: config.py
"""

import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库配置
DATABASE = {
    'path': os.path.join(BASE_DIR, 'static', 'data', 'timeline.db'),
    'json_output': os.path.join(BASE_DIR, 'static', 'data', 'tl-story.json'),
    'backup_dir': os.path.join(BASE_DIR, 'static', 'data', 'backups')
}

# 服务器配置
SERVER = {
    'host': 'localhost',
    'port': 8000,
    'debug': True
}

# API配置
API = {
    'prefix': '/api',
    'cors_origins': ['*'],
    'rate_limit': '100 per minute'
}

# 文件上传配置
UPLOAD = {
    'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm', '.mp3'],
    'max_size': 10 * 1024 * 1024,  # 10MB
    'upload_folder': os.path.join(BASE_DIR, 'static', 'uploads')
}

# 初始化函数
def init_config():
    """初始化配置"""
    # 创建必要的目录
    os.makedirs(os.path.dirname(DATABASE['path']), exist_ok=True)
    os.makedirs(DATABASE['backup_dir'], exist_ok=True)
    os.makedirs(UPLOAD['upload_folder'], exist_ok=True)
    
    print(f"配置初始化完成:")
    print(f"  数据库路径: {DATABASE['path']}")
    print(f"  JSON输出: {DATABASE['json_output']}")
    print(f"  上传目录: {UPLOAD['upload_folder']}")
    
    # 导入并初始化数据库
    try:
        from models.tl_story import db
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
    
    return True