from neo4j import GraphDatabase


class Neo4jConnection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            self.driver.verify_connectivity()
            print("Neo4j bağlantısı başarılı.")
        except Exception as e:
            print(f"Neo4j bağlantı hatası: {e}")
            self.driver = None

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def insert_transfer(self, transfer_data):
        if self.driver is None:
            print("Neo4j bağlantısı yok, veri yazılamadı.")
            return

        with self.driver.session() as session:
            session.execute_write(self._create_transfer_relationship, transfer_data)
            print(f"Neo4j'e yazıldı: {transfer_data.get('transfer_id')}")

    @staticmethod
    def _create_transfer_relationship(tx, transfer_data):
        sender_id = transfer_data.get('sender_id')
        receiver_id = transfer_data.get('receiver_id')

        query = (
            "MERGE (sender:Customer {customer_id: $sender_id}) "
            "MERGE (receiver:Customer {customer_id: $receiver_id}) "
            "CREATE (sender)-[:SENT { "
            "  transfer_id: $transfer_id, "
            "  amount: $amount, "
            "  timestamp: $timestamp "
            "}]->(receiver)"
        )

        tx.run(query,
               sender_id=sender_id,
               receiver_id=receiver_id,
               transfer_id=transfer_data.get('transfer_id'),
               amount=transfer_data.get('amount'),
               timestamp=transfer_data.get('timestamp'))