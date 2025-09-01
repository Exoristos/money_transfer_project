import json
import time
from kafka import KafkaConsumer
from neo4j_inserts import Neo4jConnection

# Sahtekarlık tespiti için yapılandırma
FRAUD_CONFIG = {
    # Bir transfer, müşterinin aylık gelirinin %80'inden fazlaysa şüpheli kabul ediyorum
    "INCOME_RATIO_THRESHOLD": 0.8,
    "RAPID_TRANSACTION": {
        "COUNT": 10,  # 1 saat içinde 10'dan fazla işlem yaparsa şüpheli kabul ediyorum
        "TIMEFRAME_SECONDS": 3600  # 1 saat
    }
}

def check_for_fraud(neo4j_conn, transfer_data):
    sender_id = transfer_data['sender_id']
    receiver_id = transfer_data['receiver_id']
    amount = transfer_data.get('amount', 0)
    transfer_id = transfer_data['transfer_id']

    # Tüm sorgular için tek bir session kullanmak daha verimlidir.
    with neo4j_conn.driver.session() as session:
        # 1. kural için kod bloğum: Gelire Oranla Şüpheli Tutar
        # Göndericinin gelir bilgisini Neo4j'den alıyorum
        query_income = "MATCH (c:Customer {customer_id: $sender_id}) RETURN c.income_level AS income"
        result_income = session.run(query_income, sender_id=sender_id).single()

        if result_income and result_income['income']:
            sender_income = result_income['income']
            # Gelir 0'dan büyükse ve oran eşiği aşıyorsa
            if sender_income > 0 and (amount / sender_income) > FRAUD_CONFIG["INCOME_RATIO_THRESHOLD"]:
                print(f"[!!!] ŞÜPHELİ İŞLEM (Gelire Oranla Yüksek Tutar): "
                      f"Transfer ID: {transfer_id}, Tutar: {amount}, Müşteri Geliri: {sender_income}")

        # 2. kural için kod bloğum: Hızlı ve Çok Sayıda İşlem
        query_rapid_tx = """
        MATCH (sender:Customer {customer_id: $sender_id})-[r:SENT]->()
        WHERE r.timestamp >= $start_time
        RETURN count(r) AS transaction_count
        """
        # Zaman çerçevesini hesapla (son 1 saat)
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - FRAUD_CONFIG["RAPID_TRANSACTION"]["TIMEFRAME_SECONDS"]))
        result_rapid = session.run(query_rapid_tx, sender_id=sender_id, start_time=start_time).single()

        if result_rapid and result_rapid["transaction_count"] > FRAUD_CONFIG["RAPID_TRANSACTION"]["COUNT"]:
            print(f"[!!!] ŞÜPHELİ AKTİVİTE (Hızlı İşlemler): Müşteri ID: {sender_id}, Son 1 saatteki işlem sayısı: {result_rapid['transaction_count']}")

        # Kural 3: Döngüsel Transfer Kontrolü
        # Yeni işlemle birlikte alıcıdan göndericiye 2 adımda bir yol oluşup oluşmadığını kontrol eder.
        query_circular_tx = """
        MATCH path = (:Customer {customer_id: $receiver_id})-[:SENT*2]->(:Customer {customer_id: $sender_id})
        RETURN path LIMIT 1
        """
        result_circular = session.run(query_circular_tx, sender_id=sender_id, receiver_id=receiver_id)
        # Eğer en az bir sonuç varsa (peek() ile veriyi çekmeden kontrol ederiz)
        if result_circular.peek():
             print(f"[!!!] ŞÜPHELİ İŞLEM (Döngüsel Transfer): Transfer ID: {transfer_id} bir döngü oluşturuyor.")


def main():
    neo4j_conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password123")

    if neo4j_conn.driver is None:
        return

    consumer = KafkaConsumer(
        'money_transfers',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='money-transfer-fraud-detector-group' # Grup ID'sini değiştirmek iyi bir pratik olabilir
    )

    print("Consumer başlatıldı. Mesajlar dinleniyor ve sahtekarlık kontrolü yapılıyor...")

    for message in consumer:
        transfer_data = message.value

        if transfer_data.get('status') == 'completed':
            try:
                # 1. Adım: Transferi veritabanına yazıyoruz
                neo4j_conn.insert_transfer(transfer_data)

                # 2. Adım: Veri üzerine sahtekarlık kontrolü
                check_for_fraud(neo4j_conn, transfer_data)

            except Exception as e:
                print(f"Veri işlenirken hata oluştu: {e}")
        else:
            # 'completed' olmayan transferleri atla
            print(f"Atlandı (durum 'completed' değil): {transfer_data.get('transfer_id')}")

    neo4j_conn.close()


if __name__ == "__main__":
    main()