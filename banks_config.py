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
    
    english_card_pattern: Optional[Pattern] = None
    arabic_card_pattern: Optional[Pattern] = None

    debit_card_amount_group: str = "amount"
    debit_card_merchant_group: str = "merchant"



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

        english_card_pattern = re.compile(
            r"Your credit card (?:ending with)?#\d+ was charged for EGP\s+"
            r"(?P<amount>[\d.,]+)\s+at\s+"
            r"(?P<merchant>.*?)\s+on\s+"
            r"(?P<date>[\d/]+)\s+at\s+"
            r"(?P<time>[\d:]+)"
        ),

        arabic_card_pattern = re.compile(
            r"تم خصم مبلغ\s+EGP\s+"
            r"(?P<amount>[\d.,]+)\s+"
            r"من بطاقة الخصم المباشر المنتهية بـ\s+\*+\d+\s+"
            r"عند\s+(?P<merchant>.*?)\s+"
            r"في\s+(?P<date>[\d/]+)\s+"
            r"(?P<time>[\d:]+)"
        ),

        debit_card_amount_group="amount",
        debit_card_merchant_group="merchant"
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
        
       arabic_card_pattern=re.compile(
            r"تم خصم (?P<amount>[\d\.,]+)EGP.*?عند (?P<merchant>.*?) يوم"
        ),
        debit_card_amount_group="amount",
        debit_card_merchant_group="merchant"
    )
}
