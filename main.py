#!/usr/bin/env python3
"""
TimelineJS 主程序入口
运行: python3 main.py
访问: http://localhost:8000/admin/admin.html
"""

import os
import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3

# 导入配置和模型
from config import init_config, DATABASE, SERVER
from models.tl_story import TimelineDatabase

# 全局数据库实例
db = TimelineDatabase(DATABASE['path'])

class TimelineAPIHandler(SimpleHTTPRequestHandler):
    """扩展的HTTP请求处理器，支持API和静态文件"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        # API路由
        if parsed_path.path.startswith('/api/'):
            self.handle_api(parsed_path)
        else:
            # 静态文件服务
            super().do_GET()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/'):
            self.handle_api(parsed_path, method='POST')
        else:
            self.send_error(404)
    
    def do_PUT(self):
        """处理PUT请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/'):
            self.handle_api(parsed_path, method='PUT')
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        """处理DELETE请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/'):
            self.handle_api(parsed_path, method='DELETE')
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
    
    def handle_api(self, parsed_path, method='GET'):
        """处理API请求"""
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        try:
            # 获取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = None
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            # 路由处理
            if path == '/api/config':
                self.handle_config(method, query, post_data)
            elif path == '/api/events':
                self.handle_events(method, query, post_data)
            elif path == '/api/events/<int>':
                event_id = int(path.split('/')[-1])
                self.handle_single_event(method, event_id, query, post_data)
            elif path == '/api/eras':
                self.handle_eras(method, query, post_data)
            elif path == '/api/eras/<int>':
                era_id = int(path.split('/')[-1])
                self.handle_single_era(method, era_id, query, post_data)
            elif path == '/api/generate-json':
                self.handle_generate_json(method, query, post_data)
            elif path == '/api/export':
                self.handle_export(method, query, post_data)
            elif path == '/api/import':
                self.handle_import(method, query, post_data)
            elif path == '/api/backup':
                self.handle_backup(method, query, post_data)
            elif path == '/api/health':
                self.send_json_response({'status': 'ok', 'timestamp': time.time()})
            else:
                self.send_error(404, 'API endpoint not found')
        
        except Exception as e:
            print(f"API处理错误: {e}")
            self.send_json_response({'error': str(e)}, status=500)
    
    def handle_config(self, method, query, post_data):
        """处理配置请求"""
        if method == 'GET':
            config = db.get_timeline_config()
            self.send_json_response(config)
        
        elif method == 'PUT':
            data = json.loads(post_data.decode('utf-8'))
            db.update_timeline_config(
                title_headline=data.get('title_headline'),
                title_text=data.get('title_text'),
                scale=data.get('scale')
            )
            self.send_json_response({'status': 'success'})
    
    def handle_events(self, method, query, post_data):
        """处理事件请求"""
        if method == 'GET':
            active_only = query.get('active_only', ['true'])[0].lower() == 'true'
            events = db.get_all_events(active_only=active_only)
            self.send_json_response(events)
        
        elif method == 'POST':
            data = json.loads(post_data.decode('utf-8'))
            event_id = db.add_event(data)
            self.send_json_response({'status': 'success', 'id': event_id}, status=201)
    
    def handle_single_event(self, method, event_id, query, post_data):
        """处理单个事件请求"""
        if method == 'GET':
            event = db.get_event_by_id(event_id)
            if event:
                self.send_json_response(event)
            else:
                self.send_error(404, 'Event not found')
        
        elif method == 'PUT':
            data = json.loads(post_data.decode('utf-8'))
            success = db.update_event(event_id, data)
            self.send_json_response({'status': 'success' if success else 'failed'})
        
        elif method == 'DELETE':
            soft_delete = query.get('soft', ['true'])[0].lower() == 'true'
            success = db.delete_event(event_id, soft_delete=soft_delete)
            self.send_json_response({'status': 'success' if success else 'failed'})
    
    def handle_eras(self, method, query, post_data):
        """处理时代请求"""
        if method == 'GET':
            active_only = query.get('active_only', ['true'])[0].lower() == 'true'
            eras = db.get_all_eras(active_only=active_only)
            self.send_json_response(eras)
        
        elif method == 'POST':
            data = json.loads(post_data.decode('utf-8'))
            era_id = db.add_era(data)
            self.send_json_response({'status': 'success', 'id': era_id}, status=201)
    
    def handle_single_era(self, method, era_id, query, post_data):
        """处理单个时代请求"""
        if method == 'GET':
            era = None  # 这里需要添加获取单个时代的方法
            if era:
                self.send_json_response(era)
            else:
                self.send_error(404, 'Era not found')
        
        elif method == 'PUT':
            data = json.loads(post_data.decode('utf-8'))
            success = db.update_era(era_id, data)
            self.send_json_response({'status': 'success' if success else 'failed'})
        
        elif method == 'DELETE':
            soft_delete = query.get('soft', ['true'])[0].lower() == 'true'
            success = db.delete_era(era_id, soft_delete=soft_delete)
            self.send_json_response({'status': 'success' if success else 'failed'})
    
    def handle_generate_json(self, method, query, post_data):
        """处理生成JSON请求"""
        if method == 'POST':
            json_data = db.generate_json()
            filepath = db.save_json_to_file()
            
            # 返回JSON数据
            self.send_json_response({
                'status': 'success',
                'filepath': filepath,
                'data': json_data
            })
        
        elif method == 'GET':
            # 直接生成并返回JSON
            json_data = db.generate_json()
            self.send_json_response(json_data)
    
    def handle_export(self, method, query, post_data):
        """处理导出请求"""
        if method == 'GET':
            # 导出数据库为JSON文件
            json_data = db.generate_json()
            
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Disposition', 'attachment; filename="timeline-export.json"')
            self.end_headers()
            
            self.wfile.write(json.dumps(json_data, indent=2).encode('utf-8'))
    
    def handle_import(self, method, query, post_data):
        """处理导入请求"""
        if method == 'POST':
            # TODO: 实现数据导入
            self.send_json_response({'status': 'import not implemented yet'}, status=501)
    
    def handle_backup(self, method, query, post_data):
        """处理备份请求"""
        if method == 'POST':
            # TODO: 实现数据库备份
            self.send_json_response({'status': 'backup not implemented yet'}, status=501)
    
    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"{self.log_date_time_string()} {format % args}")


class StaticFileHandler(TimelineAPIHandler):
    """处理静态文件请求"""
    
    def __init__(self, *args, **kwargs):
        # 设置当前目录为项目根目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, **kwargs)


def main():
    """主函数"""
    print("=== TimelineJS 数据管理系统 ===")
    
    # 初始化配置
    init_config()
    
    # 启动HTTP服务器
    server_address = (SERVER['host'], SERVER['port'])
    httpd = HTTPServer(server_address, StaticFileHandler)
    
    print(f"\n服务器启动在: http://{SERVER['host']}:{SERVER['port']}")
    print(f"管理后台: http://{SERVER['host']}:{SERVER['port']}/admin/admin.html")
    print(f"API文档: http://{SERVER['host']}:{SERVER['port']}/api/")
    print(f"数据文件: {DATABASE['json_output']}")
    print("\nAPI端点:")
    print("  GET  /api/config           - 获取配置")
    print("  PUT  /api/config           - 更新配置")
    print("  GET  /api/events           - 获取所有事件")
    print("  POST /api/events           - 添加事件")
    print("  GET  /api/events/{id}      - 获取单个事件")
    print("  PUT  /api/events/{id}      - 更新事件")
    print("  DELETE /api/events/{id}    - 删除事件")
    print("  GET  /api/eras             - 获取所有时代")
    print("  POST /api/eras             - 添加时代")
    print("  POST /api/generate-json    - 生成JSON文件")
    print("  GET  /api/health           - 健康检查")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        db.close()
        httpd.server_close()


if __name__ == '__main__':
    main()