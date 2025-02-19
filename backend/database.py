import sqlite3
from pathlib import Path
import os

def create_database(db_name):
    db_path = Path(__file__).parent.parent / "database" / "momo.db"
    db_dir = db_path.parent

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            transaction_id TEXT UNIQUE, 
            sender TEXT,
            recipient TEXT,
            fee REAL DEFAULT 0.0,
            new_balance REAL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database created/checked at: {db_path}")

def insert_transactions(transactions, db_name):
    db_path = Path(__file__).parent.parent / "database" / "momo.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for transaction in transactions:
        print("Transaction Data (Before Insertion):", transaction)

        try:
            cursor.execute("""
                SELECT 1 FROM transactions 
                WHERE (transaction_id = ? OR (? IS NULL AND transaction_id IS NULL)) 
                AND amount = ? 
                AND timestamp = ? 
                AND type = ?
            """, (
                transaction.get("transaction_id"), transaction.get("transaction_id"),
                transaction.get("amount"),
                transaction.get("timestamp"),
                transaction.get("type")
            ))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO transactions (amount, type, timestamp, transaction_id, sender, recipient, fee, new_balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.get("amount"),
                    transaction.get("type"),
                    transaction.get("timestamp"),
                    transaction.get("transaction_id"),
                    transaction.get("sender"),
                    transaction.get("recipient"),
                    transaction.get("fee", 0.0),
                    transaction.get("new_balance")
                ))
                inserted_count += 1
                print(f"Transaction with ID {transaction.get('transaction_id')} inserted successfully.")
            else:
                skipped_count += 1
                print(f"Duplicate transaction detected (ID: {transaction.get('transaction_id')}). Skipping.")

        except sqlite3.IntegrityError:
            print(f"Integrity Error (Duplicate ID): {transaction.get('transaction_id')}. Skipping.")
            skipped_count += 1
        except sqlite3.Error as e:
            print(f"Database error during insertion: {e}")
            conn.rollback()
            conn.close()
            return

    conn.commit()
    conn.close()
    print(f"{inserted_count} transactions inserted. {skipped_count} skipped.")
