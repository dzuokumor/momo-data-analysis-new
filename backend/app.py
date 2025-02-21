from pathlib import Path
from flask import Flask, jsonify, make_response, render_template
from .data_processing import extract_transaction_data
from .database import create_database, insert_transactions
import sqlite3
import os

app = Flask(__name__,
            template_folder=str(Path(__file__).parent.parent / "frontend"),
            static_folder=str(Path(__file__).parent.parent / "frontend"))

DB_NAME = str(Path(__file__).parent.parent / "database" / "momo.db")
XML_FILE = str(Path(__file__).parent.parent / "data" / "modified_sms_v2.xml")
LOG_DIR = str(Path(__file__).parent.parent / "log")
RESULTS_FILE = os.path.join(LOG_DIR, "results.txt")

@app.route('/')
def dashboard():
    return render_template("index.html")

@app.route('/api/transactions')
def get_transactions():
    return _get_data_from_db("SELECT * FROM transactions")

@app.route('/api/money-flow')
def get_money_flow():
    query = """
    SELECT 
        SUM(CASE WHEN type = 'receive' OR type = 'deposit' OR type = 'transfer' THEN amount ELSE 0 END) as money_in,
        SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END) as money_out
    FROM transactions
    """
    return _get_data_from_db(query)

@app.route('/api/transaction-types')
def get_transaction_types():
    query = """
    SELECT 
        SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END) as sent,
        SUM(CASE WHEN type = 'receive' THEN amount ELSE 0 END) as received,
        SUM(CASE WHEN type = 'transfer' THEN amount ELSE 0 END) as airtime,
        SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END) as bills,
        SUM(CASE WHEN type = 'deposit' THEN amount ELSE 0 END) as deposits
    FROM transactions
    """
    return _get_data_from_db(query)

@app.route('/api/highest-sender')
def get_highest_sender():
    query = """
        SELECT sender, SUM(amount) as total_sent
        FROM transactions
        WHERE type = 'payment'
        GROUP BY sender
        ORDER BY total_sent DESC
        LIMIT 1;
    """
    return _get_data_from_db(query)

@app.route('/api/total-transaction-volume')
def get_total_transaction_volume():
    return _get_data_from_db("SELECT SUM(amount) as total_volume FROM transactions")

@app.route('/api/average-transaction-size')
def get_average_transaction_size():
    return _get_data_from_db("SELECT AVG(amount) as average_size FROM transactions")

def calculate_summary(db):
    cursor = db.cursor()

    cursor.execute("SELECT sender, COUNT(*) AS transaction_count FROM transactions GROUP BY sender ORDER BY transaction_count DESC LIMIT 2")
    senders = cursor.fetchall()
    if len(senders) > 1:
        sender_most_name = senders[0][0]
        sender_most_count = senders[0][1]
        sender_second_name = senders[1][0]
        sender_second_count = senders[1][1]
    elif len(senders) == 1:
        sender_most_name = senders[0][0]
        sender_most_count = senders[0][1]
        sender_second_name = "No sender found"
        sender_second_count = 0
    else:
        sender_most_name = "No sender found"
        sender_most_count = 0
        sender_second_name = "No sender found"
        sender_second_count = 0

    cursor.execute("SELECT recipient, COUNT(*) AS transaction_count FROM transactions GROUP BY recipient ORDER BY transaction_count DESC LIMIT 2")
    recipients = cursor.fetchall()
    if len(recipients) > 1:
        recipient_most_name = recipients[0][0]
        recipient_most_count = recipients[0][1]
        recipient_second_name = recipients[1][0]
        recipient_second_count = recipients[1][1]
    elif len(recipients) == 1:
        recipient_most_name = recipients[0][0]
        recipient_most_count = recipients[0][1]
        recipient_second_name = "No recipient found"
        recipient_second_count = 0
    else:
        recipient_most_name = "No recipient found"
        recipient_most_count = 0
        recipient_second_name = "No recipient found"
        recipient_second_count = 0

    cursor.execute("SELECT sender, SUM(amount) AS total_sent FROM transactions GROUP BY sender ORDER BY total_sent DESC LIMIT 2")
    highest_senders = cursor.fetchall()
    if len(highest_senders) > 1:
        highest_sender_name = highest_senders[0][0]
        highest_sender_amount = highest_senders[0][1]
        second_highest_sender_name = highest_senders[1][0]
        second_highest_sender_amount = highest_senders[1][1]
    elif len(highest_senders) == 1:
        highest_sender_name = highest_senders[0][0]
        highest_sender_amount = highest_senders[0][1]
        second_highest_sender_name = "No sender found"
        second_highest_sender_amount = 0
    else:
        highest_sender_name = "No sender found"
        highest_sender_amount = 0
        second_highest_sender_name = "No sender found"
        second_highest_sender_amount = 0

    cursor.execute("SELECT AVG(new_balance) FROM transactions")
    avg_balance = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE type IN ('payment', 'transfer')")
    transactions_sent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE type IN ('receive', 'deposit')")
    transactions_received = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions")
    total_volume = cursor.fetchone()[0] or 0

    summary = {
        "sender_most": {"name": sender_most_name, "count": sender_most_count},
        "sender_second_most": {"name": sender_second_name, "count": sender_second_count},
        "recipient_most": {"name": recipient_most_name, "count": recipient_most_count},
        "recipient_second_most": {"name": recipient_second_name, "count": recipient_second_count},
        "highest_sender": {"name": highest_sender_name, "total": highest_sender_amount},
        "second_highest_sender": {"name": second_highest_sender_name, "total": second_highest_sender_amount},
        "avg_balance": avg_balance,
        "transactions_sent": transactions_sent,
        "transactions_received": transactions_received,
        "total_volume": total_volume
    }

    return summary


@app.route('/api/summary')
def get_summary():
    try:
        conn = sqlite3.connect(DB_NAME)
        summary = calculate_summary(conn)
        conn.close()
        return jsonify(summary)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return make_response(jsonify({"error": "Database error"}), 500)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return make_response(jsonify({"error": "An unexpected error occurred"}), 500)

def _get_data_from_db(query):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        if data:
            keys = [description[0] for description in cursor.description]
            result = [dict(zip(keys, row)) for row in data]
            return jsonify(result)
        else:
            return make_response(jsonify({"message": "No data found"}), 204)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return make_response(jsonify({"error": "Database error"}), 500)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return make_response(jsonify({"error": "An unexpected error occurred"}), 500)

if __name__ == '__main__':
    print(f"DB_NAME: {DB_NAME}")
    create_database(DB_NAME)
    transactions = extract_transaction_data(XML_FILE)
    print(transactions)
    insert_transactions(transactions, DB_NAME)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        conn = sqlite3.connect(DB_NAME)
        summary = calculate_summary(conn)
        conn.close()

        with open(RESULTS_FILE, "w") as f:
            f.write("Transaction Summary:\n")
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")

        print(f"Summary written to {RESULTS_FILE}")

    except Exception as e:
        print(f"Error writing results to file: {e}")

    app.run(debug=True, port=5000)