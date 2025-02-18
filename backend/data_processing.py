import xml.etree.ElementTree as ET
import re
from datetime import datetime
import sqlite3

def extract_transaction_data(xml_file):
    transactions = []
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for sms in root.findall('sms'):
        body = sms.get('body')
        try:
            transaction = parse_transaction(body)
            if transaction:
                transactions.append(transaction)
        except Exception as e:
            print(f"Error parsing SMS: {body[:50]}... - Error: {e}")

    return transactions

def parse_transaction(body):
    if "received" in body:
        match = re.search(r"You have received (.+?) RWF from (.+?) \((.*?)\) on your mobile money account at (.+?)\.", body)
        if match:
            amount = float(match.group(1).replace(",", ""))
            sender = match.group(2).strip()
            sender_phone = match.group(3).strip()
            timestamp_str = match.group(4)
            transaction_type = "receive"
            transaction_id = None

    elif "payment" in body and "completed" in body:
        match = re.search(r"TxId: (.+?)\. Your payment of (.+?) RWF to (.+?) (.+?) has been completed at (.+?)\.", body)
        if match:
            transaction_id = match.group(1).strip()
            amount = float(match.group(2).replace(",", ""))
            recipient = match.group(3).strip()
            recipient_info = match.group(4).strip()
            timestamp_str = match.group(5)
            transaction_type = "payment"

    elif "transferred" in body:
        match = re.search(r"\*165\*S\*(.+) RWF transferred to (.+?) \((.*?)\) from (.+?) at (.+?) \. Fee was: (.+?) RWF", body)
        if match:
            amount = float(match.group(1).replace(",", ""))
            recipient = match.group(2).strip()
            recipient_phone = match.group(3).strip()
            sender_info = match.group(4).strip()
            timestamp_str = match.group(5)
            fee = float(match.group(6).replace(",", "")) if match.group(6) else 0.0
            transaction_type = "transfer"
            transaction_id = None

    elif "bank deposit" in body:
        match = re.search(r"bank deposit of (.+?) RWF has been added to your mobile money account at (.+?)\.", body)
        if match:
            amount = float(match.group(1).replace(",", ""))
            timestamp_str = match.group(2)
            transaction_type = "deposit"
            transaction_id = None

    else:
        return None

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        timestamp = datetime.now()

    transaction = {
        "amount": amount,
        "type": transaction_type,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_id": transaction_id,
        "sender": sender if "sender" in locals() else None,
        "sender_phone": sender_phone if "sender_phone" in locals() else None,
        "recipient": recipient if "recipient" in locals() else None,
        "recipient_info": recipient_info if "recipient_info" in locals() else None,
        "recipient_phone": recipient_phone if "recipient_phone" in locals() else None,
        "fee": fee if "fee" in locals() else 0.0,
    }
    return transaction