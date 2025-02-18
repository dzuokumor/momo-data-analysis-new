# backend/database.py
import sqlite3
from pathlib import Path
import os

def create_database(db_name="database/momo.db"):
    db_path = Path(__file__).parent.parent / "database" / "momo.db"
    db_dir = db_path.parent

    # 1. Create the directory FIRST (if it doesn't exist)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Directory created: {db_dir}")  # Confirmation

    # 2. THEN connect to the database (which creates the file if it doesn't exist)
    conn = sqlite3.connect(str(db_path))  # This will create momo.db if it's missing
    cursor = conn.cursor()

    # 3. Create the table (only if it doesn't exist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            type TEXT,
            timestamp TEXT,
            transaction_id TEXT UNIQUE,
            sender TEXT,
            sender_phone TEXT,
            recipient TEXT,
            recipient_info TEXT,
            recipient_phone TEXT,
            fee REAL
        )
    """)
    conn.commit()
    conn.close()

    print(f"Database created/checked at: {db_path}")  # Confirmation


def insert_transactions(transactions, db_name="database/momo.db"):
    db_path = Path(__file__).parent.parent / "database" / "momo.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    for transaction in transactions:
        try:
            cursor.execute("""
                INSERT INTO transactions (amount, type, timestamp, transaction_id, sender, sender_phone, recipient, recipient_info, recipient_phone, fee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (transaction["amount"], transaction["type"], transaction["timestamp"], transaction.get("transaction_id"), transaction.get("sender"), transaction.get("sender_phone"), transaction.get("recipient"), transaction.get("recipient_info"), transaction.get("recipient_phone"), transaction.get("fee")))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Duplicate transaction ID: {transaction.get('transaction_id')}. Skipping.")
        except Exception as e:
            print(f"Error inserting transaction: {transaction}. Error: {e}")

    conn.close()

