import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
import re

@st.cache_data
def load_and_process_data(xml_file_path, last_4_digits):
    def categorize(desc):
        desc = desc.upper()
        if any(x in desc for x in ['ATM', 'DAR EL SALAM']): return 'ATM'
        elif any(x in desc for x in ['BREADFAST', 'DEE POINT', 'FOOD', 'METRO', 'KAZYON', 'ASWAQ', 'NADA', 'SUPERMRKT', 'HAWARY']): return 'Groceries & Food'
        elif any(x in desc for x in ['GOOGLE', 'GETCONTACT']): return 'Tech & Subs'
        elif any(x in desc for x in ['THNDR', 'JEW']): return 'Investment'
        elif 'ETISALAT' in desc: return 'Telecom'
        elif 'UBER' in desc: return 'Transportation'
        elif 'LC WAIKIKI' in desc: return 'Clothing & Shopping'
        elif any(x in desc for x in ['PHAR', 'MEDI']): return 'Health & Pharmacy'
        elif 'FOREIGN EXCHANGE' in desc: return 'Fees'
        else: return 'Others'

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    deduction_pattern = r"تم تنفيذ تحويل لحظي من حسابكم رقم \d+ بمبلغ (?P<amount>[\d\.]+) جم إلى (?P<receiver>.*?) رقم مرجعي"
    addition_pattern = r"تم إضافة تحويل لحظي لحسابكم رقم\s+(?P<account>\d+)\s+بمبلغ\s+(?P<amount>[\d\.,]+)\s+جم\s+من\s+(?P<sender>.*?)\s+رقم مرجعي\s+(?P<ref>\d+)\s+يوم\s+(?P<date>[\d-]+)\s+الساعة\s+(?P<time>[\d:]+)"
    debit_card_pattern = r"تم خصم ([\d\.,]+)EGP.*?عند (.*?) يوم"
    
    transactions, transfers = [], []

    for sms in root.findall('sms'):
        address = sms.get('address')
        body = sms.get('body')
        date_str = sms.get('readable_date')

        if address == "BanK-AlAhly":
            # Transfers Out
            deduct_match = re.search(deduction_pattern, body)
            if deduct_match:
                dt = pd.to_datetime(date_str, format='%b %d, %Y %I:%M:%S %p')
                transfers.append({
                    'Date': dt, 'Type': 'Sent', 'Amount': float(deduct_match.group(1)),
                    'Party': deduct_match.group(2), 'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name()
                })

            # Transfers In
            add_match = re.search(addition_pattern, body)
            if add_match:
                dt = pd.to_datetime(date_str, format='%b %d, %Y %I:%M:%S %p')
                transfers.append({
                    'Date': dt, 'Type': 'Received', 'Amount': float(add_match.group(2).replace(',', '')),
                    'Party': add_match.group(3), 'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name()
                })

            # Card Transactions
            if last_4_digits in body:
                match = re.search(debit_card_pattern, body)
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    if amount > 0:
                        dt = pd.to_datetime(date_str, format='%b %d, %Y %I:%M:%S %p')
                        transactions.append({
                            'Date': dt, 'Amount': amount, 'Merchant': match.group(2).strip(),
                            'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name(),
                            'Category': categorize(match.group(2).strip())
                        })

    return pd.DataFrame(transactions), pd.DataFrame(transfers)