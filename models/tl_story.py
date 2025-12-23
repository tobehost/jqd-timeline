"""
TimelineJS SQLite 数据模型
文件名: models/tl-story.py
"""

import sqlite3
from datetime import datetime
import json

class TimelineDatabase:
    def __init__(self, db_path='static/data/timeline.db'):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def connect(self):
        """连接到数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式的结果
        return self.conn
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 1. 创建timeline主表（存储标题和设置）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_headline TEXT,
            title_text TEXT,
            scale TEXT DEFAULT 'human',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. 创建events表（存储事件）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            text TEXT,
            
            -- 开始日期
            start_year INTEGER NOT NULL,
            start_month INTEGER,
            start_day INTEGER,
            start_hour INTEGER,
            start_minute INTEGER,
            start_second INTEGER,
            start_millisecond INTEGER,
            start_display_date TEXT,
            
            -- 结束日期（可选）
            end_year INTEGER,
            end_month INTEGER,
            end_day INTEGER,
            end_hour INTEGER,
            end_minute INTEGER,
            end_second INTEGER,
            end_millisecond INTEGER,
            end_display_date TEXT,
            
            -- 事件显示日期（覆盖开始/结束日期）
            display_date TEXT,
            
            -- 分组
            event_group TEXT,
            
            -- 唯一ID
            unique_id TEXT UNIQUE,
            
            -- 媒体信息
            media_url TEXT,
            media_caption TEXT,
            media_credit TEXT,
            media_thumbnail TEXT,
            media_alt TEXT,
            media_title TEXT,
            media_link TEXT,
            media_link_target TEXT,
            
            -- 背景设置
            background_url TEXT,
            background_color TEXT,
            background_alt TEXT,
            
            -- 自动链接
            autolink BOOLEAN DEFAULT 1,
            
            -- 排序和状态
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 3. 创建eras表（存储时代）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_eras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            text TEXT,
            
            -- 开始日期
            start_year INTEGER NOT NULL,
            start_month INTEGER,
            start_day INTEGER,
            start_hour INTEGER,
            start_minute INTEGER,
            start_second INTEGER,
            start_millisecond INTEGER,
            start_display_date TEXT,
            
            -- 结束日期
            end_year INTEGER NOT NULL,
            end_month INTEGER,
            end_day INTEGER,
            end_hour INTEGER,
            end_minute INTEGER,
            end_second INTEGER,
            end_millisecond INTEGER,
            end_display_date TEXT,
            
            -- 排序和状态
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 4. 创建media表（如果需要单独管理媒体）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            url TEXT NOT NULL,
            caption TEXT,
            credit TEXT,
            thumbnail TEXT,
            alt TEXT,
            title TEXT,
            link TEXT,
            link_target TEXT,
            media_type TEXT DEFAULT 'image',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES timeline_events(id) ON DELETE CASCADE
        )
        ''')
        
        # 5. 创建groups表（用于事件分组）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            color TEXT,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 初始化默认配置
        cursor.execute('SELECT COUNT(*) as count FROM timeline_config')
        if cursor.fetchone()['count'] == 0:
            cursor.execute('''
            INSERT INTO timeline_config (title_headline, title_text, scale)
            VALUES (?, ?, ?)
            ''', ('科技发展里程碑', '从工业革命到人工智能时代的重要科技突破', 'human'))
        
        conn.commit()
        conn.close()
        
        print(f"数据库初始化完成: {self.db_path}")
    
    def get_timeline_config(self):
        """获取时间线配置"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM timeline_config LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_timeline_config(self, title_headline=None, title_text=None, scale=None):
        """更新时间线配置"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 构建更新语句
        updates = []
        params = []
        
        if title_headline is not None:
            updates.append("title_headline = ?")
            params.append(title_headline)
        
        if title_text is not None:
            updates.append("title_text = ?")
            params.append(title_text)
        
        if scale is not None:
            updates.append("scale = ?")
            params.append(scale)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        if updates:
            sql = f"UPDATE timeline_config SET {', '.join(updates)} WHERE id = 1"
            cursor.execute(sql, params)
            conn.commit()
        
        conn.close()
        return True
    
    def get_all_events(self, active_only=True):
        """获取所有事件"""
        conn = self.connect()
        cursor = conn.cursor()
        
        sql = '''
        SELECT * FROM timeline_events 
        WHERE 1=1
        '''
        params = []
        
        if active_only:
            sql += " AND is_active = 1"
        
        sql += " ORDER BY start_year, start_month, start_day, sort_order"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_event_by_id(self, event_id):
        """根据ID获取事件"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM timeline_events WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def add_event(self, event_data):
        """添加新事件"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 构建字段和值
        fields = []
        placeholders = []
        values = []
        
        for field, value in event_data.items():
            if value is not None:
                fields.append(field)
                placeholders.append('?')
                values.append(value)
        
        sql = f"INSERT INTO timeline_events ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, values)
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def update_event(self, event_id, event_data):
        """更新事件"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # 构建更新语句
        updates = []
        values = []
        
        for field, value in event_data.items():
            if value is not None:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            sql = f"UPDATE timeline_events SET {', '.join(updates)} WHERE id = ?"
            values.append(event_id)
            cursor.execute(sql, values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_event(self, event_id, soft_delete=True):
        """删除事件"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if soft_delete:
            cursor.execute('UPDATE timeline_events SET is_active = 0 WHERE id = ?', (event_id,))
        else:
            cursor.execute('DELETE FROM timeline_events WHERE id = ?', (event_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_all_eras(self, active_only=True):
        """获取所有时代"""
        conn = self.connect()
        cursor = conn.cursor()
        
        sql = '''
        SELECT * FROM timeline_eras 
        WHERE 1=1
        '''
        params = []
        
        if active_only:
            sql += " AND is_active = 1"
        
        sql += " ORDER BY start_year, sort_order"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_era(self, era_data):
        """添加新时代"""
        conn = self.connect()
        cursor = conn.cursor()
        
        fields = []
        placeholders = []
        values = []
        
        for field, value in era_data.items():
            if value is not None:
                fields.append(field)
                placeholders.append('?')
                values.append(value)
        
        sql = f"INSERT INTO timeline_eras ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, values)
        
        era_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return era_id
    
    def update_era(self, era_id, era_data):
        """更新时代"""
        conn = self.connect()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for field, value in era_data.items():
            if value is not None:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            sql = f"UPDATE timeline_eras SET {', '.join(updates)} WHERE id = ?"
            values.append(era_id)
            cursor.execute(sql, values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_era(self, era_id, soft_delete=True):
        """删除时代"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if soft_delete:
            cursor.execute('UPDATE timeline_eras SET is_active = 0 WHERE id = ?', (era_id,))
        else:
            cursor.execute('DELETE FROM timeline_eras WHERE id = ?', (era_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def generate_json(self):
        """从数据库生成TimelineJS JSON格式"""
        timeline_data = {
            "title": {},
            "events": [],
            "eras": [],
            "scale": "human"
        }
        
        # 1. 获取配置
        config = self.get_timeline_config()
        if config:
            timeline_data["title"] = {
                "text": {
                    "headline": config.get("title_headline", ""),
                    "text": config.get("title_text", "")
                }
            }
            timeline_data["scale"] = config.get("scale", "human")
        
        # 2. 获取事件
        events = self.get_all_events()
        for event in events:
            # 构建日期对象
            start_date = {}
            if event.get("start_year"):
                start_date["year"] = event["start_year"]
                if event.get("start_month"):
                    start_date["month"] = event["start_month"]
                if event.get("start_day"):
                    start_date["day"] = event["start_day"]
                if event.get("start_hour"):
                    start_date["hour"] = event["start_hour"]
                if event.get("start_minute"):
                    start_date["minute"] = event["start_minute"]
                if event.get("start_second"):
                    start_date["second"] = event["start_second"]
                if event.get("start_millisecond"):
                    start_date["millisecond"] = event["start_millisecond"]
                if event.get("start_display_date"):
                    start_date["display_date"] = event["start_display_date"]
            
            # 构建结束日期对象
            end_date = None
            if event.get("end_year"):
                end_date = {"year": event["end_year"]}
                if event.get("end_month"):
                    end_date["month"] = event["end_month"]
                if event.get("end_day"):
                    end_date["day"] = event["end_day"]
                if event.get("end_hour"):
                    end_date["hour"] = event["end_hour"]
                if event.get("end_minute"):
                    end_date["minute"] = event["end_minute"]
                if event.get("end_second"):
                    end_date["second"] = event["end_second"]
                if event.get("end_millisecond"):
                    end_date["millisecond"] = event["end_millisecond"]
                if event.get("end_display_date"):
                    end_date["display_date"] = event["end_display_date"]
            
            # 构建事件对象
            event_obj = {
                "start_date": start_date,
                "text": {
                    "headline": event.get("headline", ""),
                    "text": event.get("text", "")
                }
            }
            
            # 添加可选字段
            if end_date:
                event_obj["end_date"] = end_date
            
            if event.get("display_date"):
                event_obj["display_date"] = event["display_date"]
            
            if event.get("event_group"):
                event_obj["group"] = event["event_group"]
            
            if event.get("unique_id"):
                event_obj["unique_id"] = event["unique_id"]
            
            # 媒体
            media_fields = {}
            if event.get("media_url"):
                media_fields["url"] = event["media_url"]
                if event.get("media_caption"):
                    media_fields["caption"] = event["media_caption"]
                if event.get("media_credit"):
                    media_fields["credit"] = event["media_credit"]
                if event.get("media_thumbnail"):
                    media_fields["thumbnail"] = event["media_thumbnail"]
                if event.get("media_alt"):
                    media_fields["alt"] = event["media_alt"]
                if event.get("media_title"):
                    media_fields["title"] = event["media_title"]
                if event.get("media_link"):
                    media_fields["link"] = event["media_link"]
                if event.get("media_link_target"):
                    media_fields["link_target"] = event["media_link_target"]
            
            if media_fields:
                event_obj["media"] = media_fields
            
            # 背景
            background_fields = {}
            if event.get("background_url"):
                background_fields["url"] = event["background_url"]
                if event.get("background_color"):
                    background_fields["color"] = event["background_color"]
                if event.get("background_alt"):
                    background_fields["alt"] = event["background_alt"]
            
            if background_fields:
                event_obj["background"] = background_fields
            
            if "autolink" in event:
                event_obj["autolink"] = bool(event["autolink"])
            
            timeline_data["events"].append(event_obj)
        
        # 3. 获取时代
        eras = self.get_all_eras()
        for era in eras:
            # 构建开始日期
            start_date = {"year": era["start_year"]}
            if era.get("start_month"):
                start_date["month"] = era["start_month"]
            if era.get("start_day"):
                start_date["day"] = era["start_day"]
            
            # 构建结束日期
            end_date = {"year": era["end_year"]}
            if era.get("end_month"):
                end_date["month"] = era["end_month"]
            if era.get("end_day"):
                end_date["day"] = era["end_day"]
            
            era_obj = {
                "start_date": start_date,
                "end_date": end_date,
                "text": {
                    "headline": era.get("headline", ""),
                    "text": era.get("text", "")
                }
            }
            
            timeline_data["eras"].append(era_obj)
        
        return timeline_data
    
    def save_json_to_file(self, filepath='static/data/tl-story.json'):
        """保存JSON到文件"""
        timeline_data = self.generate_json()
        
        # 确保目录存在
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, ensure_ascii=False)
        
        print(f"JSON文件已保存: {filepath}")
        return filepath


# 创建全局数据库实例
db = TimelineDatabase()