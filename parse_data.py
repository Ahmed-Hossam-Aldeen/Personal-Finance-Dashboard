import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
import re

@st.cache_data
def load_and_process_data(xml_file_path, last_4_digits):
    def categorize(desc):
        desc = desc.upper()
        
        # 1. Fees & Government
        if any(x in desc for x in ['FOREIGN EXCHANGE', 'PASSPORT', 'FEES', 'COMMISSION', 'STAMP', 'TAX', 'RENEWAL', 'TRAFFIC', 'AMAN']): 
            return 'Fees'
        
        # 2. Cash & ATM
        elif any(x in desc for x in ['ATM', 'DAR EL SALAM', 'CIB', 'QNB', 'BANQUE MISR', 'WITHDRAWAL']): 
            return 'ATM'
        
        # 3. Groceries & Food
        elif any(x in desc for x in [
            'BREADFAST', 'DEE POINT', 'FOOD', 'METRO', 'KAZYON', 'ASWAQ', 'NADA', 'TALABAT', 'SPINNEYS',
            'SUPERMRKT', 'HAWARY', 'CARREFOUR', 'PIZZA', 'COFFEE', 'ROOSTERS', 'SEOUDI', 'LULU', 'ALFA',
            'AGA', 'SECOND CUP', 'ETOILE', 'BAZOOKA', 'COOK DOOR', 'MCDONALDS', 'KFC', 'BURGER KING', 
            'GOMLA', 'FATHALLA', 'COSTA', 'CINNABON', 'ELABD', 'STARBUCKS', 'DUNKIN'
        ]): 
            return 'Groceries & Food'

        # 4. Clothing & Shopping
        elif any(x in desc for x in [
            'LC WAIKIKI', 'MAX', 'SHOES', 'SCARVES', 'CLOTHIN', 'DICE', 'LEATHER', 'DEFACTO', 'COTONIL', 
            'BAHYA', 'HEGABE', 'ZARA', 'H&M', 'AMAZON', 'JUMIA', 'BERSHKA', 'STRADIVARIUS', 'PULL & BEAR', 
            'ALDO', 'MISS DIVA', 'TIMBERLAND', 'ADIDAS', 'NIKE'
        ]): 
            return 'Clothing & Shopping'
        
        # 5. Home & Electronics
        elif any(x in desc for x in [
            'IKEA', 'ELTAWHEED', 'HOME', 'DREAM 2000', 'SELECT', 'EL ARABY', 'SHARAF DG', 'B TECH', 
            'KIRIAZI', 'LIZARHOME', '2B', 'TRADELINE'
        ]): 
            return 'Home & Electronics'
        
        # 6. Health & Pharmacy
        elif any(x in desc for x in ['PHAR', 'MEDI', 'ALMOKHTABAR', 'EZABY', 'SEIF', '19011', 'MISR PHARM', 'VEZEETA']): 
            return 'Health & Pharmacy'
        
        # 7. Tech & Subs
        elif any(x in desc for x in ['GOOGLE', 'GETCONTACT', 'NETFLIX', 'SPOTIFY', 'MICROSOFT', 'OPENAI', 'LINKEDIN', 'APPLE', 'ITUNES']): 
            return 'Tech & Subs'
        
        # 8. Investment & Finance
        elif any(x in desc for x in ['THNDR', 'JEW', 'HALAN', 'EFG', 'VALU', 'HERMES', 'MISR CAP']): 
            return 'Investment'
        
        # 9. Telecom
        elif any(x in desc for x in ['ETISALAT', 'VODAFONE', 'ORANGE', 'WE ', 'TE DATA']): 
            return 'Telecom'
            
        # 10. Transportation
        elif any(x in desc for x in ['UBER', 'DIDY', 'INDRIVE', 'SWVL', 'CAREEM']): 
            return 'Transportation'
        
        else: 
            return 'Others'

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