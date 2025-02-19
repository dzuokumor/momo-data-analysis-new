import sqlite3
from pathlib import Path


def clean_duplicates(db_name):
    db_path = Path(__file__).parent.parent / "database" / db_name
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM transactions WHERE rowid NOT IN (
            SELECT MIN(rowid) FROM transactions 
            GROUP BY COALESCE(transaction_id, ''), amount, timestamp, type
        );
    """)

    conn.commit()
    conn.close()
    print("Duplicate transactions removed.")
