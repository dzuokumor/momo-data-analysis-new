from flask import Flask, jsonify, render_template, request
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database/momo.db"



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def _get_data_from_db(query, params=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        data = cursor.fetchall()
        conn.close()

        if data:
            return jsonify([dict(zip([column[0] for column in cursor.description], row)) for row in data])
        return jsonify([])
            
    except sqlite3.Error as e:
        print(f"Database error in query '{query}': {e}")
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500
    except ValueError as e:
        print(f"Value error in query '{query}': {e}")
        return jsonify({
            "error": "Invalid parameter format",
            "details": str(e)
        }), 400
    except Exception as e:
        print(f"Unexpected error in query '{query}': {e}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500
    

@app.route('/api/transactions/search', methods=['GET'])
def search_transactions():
    try:
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        min_amount = request.args.get('minAmount')
        max_amount = request.args.get('maxAmount')
        transaction_type = request.args.get('type')
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if date_from:
            query += " AND date(timestamp) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(timestamp) <= ?"
            params.append(date_to)
        if min_amount:
            query += " AND amount >= ?"
            params.append(float(min_amount))
        if max_amount:
            query += " AND amount <= ?"
            params.append(float(max_amount))
        if transaction_type:
            query += " AND LOWER(type) = LOWER(?)"
            params.append(transaction_type)
        
        query += " ORDER BY timestamp DESC LIMIT 200"
        
        return _get_data_from_db(query, tuple(params))
        
    except ValueError as e:
        return jsonify({"error": "Invalid parameter format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return render_template("index.html", active_page='dashboard')

@app.route('/summary')
def summary():
    return render_template("summary.html", active_page='summary')

@app.route('/api/card-data')
def card_data():
    target = request.args.get('target')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if target == 'top-sender':
        cursor.execute("SELECT sender, SUM(amount) as amount FROM transactions WHERE type = 'payment' GROUP BY sender ORDER BY amount DESC LIMIT 1")
    elif target == 'top-recipient':
        cursor.execute("SELECT recipient, COUNT(*) as count FROM transactions WHERE recipient IS NOT NULL GROUP BY recipient ORDER BY count DESC LIMIT 1")
    elif target == 'transaction-volume':
        cursor.execute("SELECT SUM(amount) as volume FROM transactions")
    elif target == 'busiest-hour':
        cursor.execute("SELECT strftime('%H', timestamp) as hour FROM transactions GROUP BY hour ORDER BY COUNT(*) DESC LIMIT 1")
    elif target == 'total-income':
        cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE type IN ('receive', 'deposit')")
    elif target == 'total-expenses':
        cursor.execute("SELECT SUM(amount) as total FROM transactions WHERE type IN ('payment', 'transfer', 'bill_payment')")
    elif target == 'total-transactions':
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
    elif target == 'avg-balance':
        cursor.execute("SELECT AVG(new_balance) as average FROM transactions WHERE new_balance IS NOT NULL")

    result = cursor.fetchone()
    conn.close()
    return jsonify(dict(zip([col[0] for col in cursor.description], result))) if result else jsonify({})

@app.route('/api/recent-transactions')
def recent_transactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT type, amount, timestamp, sender, recipient FROM transactions ORDER BY timestamp DESC LIMIT 5")
    transactions = cursor.fetchall()
    conn.close()
    
    keys = [col[0] for col in cursor.description]
    return jsonify([dict(zip(keys, row)) for row in transactions])

@app.route('/api/summary/top-senders')
def top_senders():
    return _get_data_from_db("""
        SELECT sender, SUM(amount) as total_sent 
        FROM transactions 
        WHERE type = 'payment' 
        GROUP BY sender 
        ORDER BY total_sent DESC 
        LIMIT 5
    """)

@app.route('/api/summary/top-recipients')
def top_recipients():
    return _get_data_from_db("""
        SELECT recipient, COUNT(*) as transaction_count 
        FROM transactions 
        WHERE recipient IS NOT NULL 
        GROUP BY recipient 
        ORDER BY transaction_count DESC 
        LIMIT 5
    """)

@app.route('/api/summary/hourly-activity')
def hourly_activity():
    return _get_data_from_db("""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount
        FROM transactions
        GROUP BY hour
        ORDER BY hour
    """)

@app.route('/api/transaction-types')
def transaction_types():
    return _get_data_from_db("""
        SELECT 
            type,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count
        FROM transactions
        GROUP BY type
        ORDER BY total_amount DESC
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
