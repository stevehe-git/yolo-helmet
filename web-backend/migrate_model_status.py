import os
import sqlite3
from sqlalchemy import create_engine, inspect, text

if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, 'instance')
    db_path = os.path.join(instance_path, "yolo_helmet.db")
    db_uri = f'sqlite:///{db_path}'

    print(f"正在迁移数据库: {db_path}")

    if not os.path.exists(db_path):
        print("数据库文件不存在，请先运行 init_db.py")
        exit(1)

    engine = create_engine(db_uri)
    inspector = inspect(engine)

    if not inspector.has_table('models'):
        print("Models table does not exist. Please run init_db.py first.")
        exit(1)

    # 检查status列是否存在
    columns = [col['name'] for col in inspector.get_columns('models')]
    
    if 'status' not in columns:
        try:
            with engine.connect() as connection:
                connection.execute(text("ALTER TABLE models ADD COLUMN status TEXT DEFAULT 'pending'"))
                connection.commit()
            print("✓ 成功添加 status 列到 models 表")
            
            # 更新现有模型的状态
            with engine.connect() as connection:
                # 根据metrics判断状态
                connection.execute(text("""
                    UPDATE models 
                    SET status = CASE 
                        WHEN metrics_json IS NOT NULL AND metrics_json != 'null' AND metrics_json NOT LIKE '%error%' THEN 'completed'
                        WHEN metrics_json IS NOT NULL AND metrics_json LIKE '%error%' THEN 'failed'
                        ELSE 'pending'
                    END
                """))
                connection.commit()
            print("✓ 成功更新现有模型的状态")
        except Exception as e:
            print(f"✗ 添加 status 列失败: {e}")
    else:
        print("status 列已存在于 models 表中，无需迁移。")

