import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Optional
from banks_config import *
from classify_trans import *

# --- CUSTOM EXCEPTIONS ---
class DataParsingError(Exception):
    """Base exception for data parsing errors."""
    pass

class CardDigitsNotFoundError(DataParsingError):
    """Exception raised when the provided card digits do not match any transactions."""
    pass



def parse_date(date_str: Optional[str], epoch_str: Optional[str]) -> pd.Timestamp:
    """Parses SMS dates with fallback options to handle varied locales and formats."""
    if date_str:
        for fmt in ('%b %d, %Y %I:%M:%S %p', '%d/%m/%Y %I:%M:%S %p', '%Y-%m-%d %H:%M:%S'):
            try:
                return pd.to_datetime(date_str, format=fmt)
            except (ValueError, TypeError):
                continue
        try:
            return pd.to_datetime(date_str)
        except (ValueError, TypeError):
            pass

    if epoch_str:
        try:
            return pd.to_datetime(int(epoch_str), unit='ms')
        except (ValueError, TypeError):
            pass

    return pd.Timestamp.now()

@st.cache_data
def load_and_process_data(xml_file, last_4_digits: str, target_bank: str):
    """Parses and loads bank transaction/transfer data from the uploaded XML file."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        raise DataParsingError(f"Malformed XML file structure: {e}")
    except Exception as e:
        raise DataParsingError(f"Failed to read XML document: {e}")

    config = BANK_CONFIGS.get(target_bank)
    if not config:
        raise DataParsingError(f"Unsupported bank option: {target_bank}")

    transactions, transfers = [], []
    is_last_4_digits_found = False

    for sms in root.findall('sms'):
        address = sms.get('address')
        body = sms.get('body', '')
        date_str = sms.get('readable_date')
        epoch_str = sms.get('date')

        if address == target_bank:
            # Transfers Out
            deduct_match = config.deduction_pattern.search(body)
            if deduct_match:
                dt = parse_date(date_str, epoch_str)
                try:
                    amount_str = deduct_match.group(config.deduction_amount_group).replace(',', '')
                    amount = float(amount_str)
                    party = deduct_match.group(config.deduction_party_group).strip()
                    transfers.append({
                        'Date': dt, 'Type': 'Sent', 'Amount': amount,
                        'Party': party, 'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name()
                    })
                except (ValueError, IndexError, AttributeError):
                    pass

            # Transfers In
            add_match = config.addition_pattern.search(body)
            if add_match:
                dt = parse_date(date_str, epoch_str)
                try:
                    amount_str = add_match.group(config.addition_amount_group).replace(',', '')
                    amount = float(amount_str)
                    party = add_match.group(config.addition_party_group).strip()
                    transfers.append({
                        'Date': dt, 'Type': 'Received', 'Amount': amount,
                        'Party': party, 'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name()
                    })
                except (ValueError, IndexError, AttributeError):
                    pass

            # Card Transactions
            if last_4_digits in body:
                match = None
                if config.english_card_pattern:
                    match = config.english_card_pattern.search(body)
                if not match and config.arabic_card_pattern:
                    match = config.arabic_card_pattern.search(body)  

                if match:
                    is_last_4_digits_found = True
                    try:
                        amount_str = match.group(config.debit_card_amount_group).replace(',', '')
                        amount = float(amount_str)
                        if amount > 0:
                            dt = parse_date(date_str, epoch_str)
                            merchant = match.group(config.debit_card_merchant_group).strip()
                            transactions.append({
                                'Date': dt, 'Amount': amount, 'Merchant': merchant,
                                'Hour': dt.hour, 'Day': dt.day_name(), 'Month': dt.month_name(),
                                'Category': categorize(merchant)
                            })
                    except Exception as e:
                        logging.warning(
                            f"Failed parsing card transaction: {body[:100]}... Error: {e}"
                        )

    if not is_last_4_digits_found:
        raise CardDigitsNotFoundError(
            f"No card transactions detected for card ending with '{last_4_digits}' in your {target_bank} messages."
        )

    trans_cols = ['Date', 'Amount', 'Merchant', 'Hour', 'Day', 'Month', 'Category']
    transfer_cols = ['Date', 'Type', 'Amount', 'Party', 'Hour', 'Day', 'Month']

    df_trans = pd.DataFrame(transactions)
    if df_trans.empty:
        df_trans = pd.DataFrame(columns=trans_cols)
    else:
        # Ensure all required columns are present
        for col in trans_cols:
            if col not in df_trans.columns:
                df_trans[col] = pd.Series(dtype='object')

    df_tranf = pd.DataFrame(transfers)
    if df_tranf.empty:
        df_tranf = pd.DataFrame(columns=transfer_cols)
    else:
        # Ensure all required columns are present
        for col in transfer_cols:
            if col not in df_tranf.columns:
                df_tranf[col] = pd.Series(dtype='object')

    return df_trans, df_tranf