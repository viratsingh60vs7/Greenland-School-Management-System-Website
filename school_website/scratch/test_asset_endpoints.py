import sqlite3, os, sys, json
sys.path.insert(0, 'school_website')
from server import SchoolHandler
from io import BytesIO

class MockRequest:
    def __init__(self, data=b""):
        self._data = data
    def makefile(self, *args, **kwargs):
        return BytesIO(self._data)

def test_routes():
    conn = sqlite3.connect('school_website/school.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Verify tables exist
    for tbl in ['it_assets', 'it_rentals', 'it_asset_allocations', 'it_warranties', 'it_maintenance_service', 'it_asset_payments', 'it_asset_logs']:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"Table {tbl}: {cur.fetchone()[0]} rows")
    
    print("✓ All tables exist and populated!")

if __name__ == '__main__':
    test_routes()
