# 🔍 Kafka Avro vs JSON 성능 테스트
## 🔗 **테스트 환경**
- **Kafka 브로커** : 192.168.122.60, 61, 62
- **Producer 테스트 서버** : 192.168.122.63
- **Consumer 테스트 서버** : 192.168.122.64
- **Schema Registry** : 192.168.122.59 (Docker)
- **테스트 토픽** :
  - Avro : `job_sc_test` (Partition 3, Replication 3)
  - JSON : `job_text_test` (Partition 3, Replication 3)
- **삽입 데이터** : 30,000 건
- **모니터링 도구** : Node Exporter + Prometheus + Grafana
- **측정 기준** : Grafana max 값 기준 기록
---
<br>

## 📌 테스트 목적
- Kafka 메시지 전송 시 **Avro 직렬화와 JSON 원본 메시지 성능 차이** 확인
- **디스크 I/O, 네트워크 사용량, CPU 사용률, 토픽 용량** 비교
---
<br><br>

# 🛑 문제 (Problem)
- **JSON** : 메시지 용량 크고 브로커 I/O 부담 증가 가능
- **Avro** : 메시지 압축 및 schema_id 전송으로 디스크·네트워크 효율 향상
- 테스트로 **프로듀서/컨슈머 부하, 네트워크 트래픽, 토픽 저장 용량** 차이 확인
---
<br>

## ⚙ 테스트 환경 및 Grafana 모니터링
### 🔹 간단 쿼리 & 설명
| 지표 | 간단 쿼리 | 설명 |
|------|------------|------|
| **Disk Write Throughput** | `rate(node_disk_written_bytes_total[1m])` | 브로커 디스크 쓰기량 |
| **Network I/O (Producer OUT)** | `rate(node_network_transmit_bytes_total[1m])` | 프로듀서 → 브로커 전송량 |
| **Network I/O (Broker IN)** | `rate(node_network_receive_bytes_total[1m])` | 브로커 수신량 |
| **Network RX (Consumer)** | `rate(node_network_receive_bytes_total[1m])` | 컨슈머 수신 트래픽 |
| **CPU 사용률** | `rate(node_cpu_seconds_total[1m])` | CPU 사용률 |
---

<br>

## ⚙ 테스트 방법 (Solution)
### 1️⃣ JSON 원본 메시지
- Producer : `confluent_kafka.Producer`
- Consumer : `confluent_kafka.Consumer`
- 토픽 : `job_text_test`
```python
producer.produce(topic="job_text_test", value=json.dumps(job_data).encode('utf-8'))
producer.flush()
```
---
### 2️⃣ Avro 직렬화 메시지
- Producer : `confluent_kafka.avro.AvroProducer`
- Consumer : `confluent_kafka.avro.AvroConsumer`
- 토픽 : `job_sc_test`
```python
producer.produce(topic="job_sc_test", value=job_data)
producer.flush()
```
---
<br><br>

# 📊 결과 (Result)
| 지표                   | JSON 원본 | Avro 직렬화 | 설명 |
|-----------------------|-----------|------------|------|
| **Disk Write Throughput (Broker)** | 58,409~62,177 B/s | 46,940~55,460 B/s | Avro 메시지 압축으로 디스크 I/O 감소 |
| **Network I/O (Producer OUT)** | 34,182 B/s | 25,269 B/s | Avro 직렬화로 전송 데이터 감소 |
| **Network I/O (Broker IN)** | 34,747~34,909 B/s | 25,188~26,188 B/s | 브로커 수신 트래픽 감소 |
| **Network RX (Consumer)** | 97,689 B/s | 70,802 B/s | Avro 수신 데이터 감소 |
| **CPU 사용률 (Producer)** | 0.00104~0.00139 | 0.000905~0.00156 | 직렬화 처리로 약간 CPU 증가 |
| **CPU 사용률 (Consumer)** | 0.000404 | 0.000731 | Avro 역직렬화 처리로 CPU 약간 증가 |
| **토픽 디스크 용량** | 14.51 MB | 10.46 MB | Avro 압축으로 약 28% 용량 절감 |

---

#### 💡 요약
- **Avro 직렬화** → 디스크/네트워크 효율 향상, 토픽 용량 감소
- CPU 사용률 약간 증가, 전체 I/O 부담 감소
- Network RX도 약 28% 감소

---

## ⚡ Avro 장점
- 메시지 압축 → 디스크/네트워크 효율 향상
- schema_id 기반 전송 → 안정적 역직렬화
- 중복 schema 호출 최소화 → 효율적 처리

## ⚡ Avro 단점
- 직렬화/역직렬화 과정 CPU 부담
- 초기 schema 정의 필요

---
<br><br>

# 🏆 성과 요약
| 지표                   | JSON 원본 | Avro 직렬화 | 개선 비율 / 효율 |
|-----------------------|-----------|------------|----------------|
| **Disk Write Throughput** | 58,409~62,177 B/s | 46,940~55,460 B/s | 약 10~25% 감소 |
| **Network I/O (Producer OUT)** | 34,182 B/s | 25,269 B/s | 약 26% 감소 |
| **Network I/O (Broker IN)** | 34,747~34,909 B/s | 25,188~26,188 B/s | 약 25~28% 감소 |
| **Network RX (Consumer)** | 97,689 B/s | 70,802 B/s | 약 28% 감소 |
| **CPU 사용률 (Producer)** | 0.00104~0.00139 | 0.000905~0.00156 | 약간 상승 |
| **CPU 사용률 (Consumer)** | 0.000404 | 0.000731 | 약간 상승 |
| **토픽 디스크 용량** | 14.51 MB | 10.46 MB | 약 28% 감소 |

---
<br>

## 📌 결론
- **대규모 Kafka 메시지 전송** → Avro 직렬화 권장
- 디스크 I/O, 네트워크, 토픽 용량 효율 최적화
- CPU 부담은 약간 증가하지만 전체 효율 우위

---
<br>

## ✅ 최종 선택
- **Avro 직렬화 → 디스크/네트워크 효율 극대화 + 토픽 용량 절감**
