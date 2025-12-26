"""
迁移脚本：为 datasets 表添加 error_reason 字段
如果数据库已存在，运行此脚本来添加新字段
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 使用原始 SQL 添加列（如果不存在）
        db.session.execute(text("""
            ALTER TABLE datasets 
            ADD COLUMN error_reason TEXT
        """))
        db.session.commit()
        print('成功添加 error_reason 字段到 datasets 表')
    except Exception as e:
        # 如果列已存在，会抛出异常，这是正常的
        if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
            print('error_reason 字段已存在，无需添加')
        else:
            print(f'添加字段时出错: {str(e)}')
            db.session.rollback()

