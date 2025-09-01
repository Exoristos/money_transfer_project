import streamlit as st
import pandas as pd
from neo4j_inserts import Neo4jConnection

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="Para Transferi Analiz Panosu", layout="wide")

# --- Neo4j Bağlantısı ---
# Streamlit'in cache mekanizması sayesinde bağlantı her etkileşimde yeniden kurulmaz.
@st.cache_resource
def get_neo4j_connection():
    """Neo4j bağlantısını başlatır ve cache'ler."""
    # docker-compose.yml dosyasındaki şifreyi kullanıyoruz
    conn = Neo4jConnection("neo4j://localhost:7687", "neo4j", "password123")
    if conn.driver is None:
        st.error("Neo4j bağlantısı kurulamadı. Docker konteynerinin çalıştığından emin olun.")
        st.stop()
    return conn

# --- Sorgu Fonksiyonları ---
def run_query(conn, query, params=None):
    """Verilen Cypher sorgusunu çalıştırır ve sonucu DataFrame olarak döndürür."""
    with conn.driver.session() as session:
        result = session.run(query, params)
        # Sonuçları bir liste sözlüğe dönüştür
        data = [record.data() for record in result]
        return pd.DataFrame(data)

# --- Ana Pano Arayüzü ---
st.title("💸 Para Transferi Akışı Analiz Panosu")
st.markdown("Bu pano, Kafka üzerinden akan ve Neo4j'de depolanan para transferi verilerini analiz eder.")

# Bağlantıyı al
neo4j_conn = get_neo4j_connection()

# --- Kenar Çubuğu (Sidebar) ---
st.sidebar.header("Analiz Seçenekleri")
analysis_type = st.sidebar.radio(
    "Görmek istediğiniz analiz türünü seçin:",
    ("Genel Bakış", "Müşteri Detay Analizi", "Sahtekarlık ve Şüpheli Aktiviteler")
)

# --- Analiz Sayfaları ---

# 1. Genel Bakış Sayfası
if analysis_type == "Genel Bakış":
    st.header("Genel Bakış ve Lider Tabloları")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("En Çok Transfer Yapan 10 Müşteri (İşlem Sayısı)")
        query_top_senders = """
        MATCH (sender:Customer)-[r:SENT]->()
        RETURN sender.customer_id AS Musteri_ID, sender.name AS Isim, count(r) AS Islem_Sayisi
        ORDER BY Islem_Sayisi DESC LIMIT 10
        """
        top_senders_df = run_query(neo4j_conn, query_top_senders)
        st.dataframe(top_senders_df, use_container_width=True)

    with col2:
        st.subheader("En Çok Transfer Alan 10 Müşteri (İşlem Sayısı)")
        query_top_receivers = """
        MATCH (receiver:Customer)<-[r:SENT]-()
        RETURN receiver.customer_id AS Musteri_ID, receiver.name AS Isim, count(r) AS Islem_Sayisi
        ORDER BY Islem_Sayisi DESC LIMIT 10
        """
        top_receivers_df = run_query(neo4j_conn, query_top_receivers)
        st.dataframe(top_receivers_df, use_container_width=True)

    st.subheader("Ülkelere Göre Transfer Hacmi")
    query_country_volume = """
    MATCH (sender:Customer)-[r:SENT]->(receiver:Customer)
    WHERE sender.country IS NOT NULL AND receiver.country IS NOT NULL AND sender.country <> receiver.country
    RETURN sender.country AS Gonderen_Ulke, receiver.country AS Alan_Ulke, count(r) as Islem_Sayisi, sum(r.amount) as Toplam_Tutar
    ORDER BY Islem_Sayisi DESC LIMIT 20
    """
    country_volume_df = run_query(neo4j_conn, query_country_volume)
    st.dataframe(country_volume_df, use_container_width=True)


# 2. Müşteri Detay Analizi Sayfası
elif analysis_type == "Müşteri Detay Analizi":
    st.header("Müşteri Detay Analizi")
    customer_id_input = st.text_input("Analiz etmek için bir Müşteri ID'si girin:", placeholder="Örn: 5f8f8c...")

    if customer_id_input:
        st.subheader(f"Müşteri '{customer_id_input}' için Bağlantılar")
        query_connections = """
        MATCH (c:Customer {customer_id: $customer_id})-[r:SENT]-(other:Customer)
        RETURN c.customer_id as Kaynak, type(r) as Iliski, other.customer_id as Hedef, r.amount as Tutar
        """
        connections_df = run_query(neo4j_conn, query_connections, params={"customer_id": customer_id_input})

        if not connections_df.empty:
            st.dataframe(connections_df, use_container_width=True)
        else:
            st.warning("Bu müşteri için herhangi bir bağlantı bulunamadı veya müşteri ID'si geçersiz.")


# 3. Sahtekarlık ve Şüpheli Aktiviteler Sayfası
elif analysis_type == "Sahtekarlık ve Şüpheli Aktiviteler":
    st.header("Sahtekarlık ve Şüpheli Aktivite Tespiti")
    st.warning("Bu sorgular büyük veri setlerinde yavaş çalışabilir.", icon="⚠️")

    st.subheader("Döngüsel Transferler (Kara Para Aklama Şüphesi)")
    st.markdown("`A -> B -> C -> A` şeklinde 3'lü para transferi döngülerini gösterir.")

    query_circular = """
    MATCH path = (c1:Customer)-[:SENT]->(c2:Customer)-[:SENT]->(c3:Customer)-[:SENT]->(c1)
    WHERE c1 <> c2 AND c2 <> c3 AND c1 <> c3
    RETURN c1.customer_id AS Musteri_A, c2.customer_id AS Musteri_B, c3.customer_id AS Musteri_C
    LIMIT 20
    """
    circular_df = run_query(neo4j_conn, query_circular)

    if not circular_df.empty:
        st.dataframe(circular_df, use_container_width=True)
    else:
        st.info("Sistemde 3'lü döngüsel transfer bulunamadı.")