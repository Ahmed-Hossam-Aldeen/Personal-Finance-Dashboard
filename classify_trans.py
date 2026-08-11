import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- CATEGORY KEYWORDS CONFIG ---
CATEGORIES = {
    'Fees': [
        'FOREIGN EXCHANGE', 'PASSPORT', 'FEES', 'COMMISSION', 'STAMP', 'TAX', 
        'RENEWAL', 'TRAFFIC', 'AMAN', 'EGYPTIAN CUSTOM', 'NEQABTY', 'PENSION', 'ABYAR'
    ],
    'Entertainment & Subs': [
        'ELSAWY', 'GOOGLE', 'GETCONTACT', 'NETFLIX', 'SPOTIFY', 'MICROSOFT', 
        'OPENAI', 'LINKEDIN', 'APPLE', 'ITUNES', 'ACADEMY', 'THEMES','CINEMA', 'CINEMA', 'MOVIE', 'PLAYSTATION', 'XBOX', 'GAMING'
    ],
    'ATM': [
        'ATM', 'NATIONAL BANK OF EGYPT', 'DAR EL SALAM', 'CIB', 'QNB', 'BM', 
        'BANQUE MISR', 'WITHDRAWAL'
    ],
    'Investment': [
        'FINANCE', 'THNDR', 'JEW', 'HALAN', 'EFG', 'VALU', 'HERMES', 'MISR CAP'
    ],
    'Home & Electronics': [
        'IKEA', 'ELTAWHEED', 'HOME', 'DREAM 2000', 'SELECT', 'EL ARABY', 
        'SHARAF DG', 'B TECH', 'KIRIAZI', 'LIZARHOME', '2B', 'TRADELINE', 
        'DREAM'
    ],
    'Groceries & Food': [
        'BREADFAST', 'DEE POINT', 'FOOD', 'METRO', 'KAZYON', 'ASWAQ', 'NADA', 
        'TALABAT', 'SPINNEYS', 'MARKT', 'MARKET', 'SUPERMRKT', 'HAWARY', 
        'CARREFOUR', 'PIZZA', 'COFFEE', 'ROOSTERS', 'SEOUDI', 'LULU', 'ALFA', 
        'LYFE', 'AGA', 'SECOND CUP', 'ETOILE', 'BAZOOKA', 'COOK DOOR', 
        'MCDONALDS', 'KFC', 'BURGER KING', 'MOLLYS', 'KATURA', 'BEANOS', 
        'CILANTRO', 'CAFE', 'WOK', 'TRUCK', 'BREW', 'ELMADENA ALMONWARA', 
        'ELMADENA','ELMADINA', 'GOMLA', 'FATHALLA', 'COSTA', 'CINNABON', 'ELABD', 
        'STARBUCKS', 'DUNKIN', 'BAKERY', 'LAMOAGHZA', 'ABU AUF', 'QAHWA', 
        'ESPRESSO', 'BAKE', '1980', 'GOURMET', 'FOAM', 'SIP', 'ICE CREAM', 
        'MANDARINE', 'ELKEBIR', 'WHAT THE TRUC', '30 NORTH', 'MASHWY', 
        'BEST BUY', 'ARDNA', 'RDNA', 'TEA', 'ABW BRYN','KUFTA', 'KOUEIDER',
        'CIRCLE K', 'GELATO', 'MAYYAL', 'ABO ANAS', 'KOWAYDA',
        'LOKALI', 'VASKO', 'ZAHIO', 'ALAMYR','FRGHLY'
    ],
    'Clothing & Shopping': [
        'LC WAIKIKI', 'MAX', 'SHOES', 'SCARVES', 'CLOTHIN', 'DICE', 'LEATHER', 
        'DEFACTO', 'MINTRA', 'COTONIL', 'BAHYA', 'HEGABE', 'ZARA', 'H&M', 'AMAZON', 
        'JUMIA', 'BERSHKA', 'STRADIVARIUS', 'PULL & BEAR', 'ALDO', 'MISS DIVA', 
        'TIMBERLAND', 'ADIDAS', 'NIKE', 'FRAGRA', 'DECATHLON', 'CLOTHES'
    ],
    'Health & Pharmacy': [
        'ANEES', 'GYM', 'AFRICANA', 'PHAR', 'PHARMACY', 'MEDI', 'ALMOKHTABAR', 
        'EZABY', 'SEIF', '19011', 'PHARM', 'VEZEETA', 'DR', 'HOSPITAL', 'LASELIA'
    ],
    'Telecom': [
        'ETISALAT', 'VODAFONE', 'ORANGE', 'WE ', 'TE DATA', 'MYFAWRY'
    ],
    'Transportation': [
        'UBER', 'DIDY', 'INDRIVE', 'SWVL', 'CAREEM'
    ]
}

def categorize(desc: str) -> str:
    """Categorizes the transaction merchant name using predefined keyword mappings."""
    if '*' in desc:
        desc = desc.split('*')[1]
    desc = desc.upper()
    
    for category, keywords in CATEGORIES.items():
        if any(keyword in desc for keyword in keywords):
            return category
    logging.warning(f"Couldn't identify {desc}")        
    return 'Others'