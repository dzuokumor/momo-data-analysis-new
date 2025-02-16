import sqlite3

def create_db():
    conn = sqlite3.connect('database/momo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            date TEXT,
           type TEXT,
            body TEXT,
            readable_date TEXT,
            transaction_type TEXT,
            amount INTEGER,
            sender_receiver TEXT,
            date_time TEXT,
           balance INTEGER,
            transaction_id TEXT
       )
    ''')
    conn.commit()
    conn.close()

def insert_data(transactions):
    conn = sqlite3.connect('database/momo.db')
    cursor = conn.cursor()
    for transaction in transactions:
        cursor.execute('''
            INSERT INTO transactions (
                address, date, type, body, readable_date,
               transaction_type, amount, sender_receiver, date_time, balance, transaction_id
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction['address'],
            transaction['date'],
            transaction['type'],
            transaction['body'],
            transaction['readable_date'],
            transaction['transaction_type'],
            transaction['amount'],
            transaction['sender_receiver'],
            transaction['date_time'],
            transaction['balance'],
            transaction['transaction_id']
        ))
    conn.commit()
    conn.close()