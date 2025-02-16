from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = sqlite3.connect('database/momo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True)