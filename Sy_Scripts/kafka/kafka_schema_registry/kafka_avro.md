# 📦 Kafka + Schema Registry + Avro Serialization 실습

Kafka 메시지를 **Avro 직렬화**하여 전송하고,  
**Schema Registry**를 통해 스키마를 중앙 관리하는 실습 정리입니다.

---
<br>

## 📌 구성 개요
- Kafka Cluster (3 brokers)
- Schema Registry (Confluent)
- Python Producer
- Avro 직렬화
- Selenium 크롤링 데이터 전송
---
<br>


## 🔗 버전 호환성 확인
- Schema Registry ↔ Kafka 버전 호환성은 아래 문서를 기준으로 확인 👉 https://docs.confluent.io/platform/current/installation/versions-interoperability.html
---
<br>

## 1️⃣ 사전 준비
### Kafka + Zookeeper 기동
- 자체 개발 스크립트 입니다.. ( zookeeper + kafka 기동 )
```bash
# Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Kafka
bin/kafka-server-start.sh config/server.properties
```
---
<br>

## 2️⃣ Schema Registry 실행 (Docker)
```bash
docker run -d \
  --name schema-registry \
  -p 8081:8081 \
  -e SCHEMA_REGISTRY_HOST_NAME=schema-registry \
  -e SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=PLAINTEXT://192.168.56.60:9092,PLAINTEXT://192.168.56.61:9092,PLAINTEXT://192.168.56.62:9092 \
  -e SCHEMA_REGISTRY_KAFKASTORE_TOPIC_REPLICATION_FACTOR=3 \
  confluentinc/cp-schema-registry:7.6.0

## 정상 기동 확인
curl http://localhost:8081/subjects
[]
⚠️ 처음에는 등록된 스키마가 없으므로 빈 배열이 정상
```
---
<br>

## 3️⃣ Kafka 에서 Avro 직렬화 동작 흐름
- 프로듀서가 메시지를 보내려고 하면, 먼저 **사용할 Avro 스키마가** Schema Registry에 있는지 확인합니다.
- 이미 등록된 스키마라면 **registry에서 schema_id 조회** → 메시지에 schema_id 붙임 → 전송
- 등록되지 않은 새로운 스키마면 **Schema Registry에 등록** → schema_id 반환 → 메시지에 붙임 → 전송

```graphql
Producer
 ├─ 로컬 Avro 스키마(.avsc) 로드
 ├─ 메시지 전송 시
 │   ├─ Schema Registry에 스키마 존재 여부 확인
 │   ├─ 없으면 자동 등록
 │   └─ schema_id 발급
 └─ schema_id + payload를 Kafka로 전송
```
#### 🔑 포인트 : 매번 등록하는 게 아니라 매번 체크를 하는 것. 대부분 라이브러리(예: Confluent Kafka Avro Producer)는 로컬 캐시를 써서 이미 등록된 스키마는 registry 호출 없이 바로 schema_id 사용 가능
```bash
1. 메시지를 보내려는 프로듀서가 스키마를 확인
2. 먼저 로컬 캐시에서 이 스키마가 등록되어 있는지 확인
    if 등록되어 있으면 → registry 호출 없이 schema_id 사용
    else 없으면 → Schema Registry에 조회/등록 → schema_id를 받고 로컬 캐시에 저장
3. 다음 메시지부터는 캐시에 있는 schema_id를 바로 사용
```
---
<br>

## 4️⃣ Avro 스키마 정의
- job_header.avsc
```json
{
  "type": "record",
  "name": "JobHeader",
  "namespace": "job.crawler",
  "fields": [
    { "name": "domain", "type": "string" },
    { "name": "href", "type": "string" },
    { "name": "company", "type": "string" },
    { "name": "title", "type": "string" }
  ]
}
```
---
<br>

## 5️⃣ KafkaHook 클래스 구현
- 일반 Kafka / Avro Kafka 분리 설계
```python
from confluent_kafka import Producer
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro


class KafkaHook:
    """
    Kafka 연결/해제 및 Producer 제공
    """
    def __init__(self, brokers):
        self.brokers = brokers
        self.conn = None

    # 일반 Kafka Producer
    def connect(self, **configs):
        conf = {
            "bootstrap.servers": self.brokers,
            **configs
        }
        self.conn = Producer(conf)

    # Avro Kafka Producer
    def avro_connect(self, schema_registry_url, schema_path, **configs):
        value_schema = avro.load(schema_path)

        conf = {
            "bootstrap.servers": self.brokers,
            "schema.registry.url": schema_registry_url,
            **configs
        }

        self.conn = AvroProducer(
            conf,
            default_value_schema=value_schema
        )

    def __getattr__(self, name):
        return getattr(self.conn, name)
```
---
<br>

## 6️⃣ Producer 핵심 코드 요약
```python
kafka = KafkaHook(
    brokers="192.168.56.60:9092,192.168.56.61:9092,192.168.56.62:9092"
)

kafka.avro_connect(
    schema_registry_url="http://192.168.56.60:8081",
    schema_path="/work/test/schemas/job_header.avsc"
)

kafka.produce(
    topic="job_header_topic",
    value=job_header
)

kafka.flush()
```
---
<br>

## 7️⃣ Schema Registry 확인
- 등록된 Subject 목록
```bash
curl http://192.168.56.60:8081/subjects
```
- 특정 Topic 스키마 확인
```bash
curl http://192.168.56.60:8081/subjects/job_header_topic-value/versions/latest
```
- 스키마 삭제
```bash
# value 스키마
curl -XDELETE http://localhost:8081/subjects/job_header_topic-value?permanent=true

# key 스키마
curl -XDELETE http://localhost:8081/subjects/job_header_topic-key?permanent=true
```
---
<br>

## 8️⃣ Avro Consumer로 데이터 확인
```bash
docker exec -it schema-registry kafka-avro-console-consumer \
  --bootstrap-server 192.168.56.60:9092 \
  --topic job_header_topic \
  --from-beginning \
  --property schema.registry.url=http://localhost:8081
```
```json
{"domain":"Remember","href":"https://career.rememberapp.co.kr/job/posting/289554","company":"AK아이에스(주)","title":"[애경그룹] AK아이에스 PL/개발"}
{"domain":"Remember","href":"https://career.rememberapp.co.kr/job/posting/289451","company":"한화솔루션(주)","title":"[한화큐셀] BMS 하드웨어 엔지니어"}
{"domain":"Remember","href":"https://career.rememberapp.co.kr/job/posting/289453","company":"한화솔루션(주)","title":"[한화큐셀] BMS 소프트웨어 엔지니어"}
```
---
<br>

## 9️⃣ 일반 Kafka Consumer에서 확인
```bash
kafka-console-consumer.sh \
  --bootstrap-server 192.168.56.60:9092 \
  --topic job_header_topic \
  --from-beginning
```
```json
Rememberfhttps://career.rememberapp.co.kr/job/posting/248686"(주)베스펙스&Front-end Developer
Rememberfhttps://career.rememberapp.co.kr/job/posting/289183(주)이노션L[플랫폼] 커머스 플랫폼 기획
Rememberfhttps://career.rememberapp.co.kr/job/posting/281782@넥스큐브코퍼레이션(주)React 개발자
```
---
<br>

## 🔑 핵심 정리
- Schema Registry는 실행만 해두면 됨
- 스키마 등록은 Producer가 자동 처리
- Avro 메시지는 schema_id + payload 형태로 전송
- Consumer는 schema_id를 통해 자동 역직렬화
---
