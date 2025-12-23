"""
迁移脚本：为Dataset表添加新字段
"""
from app import create_app
from extensions import db
import sqlite3

app = create_app()

with app.app_context():
    # 获取数据库路径
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        # Flask 可能会在 instance 目录下创建数据库
        import os
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            # 尝试 instance 目录
            instance_path = os.path.join('instance', os.path.basename(db_path))
            if os.path.exists(instance_path):
                db_path = instance_path
                print(f'Using database from instance directory: {db_path}')
    else:
        print('This migration script only supports SQLite databases')
        exit(1)
    
    print(f'Migrating database: {db_path}')
    
    # 使用SQLite直接操作数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datasets'")
        if not cursor.fetchone():
            print('Datasets table does not exist. Please run init_db.py first.')
            conn.close()
            exit(1)
        
        # 检查新字段是否已存在
        cursor.execute("PRAGMA table_info(datasets)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = {
            'file_size': 'BIGINT DEFAULT 0',
            'status': 'VARCHAR(20) DEFAULT "pending"',
            'train_count': 'INTEGER DEFAULT 0',
            'val_count': 'INTEGER DEFAULT 0',
            'test_count': 'INTEGER DEFAULT 0'
        }
        
        added_columns = []
        for col_name, col_def in new_columns.items():
            if col_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE datasets ADD COLUMN {col_name} {col_def}')
                    added_columns.append(col_name)
                    print(f'Added column: {col_name}')
                except sqlite3.OperationalError as e:
                    print(f'Error adding column {col_name}: {e}')
            else:
                print(f'Column {col_name} already exists')
        
        conn.commit()
        
        if added_columns:
            print(f'Successfully added columns: {", ".join(added_columns)}')
        else:
            print('All columns already exist. No migration needed.')
        
    except Exception as e:
        conn.rollback()
        print(f'Migration failed: {e}')
        raise
    finally:
        conn.close()
    
    print('Migration completed!')

