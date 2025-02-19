import re
from datetime import datetime
import logging
import os
from lxml import etree
from pathlib import Path

log_dir = "backend/log"
os.makedirs(log_dir, exist_ok=True)

log_file_path = os.path.join(log_dir, "transaction_parser.log")
logging.basicConfig(filename=log_file_path, level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")

def _parse_timestamp(timestamp_str):
    if timestamp_str:
        for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"]:
            try:
                return datetime.strptime(timestamp_str, fmt).isoformat()
            except ValueError:
                pass
    return None


def parse_transaction(body):
    body = re.sub(r"\*113\*R\*|\*165\*S\*|\*164\*S\*", "", body)

    if "Yello!Umaze kugura" in body:
        amount_match = re.search(r"([\d,]+(?:\.\d+)?)Rwf", body, re.IGNORECASE)
        timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})|" 
                                    r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})|" 
                                    r"(\d{4}-\d{2}-\d{2})|" 
                                    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", body)
        if timestamp_match:
            timestamp_str = next(filter(None, timestamp_match.groups()), None)
            timestamp = _parse_timestamp(timestamp_str)
        else:
            timestamp = None

        amount = float(amount_match.group(1).replace(",", "")) if amount_match else None
        if not all([amount, timestamp]):
            logging.warning(f"Failed to parse Yello!Umaze kugura: {body[:100]}...")
            return None

        fee_match = re.search(r"Fee\s+was\s*:? (\d+(?:,\d+)?)\s*RWF", body)
        fee = float(fee_match.group(1).replace(",", "")) if fee_match else 0.0

        return {"amount": amount, "type": "Purchase", "timestamp": timestamp, "transaction_id": None,
                "sender": None, "recipient": None, "fee": fee, "new_balance": None}

    transaction_data = {}

    sent_match = re.search(r"TxId: (\d+)\. Your payment of (\d+(?:,\d+)?) RWF to (.*?) (\d+) has been completed at (.*?)\. "
                           r"Your new balance: (\d+(?:,\d+)?) RWF\. Fee\s+was\s*:? (\d+(?:,\d+)?)\s*RWF", body)
    if sent_match:
        transaction_data.update({
            'transaction_id': sent_match.group(1),
            'amount': float(sent_match.group(2).replace(",", "")),
            'recipient': sent_match.group(3).strip(),
            'timestamp': _parse_timestamp(sent_match.group(5)),
            'new_balance': float(sent_match.group(6).replace(",", "")),
            'fee': float(sent_match.group(7).replace(",", "")),
            'type': "payment"
        })
        return transaction_data

    transfer_match = re.search(r"(\d+(?:,\d+)?) RWF transferred to (.*?) \((.*?)\) from (\d+) at (.*?)\. "
                               r"Fee\s+was\s*:? (\d+(?:,\d+)?)\s*RWF New balance: (\d+(?:,\d+)?) RWF\.", body)
    if transfer_match:
        transaction_data.update({
            'amount': float(transfer_match.group(1).replace(",", "")),
            'recipient': transfer_match.group(2).strip(),
            'timestamp': _parse_timestamp(transfer_match.group(5)),
            'fee': float(transfer_match.group(6).replace(",", "")),
            'new_balance': float(transfer_match.group(7).replace(",", "")),
            'type': "transfer"
        })
        return transaction_data

    deposit_match = re.search(r"A bank deposit of (\d+(?:,\d+)?) RWF has been added to your mobile money account at (.*?)\. "
                              r"Your NEW BALANCE :(\d+(?:,\d+)?) RWF\. Cash Deposit::CASH::::0::(.*?)\.Thank you.*", body)
    if deposit_match:
        transaction_data.update({
            'amount': float(deposit_match.group(1).replace(",", "")),
            'timestamp': _parse_timestamp(deposit_match.group(2)),
            'new_balance': float(deposit_match.group(3).replace(",", "")),
            'type': "deposit"
        })
        return transaction_data

    bill_payment_match = re.search(r"A transaction of (\d+(?:,\d+)?) RWF by (.*?) on your MOMO account was successfully completed at (.*?)\. "
                                   r"Your new balance:(\d+(?:,\d+)?) RWF\. Fee\s+was\s*:? (\d+(?:,\d+)?)\s*RWF Financial Transaction Id: (\d+)\. "
                                   r"External Transaction Id: (\d+)\.", body)
    if bill_payment_match:
        transaction_data.update({
            'amount': float(bill_payment_match.group(1).replace(",", "")),
            'recipient': bill_payment_match.group(2).strip(),
            'timestamp': _parse_timestamp(bill_payment_match.group(3)),
            'new_balance': float(bill_payment_match.group(4).replace(",", "")),
            'fee': float(bill_payment_match.group(5).replace(",", "")),
            'transaction_id': bill_payment_match.group(6),
            'type': "bill_payment"
        })
        return transaction_data

    return None

def extract_transaction_data(xml_file="data/modified_sms_v2.xml"):
    xml_path = Path(__file__).parent.parent / "data" / xml_file
    transactions = []
    try:
        tree = etree.parse(str(xml_path))
        root = tree.getroot()
        sms_elements = root.findall('.//sms')
        for sms in sms_elements:
            body = sms.get('body')
            if body:
                try:
                    transaction = parse_transaction(body)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logging.warning(f"Error parsing SMS: {body[:50]}... - Error: {e}")
    except (FileNotFoundError, etree.XMLSyntaxError) as e:
        logging.warning(f"Error processing XML: {e}")
        return []
    return transactions
