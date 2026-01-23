#!/usr/bin/python3
import json, random, time
from faker import Faker
from confluent_kafka import Producer
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

fake = Faker()

# ===============================
# 설정
# ===============================
KAFKA_BROKER = "localhost:9092"
SCHEMA_REGISTRY = "http://localhost:8081"
TOPIC = "job_topic_test"

# 전송 모드 선택: "avro" or "json"
MODE = "avro"  # <-- 여기 바꾸면 됩니다.

# ===============================
# Avro 스키마 정의
# ===============================
job_data_schema = {
    "namespace": "job.avro",
    "name": "JobData",
    "type": "record",
    "fields": [
        {"name": "domain", "type": "string"},
        {"name": "href", "type": "string"},
        {"name": "company", "type": "string"},
        {"name": "title", "type": "string"}
    ]
}

# ===============================
# Producer 초기화
# ===============================
if MODE == "avro":
    producer_config = {
        'bootstrap.servers': KAFKA_BROKER,
        'schema.registry.url': SCHEMA_REGISTRY,
        'linger.ms': 20  # 10초 대기 후 배치 전송
    }
    producer = AvroProducer(
        producer_config,
        default_value_schema=avro.loads(json.dumps(job_data_schema))
    )
else:  # json/plain
    producer_config = {
        'bootstrap.servers': KAFKA_BROKER,
        'linger.ms': 10000
    }
    producer = Producer(producer_config)

# ===============================
# 샘플 데이터 생성 함수
# ===============================
domains = ["remember", "saramin", "wanted", "incruit"]

def generate_job_data():
    return {
        "domain": random.choice(domains),
        "href": f"https://job.fake/{fake.uuid4()}",
        "company": fake.company(),
        "title": fake.job()
    }

# ===============================
# 메시지 전송 루프
# ===============================
BATCH_SIZE = 1000  # 로그용 배치 처리 단위
for i in range(10000):
    job_data = generate_job_data()

    if MODE == "avro":
        producer.produce(topic=TOPIC, value=job_data)
    else:
        producer.produce(topic=TOPIC, value=json.dumps(job_data).encode('utf-8'))

    # 중간 진행 로그
    if (i+1) % BATCH_SIZE == 0:
        print(f"{i+1}건 전송 완료")

# Flush
producer.flush()
print(f"{MODE.upper()} 전송 완료")
