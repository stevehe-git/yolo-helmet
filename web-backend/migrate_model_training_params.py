"""
迁移脚本：为 models 表添加 training_params_json 字段
"""
import os
import sqlite3
from pathlib import Path

def migrate_model_training_params():
    """为 models 表添加 training_params_json 字段"""
    # 获取数据库路径
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')
    db_path = os.path.join(instance_path, "yolo_helmet.db")
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("请先运行 init_db.py 初始化数据库")
        return
    
    print(f"正在迁移数据库: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查 training_params_json 列是否已存在
        cursor.execute("PRAGMA table_info(models)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'training_params_json' in columns:
            print("training_params_json 列已存在，无需迁移")
            return
        
        # 添加 training_params_json 列
        print("正在添加 training_params_json 列...")
        cursor.execute("ALTER TABLE models ADD COLUMN training_params_json TEXT")
        conn.commit()
        
        print("✓ 成功添加 training_params_json 列到 models 表")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 迁移失败: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_model_training_params()

