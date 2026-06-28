import xml.etree.ElementTree as ET
from datetime import datetime

def add_sms(root, address, body, date_obj):
    sms = ET.SubElement(root, "sms")
    sms.set("address", address)
    sms.set("body", body)
    sms.set("readable_date", date_obj.strftime("%b %d, %Y %I:%M:%S %p"))
    sms.set("date", str(int(date_obj.timestamp() * 1000)))

def generate_xml():
    root = ET.Element("smses")
    
    dt = datetime(2026, 6, 25, 21, 5, 0)
    
    # --- CIB ---
    bank = "CIB"
    add_sms(root, bank, "يرجى العلم انه تم تنفيذ تحويل لحظي بمبلغ 500.0 جم من حسابك المنتهي بـ 1234 برقم مرجعي REF123 بتاريخ 2026-06-25 21:05", dt)
    add_sms(root, bank, "تم إضافة تحويل لحظي لحسابكم رقم 123456 بمبلغ 150.0 جم من احمد محمد رقم مرجعي 98765 يوم 2026-06-25 الساعة 21:05", dt)
    add_sms(root, bank, "Your credit card ending with#1234 was charged for EGP 250.0 at UBER on 25/06/2026 at 21:05", dt)
    add_sms(root, bank, "تم خصم مبلغ EGP 100.0 من بطاقة الخصم المباشر المنتهية بـ ****1234 عند ZARA في 25/06/2026 21:05", dt)
    
    # --- BanK-AlAhly ---
    bank = "BanK-AlAhly"
    add_sms(root, bank, "تم تنفيذ تحويل لحظي من حسابكم رقم 123456 بمبلغ 300.0 جم إلى محمد احمد رقم مرجعي REF456", dt)
    add_sms(root, bank, "تم إضافة تحويل لحظي لحسابكم رقم 123456 بمبلغ 250.0 جم من سارة احمد رقم مرجعي 98765 يوم 2026-06-25 الساعة 21:05", dt)
    add_sms(root, bank, "تم خصم 150.0 EGP من بطاقة الخصم المباشر المنتهية بـ ****1234 عند CARREFOUR يوم 25/06/2026", dt)
    
    # --- AAIB ---
    bank = "AAIB"
    add_sms(root, bank, "Transfer reference #99988352 of EGP 500.00 has been debited from your account 1001-01 through IPN on 25/06/2026 at 21:05, your available balance is 967.69.", dt)
    add_sms(root, bank, "You have received a transfer reference #8ae6921d with EGP 200 from احمد حسام الدين حنفى محمود قناوى through IPN on 28/06/2026 at 08:18.", dt)
    add_sms(root, bank, "Your debit card **1234 was debited by EGP 320.00 at MCDONALDS. Available balance is EGP 1,925.19.", dt)
    
    tree = ET.ElementTree(root)
    tree.write("test_sms.xml", encoding="utf-8", xml_declaration=True)
    print("test_sms.xml generated successfully.")

if __name__ == "__main__":
    generate_xml()
