#!/usr/bin/python3
import json, time
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer

# ===============================
# 설정
# ===============================
KAFKA_BROKERS = "192.168.122.60:9092,192.168.122.61:9092,192.168.122.62:9092"
SCHEMA_REGISTRY = "http://192.168.122.59:8081"

# 전송 모드 선택: "avro" or "json"
MODE = "avro"   #

# 토픽
TOPIC = "job_sc_test" if MODE == "avro" else "job_text_test"
GROUP_ID = f"job-consumer-test-{MODE}"

# ===============================
# Consumer 초기화
# ===============================
if MODE == "avro":
    consumer_config = {
        "bootstrap.servers": KAFKA_BROKERS,
        "schema.registry.url": SCHEMA_REGISTRY,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "enable.auto.offset.store": False
    }
    consumer = AvroConsumer(consumer_config)
else:
    consumer_config = {
        "bootstrap.servers": KAFKA_BROKERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "enable.auto.offset.store": False
    }
    consumer = Consumer(consumer_config)

consumer.subscribe([TOPIC])
print(f"{MODE.upper()} Consumer started | topic={TOPIC}")

# ===============================
# Consume 루프 (성능 테스트)
# ===============================
BATCH_LOG = 1000
count = 0
start = time.time()

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(msg.error())
            continue

        if MODE == "avro":
            _ = msg.value()
        else:
            _ = json.loads(msg.value().decode("utf-8"))

        count += 1

        if count % BATCH_LOG == 0:
            elapsed = time.time() - start
            print(f"{count} messages consumed | {elapsed:.2f}s")
finally:
    consumer.close()
