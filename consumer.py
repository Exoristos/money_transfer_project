import json
from kafka import KafkaConsumer
from neo4j_inserts import Neo4jConnection


def main():
    neo4j_conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password123")

    if neo4j_conn.driver is None:
        return

    consumer = KafkaConsumer(
        'money_transfers',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',#Producer'ı erkenden başlattığımız senaryoda consumer başlamadan önce gelen mesajları okuması için earliest yapıyorum
        group_id='money-transfer-neo4j-group'
    )

    print("Consumer başlatıldı. Mesajlar dinleniyor...")

    for message in consumer:
        transfer_data = message.value

        if transfer_data.get('status') == 'completed':
            try:
                neo4j_conn.insert_transfer(transfer_data)
            except Exception as e:
                print(f"Veri işlenirken hata oluştu: {e}")
        else:
            print(f"Atlandı (durum 'completed' değil): {transfer_data.get('transfer_id')}")

    neo4j_conn.close()


if __name__ == "__main__":
    main()