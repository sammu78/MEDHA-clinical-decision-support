import sys
import os
sys.path.insert(0, r"c:\Users\Sameer\OneDrive\Desktop\final\backend")
from app.database.db import DB_PATH, init_db, get_db_connection

print("DB_PATH in app:", DB_PATH)
init_db()
conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables after init_db():", tables)
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} rows")
conn.close()
