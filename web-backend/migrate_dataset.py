"""Migrate Dataset table to add new columns"""
from app import create_app
from extensions import db
import sqlite3

app = create_app()

with app.app_context():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    print(f'Migrating database: {db_path}')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(datasets)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f'Existing columns: {columns}')
        
        # Add new columns if they don't exist
        if 'file_size' not in columns:
            print('Adding file_size column...')
            cursor.execute("ALTER TABLE datasets ADD COLUMN file_size INTEGER DEFAULT 0")
        
        if 'status' not in columns:
            print('Adding status column...')
            cursor.execute("ALTER TABLE datasets ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
        
        if 'train_count' not in columns:
            print('Adding train_count column...')
            cursor.execute("ALTER TABLE datasets ADD COLUMN train_count INTEGER DEFAULT 0")
        
        if 'val_count' not in columns:
            print('Adding val_count column...')
            cursor.execute("ALTER TABLE datasets ADD COLUMN val_count INTEGER DEFAULT 0")
        
        if 'test_count' not in columns:
            print('Adding test_count column...')
            cursor.execute("ALTER TABLE datasets ADD COLUMN test_count INTEGER DEFAULT 0")
        
        conn.commit()
        conn.close()
        
        print('Migration completed successfully!')
        
        # Verify migration
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(datasets)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f'Updated columns: {columns}')
        conn.close()
        
    except Exception as e:
        print(f'Migration error: {e}')
        import traceback
        traceback.print_exc()

