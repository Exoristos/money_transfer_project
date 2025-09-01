import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')#lambda ile json verisini utf-8 olarak kodluyorum def kullanmıyoruz çünkü json.dumps() fonksiyonunu lambda ile tek satırda kullanmak daha pratik oluyor
)

print("Producer başlatıldı. Transferler gönderiliyor...")

with open('transfers.json', 'r', encoding='utf-8') as f:
    for line in f:
        transfer = json.loads(line)


        producer.send('money_transfers', value=transfer)
        print(f"Gönderildi: {transfer['transfer_id']}")

        #Gerçek bir zamanlı akış oluşturmak için dökümanda verilen gecikmeyi ekliyorum
        time.sleep(random.uniform(0.01, 0.05))

# Tüm mesajların gönderildiğinden emin olmak için bekliyoruz
producer.flush()
print("Tüm transferler başarıyla gönderildi.")