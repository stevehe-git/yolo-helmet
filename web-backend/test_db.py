"""Test database connection and Dataset model"""
from app import create_app
from models import Dataset, db

app = create_app()

with app.app_context():
    try:
        print('Testing dataset query...')
        datasets = Dataset.query.all()
        print(f'Success: Found {len(datasets)} datasets')
        if datasets:
            print(f'First dataset: {datasets[0].to_dict()}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

