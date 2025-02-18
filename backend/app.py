from flask import Flask, jsonify, make_response, render_template
from .data_processing import extract_transaction_data
from backend import create_database, insert_transactions
import sqlite3
from pathlib import Path

app = Flask(__name__,
            template_folder=str(Path(__file__).parent.parent / "frontend"),
            static_folder=str(Path(__file__).parent.parent / "frontend")
            )

DB_NAME = str(Path(__file__).parent.parent / "database" / "momo.db") # Correct path using pathlib
XML_FILE = str(Path(__file__).parent.parent / "data" / "modified_sms_v2.xml") # Correct path using pathlib

@app.route("/")
def dashboard():
    return render_template("dashboard.html")
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
            return make_response(jsonify({"message": "No data found"}), 204)  # 204 No Content

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return make_response(jsonify({"error": "Database error"}), 500)  # 500 Internal Server Error
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return make_response(jsonify({"error": "An unexpected error occurred"}), 500)


if __name__ == '__main__':
    print(f"DB_NAME: {DB_NAME}")
    create_database(DB_NAME)  # Create the database and table
    transactions = extract_transaction_data(XML_FILE)
    insert_transactions(transactions, DB_NAME)  # Insert the data
    app.run(debug=True, port=5000)
