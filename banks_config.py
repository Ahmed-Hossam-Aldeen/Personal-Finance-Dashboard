import re
from dataclasses import dataclass
from typing import Pattern, Optional

@dataclass
class BankConfig:
    deduction_pattern: Pattern
    deduction_amount_group: int
    deduction_party_group: int
    
    addition_pattern: Pattern
    addition_amount_group: int
    addition_party_group: int
    
    debit_card_pattern: Pattern
    debit_card_amount_group: int
    debit_card_merchant_group: int



# --- PRE-COMPILED BANK REGEX CONFIGURATIONS ---
BANK_CONFIGS = {
    'CIB': BankConfig(
        deduction_pattern=re.compile(
            r"يرجى العلم انه تم تنفيذ تحويل لحظي بمبلغ\s+(?P<amount>[\d\.,]+)\s+جم من حسابك المنتهي بـ\s+(?P<account_last_4>.*?\d+) برقم مرجعي\s+(?P<ref>\w+) بتاريخ\s+(?P<date>[\d-]+)\s+(?P<time>[\d:]+)"
        ),
        deduction_amount_group=1,
        deduction_party_group=2,
        
        addition_pattern=re.compile(
            r"تم إضافة تحويل لحظي لحسابكم رقم\s+(?P<account>\d+)\s+بمبلغ\s+(?P<amount>[\d\.,]+)\s+جم\s+من\s+(?P<sender>.*?)\s+رقم مرجعي\s+(?P<ref>\d+)\s+يوم\s+(?P<date>[\d-]+)\s+الساعة\s+(?P<time>[\d:]+)"
        ),
        addition_amount_group=2,
        addition_party_group=3,

        debit_card_pattern = re.compile(
            r"(?:"
            r"Your credit card (?:ending with)?#\d+ was charged for EGP\s+(?P<amount_en>[\d.,]+)\s+at\s+(?P<merchant_en>.*?)\s+on\s+(?P<date_en>[\d/]+)\s+at\s+(?P<time_en>[\d:]+)"
            r"|"
            r"تم خصم مبلغ\s+EGP\s+(?P<amount_ar>[\d.,]+)\s+من بطاقة الخصم المباشر المنتهية بـ\s+\*+\d+\s+عند\s+(?P<merchant_ar>.*?)\s+في\s+(?P<date_ar>[\d/]+)\s+(?P<time_ar>[\d:]+)"
            r")",
            re.UNICODE
        ),
        debit_card_amount_group=1,
        debit_card_merchant_group=2
    ),
    'BanK-AlAhly': BankConfig(
        deduction_pattern=re.compile(
            r"تم تنفيذ تحويل لحظي من حسابكم رقم \d+ بمبلغ (?P<amount>[\d\.]+) جم إلى (?P<receiver>.*?) رقم مرجعي"
        ),
        deduction_amount_group=1,
        deduction_party_group=2,
        
        addition_pattern=re.compile(
            r"تم إضافة تحويل لحظي لحسابكم رقم\s+(?P<account>\d+)\s+بمبلغ\s+(?P<amount>[\d\.,]+)\s+جم\s+من\s+(?P<sender>.*?)\s+رقم مرجعي\s+(?P<ref>\d+)\s+يوم\s+(?P<date>[\d-]+)\s+الساعة\s+(?P<time>[\d:]+)"
        ),
        addition_amount_group=2,
        addition_party_group=3,
        
        debit_card_pattern=re.compile(
            r"تم خصم ([\d\.,]+)EGP.*?عند (.*?) يوم"
        ),
        debit_card_amount_group=1,
        debit_card_merchant_group=2
    )
}
