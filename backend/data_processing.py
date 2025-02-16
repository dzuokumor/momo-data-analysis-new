import xml.etree.ElementTree as ET
import logging
import re

logging.basicConfig(filename='logs/unprocessed.log', level=logging.INFO)

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        messages = []
        for sms in root.findall('sms'):
            message = {
                'address': sms.attrib.get('address'),
                'date': sms.attrib.get('date'),
                'type': sms.attrib.get('type'),
                'body': sms.attrib.get('body'),
                'readable_date': sms.attrib.get('readable_date')
            }
            messages.append(message)
        return messages
    except Exception as e:
        logging.error(f"Error parsing XML: {e}")
        return []

def extract_transaction_details(body):
    details = {
        'transaction_type': None,
        'amount': None,
        'sender_receiver': None,
        'date_time': None,
        'balance': None,
        'transaction_id': None
    }

    #transaction type
    if "received" in body:
        details['transaction_type'] = "Incoming Money"
    elif "payment" in body:
        details['transaction_type'] = "Payment"
    elif "deposit" in body:
        details['transaction_type'] = "Bank Deposit"
    elif "transferred" in body:
        details['transaction_type'] = "Transfer"

    #amount
    amount_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?) RWF', body)
    if amount_match:
        details['amount'] = int(amount_match.group(1).replace(',', ''))

    #sender/receiver
    sender_receiver_match = re.search(r'from|to (\w+ \w+)', body)
    if sender_receiver_match:
        details['sender_receiver'] = sender_receiver_match.group(1)

    #date and time
    date_time_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', body)
    if date_time_match:
        details['date_time'] = date_time_match.group(0)

    #balance
    balance_match = re.search(r'balance: (\d{1,3}(?:,\d{3})*(?:\.\d{2})?) RWF', body)
    if balance_match:
        details['balance'] = int(balance_match.group(1).replace(',', ''))

    #transaction ID
    tx_id_match = re.search(r'TxId: (\d+)', body)
    if tx_id_match:
        details['transaction_id'] = tx_id_match.group(1)

    return details

def clean_and_categorize(messages):
    cleaned_data = []
    for msg in messages:
        if not msg['body']:
            logging.info(f"Skipping incomplete message: {msg}")
            continue
        transaction_details = extract_transaction_details(msg['body'])
        if not transaction_details['transaction_type']:
            logging.info(f"Skipping uncategorized message: {msg}")
            continue
        msg.update(transaction_details)
        cleaned_data.append(msg)
    return cleaned_data
