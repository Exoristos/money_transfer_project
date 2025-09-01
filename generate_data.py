# ----------------------------------------------------
#  Gerçekçi Müşteri ve Transfer Verisi Oluşturucu
#  Author: Enis Erdoğan/Exoristos
#  Date: 16-08-2025
#
#  Bu python kodu rastgele müşteri verileri ve bu müşteriler arasındaki
#  finansal transferlerini üreten bir betiktir
# ----------------------------------------------------

import json
import random
import uuid
from faker import Faker

#Gerçek bir veri olması için farklı ülkelerden müşteri verileri oluşturuyorum
fakers = {
    "Türkiye": Faker("tr_TR"),
    "Deutschland": Faker("de_DE"),
    "France": Faker("fr_FR"),
    "UK": Faker("en_GB"),
    "USA": Faker("en_US"),
    "Spain": Faker("es_ES"),
    "Italy": Faker("it_IT"),
    "Netherlands": Faker("nl_NL"),
    "Japan": Faker("ja_JP"),
    "India": Faker("en_IN"),
}
#Ülkelere ağırlıklar atıyorum
countries = ["Türkiye", "Deutschland", "France", "UK", "USA", "Spain", "Italy", "Netherlands", "Japan", "India"]
country_weights = [0.30, 0.10, 0.07, 0.10, 0.08, 0.07, 0.07, 0.07, 0.07, 0.07]

cities = {
    "Türkiye": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"],
    "Deutschland": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Dortmund"],
    "France": ["Paris", "Lyon", "Marsiella", "Nice", "Toulouse"],
    "UK": ["London", "Manchester", "Liverpool", "Birmingham", "Leeds"],
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Miami"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven"],
    "Japan": ["Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad"]
}
#Verinin gerçekçi olması için ülkelerin gelir aralıklarını belirliyorum
income_ranges = {
    "Türkiye": (800, 5000),
    "Deutschland": (2500, 12000),
    "France": (2200, 11000),
    "UK": (2400, 13000),
    "USA": (3000, 15000),
    "Spain": (1800, 9000),
    "Italy": (1700, 8500),
    "Netherlands": (2800, 14000),
    "Japan": (2500, 11000),
    "India": (400, 3500)
}
#Telefon formatlarını doğru şekilde tanımlıyorum
phone_formats = {
    "Türkiye": {"code": "+90", "length": 10},
    "Deutschland": {"code": "+49", "length": 10},
    "France": {"code": "+33", "length": 9},
    "UK": {"code": "+44", "length": 10},
    "USA": {"code": "+1", "length": 10},
    "Spain": {"code": "+34", "length": 9},
    "Italy": {"code": "+39", "length": 10},
    "Netherlands": {"code": "+31", "length": 9},
    "Japan": {"code": "+81", "length": 10},
    "India": {"code": "+91", "length": 10}
    }
#İnternetten bulduğum formatlara göre telefon numaralarını düzenliyorum
def format_phone(country):
    info = phone_formats[country]
    digits = ''.join([str(random.randint(0, 9)) for _ in range(info["length"])])
    if country == "France":
        return f"{info['code']} {digits[:1]} {digits[1:3]} {digits[3:5]} {digits[5:7]} {digits[7:]}"
    elif country == "USA":
        return f"{info['code']} {digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif country == "UK":
        return f"{info['code']} {digits[:4]} {digits[4:7]} {digits[7:]}"
    elif country == "Deutschland":
        return f"{info['code']} {digits[:3]} {digits[3:6]} {digits[6:]}"
    elif country == "Spain":
        return f"{info['code']} {digits[:3]} {digits[3:6]} {digits[6:]}"
    elif country == "Italy":
        return f"{info['code']} {digits[:3]} {digits[3:]}"
    elif country == "Netherlands":
        return f"{info['code']} {digits[:2]} {digits[2:]}"
    elif country == "Japan":
        return f"{info['code']} {digits[:2]}-{digits[2:6]}-{digits[6:]}"
    elif country == "India":
        return f"{info['code']} {digits[:5]} {digits[5:]}"
    else:  # Türkiye
        return f"{info['code']} {digits[:3]} {digits[3:6]} {digits[6:]}"

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

#Müşteri verilerini oluşturmak için fonksiyon
def generate_customer():
    country = random.choices(countries, weights=country_weights, k=1)[0]
    fake = fakers[country]
    city = random.choice(cities[country])
    job = fake.job()
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=70)
    phone = format_phone(country)
    min_income, max_income = income_ranges[country]
    income = round(random.uniform(min_income, max_income), 2)

    name = fake.name()
    name_parts = name.split(' ')
    while name_parts and name_parts[0].endswith('.'):
        name_parts.pop(0)
    name = ' '.join(name_parts)
#Email adresini oluştururken karmaşık bir görüntü çıkmaması için 2'den fazla ismi olan kişilerin sadece isim ve soyisim kombinasyonlarını kullanıyorum
    if len(name_parts) > 2:
        email_user = f"{name_parts[0]}.{name_parts[-1]}"
    else:
        email_user = '.'.join(name_parts)
# Eğer isimde Türkçe karakterler varsa, bunları İngilizce karakterlerle değiştiriyorum
    email_user = email_user.lower()
    replacements = {'ı': 'i', 'ğ': 'g', 'ş': 's', 'ç': 'c', 'ö': 'o', 'ü': 'u'}
    for old, new in replacements.items():
        email_user = email_user.replace(old, new)

    if random.random() > 0.7:
        email_user += str(random.randint(1, 99))

    email = f"{email_user}@{fake.free_email_domain()}"

    return {
        "customer_id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "gender": random.choice(["male", "female"]),
        "country": country,
        "city": city,
        "job_title": job,
        "birthdate": format_date(birthdate),
        "phone": phone,
        "income_level": income,
        "created_at": fake.date_time_this_decade().strftime("%Y-%m-%d %H:%M:%S")
    }
#Müşteri verisini oluşturdum

#Transfer verileri oluşturmak için fonksiyon yazıyorum

def generate_transaction(sender_id, all_customer_ids, fake_instance):
    receiver_id = random.choice(all_customer_ids)
    # Gönderen ve alıcı aynı olursa tekrardan seçim yapıyorum
    while receiver_id == sender_id:
        receiver_id = random.choice(all_customer_ids)

    return {
        "transfer_id": str(uuid.uuid4()),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": round(random.uniform(10.00, 1000.00), 2),
        "currency": "USD",
        "timestamp": fake_instance.date_time_between(start_date='-2y', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
        "status": random.choices(["completed", "pending", "failed"], weights=[85, 10, 5], k=1)[0],
        "channel": random.choices(["mobile_app", "web", "api", "atm"], weights=[50, 35, 10, 5], k=1)[0]
    }

#Müşterileri oluşturma ve transfer verilerini yazma işlemini gerçekleştiren ana fonksiyonu tanımlıyorum
def main():
    customer_count = 20000
    customers = []
    customer_ids = []
#Başta tanımladığım fonksiyonları kullanarak müşteri verilerini oluşturuyorum
    print(f"{customer_count} adet müşteri verisi oluşturuluyor...")
    for _ in range(customer_count):
        customer = generate_customer()
        customers.append(customer)
        customer_ids.append(customer['customer_id'])

    with open('customers.json', 'w', encoding='utf-8') as f:
        for customer in customers:
            f.write(json.dumps(customer, ensure_ascii=False) + '\n')
    print(f"'{'customers.json'}' dosyasına {len(customers)} müşteri başarıyla yazıldı.")

    print("\nTransfer verileri oluşturuluyor. Bu işlem biraz zaman alabilir...")
    file_path = 'transfers.json'
    transaction_count = 0
    fake_generic = Faker()

    random.shuffle(customer_ids)
#Müşteri verilerini karıştırdım ve her müşteri için rastgele transfer verileri oluşturuyorum
    with open(file_path, 'w', encoding='utf-8') as f:
        for sender_id in customer_ids:
            num_transactions = random.randint(2, 20)
            for _ in range(num_transactions):
                single_transaction = generate_transaction(sender_id, customer_ids, fake_generic)
                f.write(json.dumps(single_transaction) + '\n')
                transaction_count += 1

    print(f"İşlem tamamlandı! Toplam {transaction_count} adet transfer oluşturuldu ve '{file_path}' dosyasına yazıldı.")

if __name__ == "__main__":
    main()

