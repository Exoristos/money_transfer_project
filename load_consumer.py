import json
from neo4j_inserts import Neo4jConnection

def load_customers_to_neo4j(neo4j_conn, customers_file='customers.json'):
    """customers.json dosyasındaki tüm müşterileri Neo4j'e yükler."""
    if neo4j_conn.driver is None:
        print("Neo4j bağlantısı yok, müşteri verisi yüklenemedi.")
        return

    # Müşteri kimliği için benzersiz kısıtlama oluşturuyorum
    try:
        with neo4j_conn.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE")
    except Exception as e:
        print(f"Constraint oluşturulurken hata: {e}")


    print(f"'{customers_file}' dosyasından müşteriler Neo4j'e yükleniyor...")
    count = 0
    with open(customers_file, 'r', encoding='utf-8') as f:
        for line in f:
            customer_data = json.loads(line)
            with neo4j_conn.driver.session() as session:
                session.execute_write(_create_customer_node, customer_data)
                count += 1
    print(f"{count} müşteri başarıyla Neo4j'e yüklendi.")

def _create_customer_node(tx, customer_data):
    """Tek bir müşteri düğümü oluşturur veya günceller."""
    query = """
    MERGE (c:Customer {customer_id: $customer_id})
    ON CREATE SET
        c.name = $name,
        c.income_level = $income_level,
        c.country = $country,
        c.created_at = $created_at
    ON MATCH SET
        c.income_level = $income_level // Müşteri bilgisi güncellenirse diye
    """
    tx.run(query,
           customer_id=customer_data.get('customer_id'),
           name=customer_data.get('name'),
           income_level=customer_data.get('income_level'),
           country=customer_data.get('country'),
           created_at=customer_data.get('created_at')
           )

if __name__ == "__main__":
    # docker-compose.yml dosyasındaki şifreyi kullanıyoruz
    conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password123")
    load_customers_to_neo4j(conn)
    conn.close()