# Veri Bilimi Öğrenme Çalışması: Kafka ve Neo4j ile Para Transferi Akışı

Bu proje, sahte müşteri ve para transferi verileri üreten, bu verileri Apache Kafka üzerinden gerçek zamanlı olarak akıtan, Neo4j graf veritabanında depolayan ve Streamlit üzerinde görselleştiren bir veri mühendisliği ve analizi vaka çalışmasıdır.

## Projenin Amacı

Bu projenin temel amacı, modern veri mühendisliği araçlarını kullanarak uçtan uca bir veri hattı (pipeline) oluşturmaktır. Proje aşağıdaki adımları içerir:

1.  **Veri Üretimi:** `Faker` kütüphanesi kullanılarak farklı ülkelerden gerçekçi müşteri profilleri ve bu müşteriler arasında para transferi kayıtları oluşturulur.
2.  **Veri Akışı:** Oluşturulan transfer verileri, bir Kafka `producer` aracılığıyla `money_transfers` adlı bir topic'e gönderilir.
3.  **Veri Tüketimi ve Depolama:** Bir Kafka `consumer`, bu topic'i dinler, 'tamamlanmış' (`completed`) statüsündeki transferleri alır ve bu bilgiyi Neo4j veritabanına bir graf olarak yazar.
4.  **Sahtekarlık Tespiti:** `consumer` aynı zamanda veri akışı üzerinden gerçek zamanlı olarak basit sahtekarlık kurallarını (yüksek meblağ, sık işlem vb.) çalıştırır.
5.  **Veri Analizi ve Görselleştirme:** Proje, `Streamlit` ile oluşturulmuş bir web panosu içerir. Bu pano, Neo4j'deki verileri sorgulayarak genel bakış, müşteri detayları ve şüpheli aktiviteler hakkında interaktif analizler sunar.

## Teknolojiler

- **Python**: Ana programlama dili.
- **Apache Kafka**: Gerçek zamanlı veri akışı platformu.
- **Neo4j**: Graf veritabanı.
- **Streamlit**: Veri analizi ve görselleştirme panosu için.
- **Docker & Docker Compose**: Altyapıyı (Kafka, Zookeeper, Neo4j) kolayca kurmak ve yönetmek için.
- **Python Kütüphaneleri**:
  - `kafka-python`: Kafka ile etkileşim için.
  - `neo4j`: Neo4j veritabanı ile etkileşim için.
  - `Faker`: Sahte veri üretimi için.
  - `pandas`: Veri manipülasyonu için.

## Kurulum

Projeyi yerelde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Altyapıyı halletmek

Proje, Kafka ve Neo4j servisleri için Docker kullanıyor.

```bash
# Proje kök dizininde aşağıdaki komutu çalıştırın
docker-compose up -d
```

Bu komut arka planda Zookeeper, Kafka ve Neo4j'i başlatacak.

- **Neo4j Arayüzü**: `http://localhost:7474`
- **Kullanıcı Adı**: `neo4j`
- **Şifre**: `password123`

### 2. Python Kütüphanelerini Yükleme

Gerekli Python kütüphanelerini yüklemek için:

```bash
pip install -r requirements.txt
```

## Kullanım

Kurulum tamamlandıktan sonra, veri hattını çalıştırmak için aşağıdaki betikleri sırasıyla çalıştırın.

### Adım 1: Veri Üretme

Müşteri ve transfer verilerini oluşturmak için `generate_data.py` betiğini çalıştırın. Bu betik, `customers.json` ve `transfers.json` dosyalarını oluşturacaktır.

```bash
python generate_data.py
```

### Adım 2: Müşterileri Neo4j'e Yükleme

Oluşturulan müşteri verilerini toplu olarak Neo4j veritabanına yüklemek için `load_consumer.py` betiğini çalıştırın. Bu, transferler işlenmeden önce tüm müşteri düğümlerinin veritabanında var olmasını sağlar.

```bash
python load_consumer.py
```

### Adım 3: Veriyi Kafka'ya Gönderme (Producer)

`transfers.json` dosyasındaki verileri Kafka'ya göndermek için `producer.py` betiğini çalıştırın.

```bash
python producer.py
```

### Adım 4: Veriyi Okuma ve Neo4j'e Yazma (Consumer)

Kafka'daki verileri dinlemek, Neo4j'e yazmak ve aynı zamanda sahtekarlık kontrolü yapmak için `consumer.py` betiğini çalıştırın. Bu betik, `producer` çalışırken veya çalıştıktan sonra başlatılabilir.

```bash
python consumer.py
```

### Adım 5: Analiz Panosunu Başlatma

Verileri görselleştirmek ve analiz etmek için Streamlit panosunu başlatın.

```bash
streamlit run dashboard.py
```

Tarayıcınızda açılan sayfada analizleri inceleyebilirsiniz.

## Proje Yapısı ve Dosyalar

- `docker-compose.yml`: Kafka, Zookeeper ve Neo4j servislerini tanımlar.
- `generate_data.py`: Sahte müşteri ve transfer verileri oluşturur.
- `producer.py`: `transfers.json` dosyasını okur ve verileri Kafka'ya gönderir.
- `consumer.py`: Kafka'dan verileri okur, Neo4j'e yazar ve sahtekarlık kontrolü yapar.
- `load_consumer.py`: `customers.json` dosyasındaki müşterileri Neo4j'e toplu olarak yükler.
- `dashboard.py`: Streamlit ile oluşturulmuş interaktif analiz panosu.
- `neo4j_inserts.py`: Neo4j veritabanı bağlantısını ve veri ekleme mantığını içerir.
- `requirements.txt`: Gerekli Python kütüphanelerini listeler.
- `cypher_queries.txt`: Analiz için kullanılabilecek örnek Cypher sorgularını içerir.

## Neo4j Veri Modeli

Bu projede kullanılan graf modeli oldukça basittir:

- **Düğümler (Nodes)**:
  - `(:Customer {customer_id: '...'}`: Her bir müşteri bir `Customer` düğümü ile temsil edilir.
- **İlişkiler (Relationships)**:
  - `(gönderen)-[:SENT]->(alıcı)`: İki `Customer` düğümü arasındaki bir para transferini temsil eder. `SENT` ilişkisi, `transfer_id`, `amount` ve `timestamp` gibi özellikler içerir.

Neo4j tarayıcısında aşağıdaki Cypher sorgusunu kullanarak grafı görselleştirebilirsiniz:

```cypher
MATCH (c1:Customer)-[r:SENT]->(c2:Customer) RETURN c1, r, c2 LIMIT 25
```
